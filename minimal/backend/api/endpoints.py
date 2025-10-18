"""
API endpoint handlers for the Aqumen question generation service.

This module contains all the route handlers for the FastAPI application.
Handlers are kept thin and delegate business logic to services and the pipeline.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, Query
from fastapi.responses import StreamingResponse

from api.main import MOCK_PIPELINE, app, get_pipeline
from api.models import GenerateRequest, HealthResponse, QuestionResponse
from api.streaming import format_sse_message, run_pipeline_streaming
from config.prompts_loader import load_prompts

logger = logging.getLogger(__name__)


@app.get("/", response_model=HealthResponse)
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns service status and pipeline readiness.
    """
    from api.main import pipelines

    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        pipeline_ready=(len(pipelines) > 0 and not MOCK_PIPELINE),
        version="1.0.0",
    )


@app.get("/api/models")
async def get_models():
    """
    Get information about the models used in the pipeline.

    Returns model IDs and descriptions for all three tiers.
    """
    if MOCK_PIPELINE:
        logger.debug("Mock mode: returning placeholder model metadata.")
        return {
            "models": {
                "strong": {
                    "id": "mock-strong-model",
                    "description": "Static strong reviewer model (mock mode)",
                    "purpose": "Strategic reasoning, quality assessment",
                },
                "mid": {
                    "id": "mock-mid-model",
                    "description": "Static mid reviewer model (mock mode)",
                    "purpose": "Baseline implementation",
                },
                "weak": {
                    "id": "mock-weak-model",
                    "description": "Static weak reviewer model (mock mode)",
                    "purpose": "Simulated weak performance",
                },
            },
            "pipeline_flow": "Mock mode – pipeline execution disabled.",
        }

    try:
        p = get_pipeline()
        return {
            "models": {
                "strong": {
                    "id": p.model_strong,
                    "description": (
                        "Claude Opus 4.1 - Used for strategic question generation (Step 3), "
                        "judging (Step 6), and assessment creation (Step 7)"
                    ),
                    "purpose": "Strategic reasoning, quality assessment, complex reasoning",
                },
                "mid": {
                    "id": p.model_mid,
                    "description": (
                        "Claude Sonnet 4.5 - Used for difficulty categories (Step 1), "
                        "error catalog (Step 2), and mid-tier implementation (Step 4)"
                    ),
                    "purpose": "Competent implementation baseline, category generation",
                },
                "weak": {
                    "id": p.model_weak,
                    "description": (
                        "Claude Haiku 4.5 - Used for weak-tier implementation (Step 5) to generate conceptual errors"
                    ),
                    "purpose": "Generate realistic errors for assessment creation",
                },
            },
            "pipeline_flow": (
                "Steps 1-2: Mid (Sonnet 4.5) → Step 3: Strong (Opus 4.1) → "
                "Step 4: Mid → Step 5: Weak (Haiku 4.5) → Steps 6-7: Strong"
            ),
        }
    except Exception as e:
        logger.exception("Failed to get model info")
        raise HTTPException(500, f"Error retrieving model info: {str(e)}")


@app.get("/api/generate-stream")
async def generate_stream(
    topic: str = Query(..., description="AI/ML topic for question generation", min_length=3),
    max_retries: int = Query(3, description="Max retries for hard question", ge=1, le=5),
    provider: str = Query("anthropic", description="Model provider: 'anthropic' or 'openai'"),
):
    """
    Stream the 7-step pipeline execution in real-time using Server-Sent Events (SSE).

    This endpoint allows clients to see each step complete as it happens,
    enabling real-time debugging and progress tracking.

    Each event contains:
    - step_number: Which step (1-7)
    - description: What this step does
    - response: The LLM's response
    - success: Whether the step succeeded
    - timestamp: When the step completed
    - metadata: Additional info (model used, duration, etc.)

    The stream ends with a "done" event containing the final result.
    """
    logger.info(f"Stream request received for topic: {topic}")

    async def event_generator():
        try:
            p = get_pipeline(provider)
            start_time = datetime.now()

            # Send initial event
            yield format_sse_message(
                {"event": "start", "topic": topic, "timestamp": start_time.isoformat()}, event_type="start"
            )

            # Run streaming pipeline
            async for step_data in run_pipeline_streaming(p, topic, max_retries):
                yield format_sse_message(step_data, event_type="step")

            # Send completion event
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            yield format_sse_message(
                {"event": "done", "timestamp": end_time.isoformat(), "total_duration_seconds": duration},
                event_type="done",
            )

        except Exception as e:
            logger.exception("Error during streaming")
            yield format_sse_message(
                {"event": "error", "error": str(e), "timestamp": datetime.now().isoformat()}, event_type="error"
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@app.post("/api/generate", response_model=QuestionResponse)
async def generate_question(
    request: GenerateRequest, provider: str = Query("anthropic", description="Model provider: 'anthropic' or 'openai'")
):
    """
    Generate a complete question (blocking).

    This endpoint runs the full 7-step pipeline and returns only the final result.
    Use /api/generate-stream for real-time progress updates.

    Returns a validated question ready for the frontend.
    """
    logger.info(f"Generate request received for topic: {request.topic} with provider: {provider}")

    try:
        start_time = datetime.now()
        p = get_pipeline(provider)

        # Run full pipeline (blocking)
        pipeline_result = p.run_full_pipeline(topic=request.topic, max_attempts=request.max_retries)

        if not pipeline_result.final_success:
            # Extract error details
            failed_steps = [s for s in pipeline_result.steps_completed if not s.success]
            error_detail = (
                f"Pipeline failed at step {failed_steps[-1].step_number}" if failed_steps else "Unknown error"
            )
            logger.error(f"Pipeline failed: {error_detail}")
            raise HTTPException(status_code=500, detail=f"Question generation failed: {error_detail}")

        # Extract the assessment from Step 7 response
        step7 = [s for s in pipeline_result.steps_completed if s.step_number == 7]
        if not step7:
            logger.error("Step 7 not found in completed steps")
            raise HTTPException(status_code=500, detail="Assessment creation step not found")

        # Parse the assessment JSON from Step 7
        try:
            assessment = json.loads(step7[0].response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Step 7 assessment: {e}")
            raise HTTPException(status_code=500, detail="Failed to parse generated assessment")

        # Validate assessment structure
        if not isinstance(assessment, dict) or "title" not in assessment:
            logger.error(f"Invalid assessment format: {assessment}")
            raise HTTPException(status_code=500, detail="Generated assessment has invalid format")

        # Add metadata
        generation_time = (datetime.now() - start_time).total_seconds()
        assessment["metadata"] = {
            "generated_at": datetime.now().isoformat(),
            "generation_time_seconds": round(generation_time, 2),
            "topic_requested": request.topic,
            "pipeline_steps": len(pipeline_result.steps_completed),
            "successful_steps": sum(1 for s in pipeline_result.steps_completed if s.success),
            "total_attempts": pipeline_result.total_attempts,
            "differentiation_achieved": pipeline_result.differentiation_achieved,
        }

        logger.info(f"Question generated successfully in {generation_time:.2f}s")
        return QuestionResponse(**assessment)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error during question generation")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/update-prompt")
async def update_prompt(request: dict):
    """
    Update a prompt override stored in prompts_changes.json.

    Request body:
    {
        "step": "step1_difficulty_categories" | ... | "step7_student_assessment",
        "new_prompt": "The new prompt template string"
    }
    """
    step = request.get("step")
    new_prompt = request.get("new_prompt")

    if not step or not new_prompt:
        raise HTTPException(status_code=400, detail="Missing required fields: 'step' and 'new_prompt'")

    valid_steps = [
        "step1_difficulty_categories",
        "step2_error_catalog",
        "step3_strategic_question",
        "step4_test_sonnet",
        "step5_test_haiku",
        "step6_judge_responses",
        "step7_student_assessment",
    ]

    if step not in valid_steps:
        raise HTTPException(status_code=400, detail=f"Invalid step. Must be one of: {', '.join(valid_steps)}")

    try:
        prompts = load_prompts()
        if step not in prompts:
            raise HTTPException(status_code=404, detail=f"Step '{step}' not found in prompt configuration")

        # Get the backend directory
        backend_dir = Path(__file__).resolve().parent.parent
        changes_path = backend_dir / "prompts_changes.json"
        now_iso = datetime.now().isoformat()

        # Load existing changes
        try:
            if changes_path.exists():
                with changes_path.open("r", encoding="utf-8") as fh:
                    prompt_changes = json.load(fh)
                    if not isinstance(prompt_changes, dict):
                        prompt_changes = {}
            else:
                prompt_changes = {}
        except json.JSONDecodeError as exc:
            logger.exception("Invalid JSON in prompts_changes.json")
            raise HTTPException(status_code=500, detail=f"Invalid JSON in prompts_changes.json: {exc}") from exc

        # Update metadata
        meta = prompt_changes.get("_meta")
        if not isinstance(meta, dict):
            meta = {"description": "UI-managed prompt overrides merged on top of prompts.json."}
        meta["last_updated"] = now_iso
        prompt_changes["_meta"] = meta

        # Update the specific step
        override_entry = prompt_changes.get(step)
        if not isinstance(override_entry, dict):
            override_entry = {}

        override_entry.update({"template": new_prompt, "last_updated": now_iso, "updated_by": "api"})
        prompt_changes[step] = override_entry

        # Write back to file
        with changes_path.open("w", encoding="utf-8") as fh:
            json.dump(prompt_changes, fh, indent=2)

        # Reload merged prompts
        merged_prompts = load_prompts()
        updated_prompt = merged_prompts.get(step, {})

        logger.info(f"Prompt override saved for step: {step}")

        return {
            "success": True,
            "step": step,
            "updated_prompt": updated_prompt,
            "message": "Prompt override saved to prompts_changes.json. Reload the pipeline to pick up changes.",
        }

    except HTTPException:
        raise
    except FileNotFoundError as exc:
        logger.exception("Prompt configuration missing")
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Error updating prompt")
        raise HTTPException(status_code=500, detail=f"Failed to update prompt: {exc}") from exc


@app.get("/api/get-prompts")
async def get_prompts():
    """
    Get the merged prompt configuration (base + overrides).
    """
    try:
        prompts = load_prompts()
        logger.info("Prompts retrieved successfully")
        return {"success": True, "prompts": prompts}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Error retrieving prompts")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve prompts: {exc}") from exc


@app.post("/api/step1")
async def step1_categories(request: dict):
    """
    Generate Step 1 difficulty categories for a topic.

    This endpoint runs only Step 1 of the pipeline to generate difficulty categories,
    which the frontend uses before running the full pipeline.

    Request body:
    {
        "topic": "AI/ML topic for categorization",
        "provider": "anthropic" | "openai" (optional, defaults to "anthropic")
    }
    """
    topic = request.get("topic")
    provider = request.get("provider", "anthropic")

    if not topic or len(topic.strip()) < 3:
        raise HTTPException(status_code=400, detail="Topic is required and must be at least 3 characters long")

    logger.info(f"Step 1 request received for topic: {topic} with provider: {provider}")

    try:
        p = get_pipeline(provider)

        # Run only Step 1
        success, categories, step1_result = p.step1_generate_difficulty_categories(topic.strip())

        if not success:
            logger.error(f"Step 1 failed for topic: {topic}")
            raise HTTPException(
                status_code=500,
                detail=f"Step 1 failed: {step1_result.response if step1_result.response else 'Unknown error'}",
            )

        logger.info(f"Step 1 completed successfully for topic: {topic}")

        # Return the categories and step info
        return {
            "success": True,
            "categories": categories,
            "step_info": {
                "step_number": step1_result.step_number,
                "step_name": step1_result.step_name,
                "model_used": step1_result.model_used,
                "success": step1_result.success,
                "timestamp": step1_result.timestamp,
                "response": step1_result.response,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error during Step 1")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/test-models")
async def test_models(request: dict | None = None):
    """
    Test all three models to verify they're accessible and responding.

    This endpoint quickly verifies the models are working by sending a simple prompt to each.

    Request body (optional):
    {
        "provider": "anthropic" | "openai" (optional, defaults to "anthropic")
    }
    """
    if request is None:
        request = {}
    provider = request.get("provider", "anthropic")
    logger.info(f"Testing all three models for provider: {provider}...")

    try:
        p = get_pipeline(provider)
        test_prompt = "Respond with: hello"

        # Test all three models
        results = {}

        # Test strong model
        try:
            strong_response = p.invoke_model(p.model_strong, test_prompt)
            results["strong"] = {"model_id": p.model_strong, "response": strong_response.strip(), "success": True}
        except Exception as e:
            results["strong"] = {"model_id": p.model_strong, "error": str(e), "success": False}

        # Test mid model
        try:
            mid_response = p.invoke_model(p.model_mid, test_prompt)
            results["mid"] = {"model_id": p.model_mid, "response": mid_response.strip(), "success": True}
        except Exception as e:
            results["mid"] = {"model_id": p.model_mid, "error": str(e), "success": False}

        # Test weak model
        try:
            weak_response = p.invoke_model(p.model_weak, test_prompt)
            results["weak"] = {"model_id": p.model_weak, "response": weak_response.strip(), "success": True}
        except Exception as e:
            results["weak"] = {"model_id": p.model_weak, "error": str(e), "success": False}

        logger.info(f"Model test results: {list(results.keys())}")

        return {"success": True, "models": results, "timestamp": datetime.now().isoformat()}

    except Exception as e:
        logger.exception("Error during model testing")
        raise HTTPException(status_code=500, detail=f"Model testing failed: {str(e)}")
