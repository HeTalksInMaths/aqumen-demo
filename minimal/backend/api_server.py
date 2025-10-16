"""
FastAPI server for dynamic adversarial question generation with SSE streaming.

This API provides real-time streaming of the 7-step pipeline execution,
allowing clients to see each step complete as it happens.

Endpoints:
- GET  /health                    Health check
- GET  /api/models                Get model information
- GET  /api/generate-stream       Stream pipeline execution (SSE)
- POST /api/generate              Generate question (blocking, returns final result)
"""

import json
import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, AsyncGenerator, Dict

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from corrected_7step_pipeline import CorrectedSevenStepPipeline
from config import load_prompts

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Toggle lightweight "mock" mode for local development/testing so we can satisfy
# frontend calls without initializing the full Bedrock-powered pipeline.
MOCK_PIPELINE = os.getenv("AQU_MOCK_PIPELINE", "0") == "1"
if MOCK_PIPELINE:
    logger.warning("AQU_MOCK_PIPELINE=1 detected – running API server in mock mode; "
                   "pipeline-dependent endpoints will return placeholders.")

# Initialize FastAPI app
app = FastAPI(
    title="Aqumen Question Generation API",
    description="Real-time adversarial AI/ML code review question generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration - allow frontend domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",           # Vite dev server
        "http://localhost:3000",           # Alternative dev port
        "http://localhost:8501",           # Streamlit local
        "https://demo.aqumen.ai",          # Production React frontend
        "https://dev.aqumen.ai",           # Dev Streamlit frontend
        "https://*.vercel.app",            # Vercel preview deployments
        "https://*.streamlit.app",         # Streamlit Cloud
        "https://*.onrender.com",          # Render preview
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class GenerateRequest(BaseModel):
    topic: str = Field(..., description="AI/ML topic for question generation", min_length=3, max_length=200)
    difficulty_preference: Optional[str] = Field(None, description="Preferred difficulty: Beginner, Intermediate, Advanced, Expert")
    max_retries: int = Field(3, description="Maximum retries if question isn't hard enough", ge=1, le=5)

class QuestionResponse(BaseModel):
    title: str
    difficulty: str
    code: list[str]
    errors: list[dict]
    metadata: dict

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    pipeline_ready: bool
    version: str

# Initialize pipeline (singleton pattern for efficiency, keyed by provider)
pipelines: Dict[str, CorrectedSevenStepPipeline] = {}

def get_pipeline(provider: str = "openai") -> CorrectedSevenStepPipeline:
    """
    Lazy initialization of pipeline singleton for specified provider.

    Args:
        provider: Either "anthropic" or "openai" (default: "openai")

    Returns:
        Pipeline instance for the specified provider
    """
    global pipelines
    if MOCK_PIPELINE:
        raise HTTPException(503, "Pipeline is disabled in mock mode.")

    # Validate provider
    if provider not in ["anthropic", "openai"]:
        raise HTTPException(400, f"Invalid provider: {provider}. Must be 'anthropic' or 'openai'")

    # Initialize pipeline for this provider if not already done
    if provider not in pipelines:
        logger.info(f"Initializing CorrectedSevenStepPipeline with provider: {provider}...")
        try:
            pipelines[provider] = CorrectedSevenStepPipeline(provider=provider)
            logger.info(f"Pipeline initialized successfully for provider: {provider}")
        except Exception as e:
            logger.error(f"Failed to initialize pipeline for provider '{provider}': {e}")
            raise HTTPException(500, f"Failed to initialize pipeline: {str(e)}")

    return pipelines[provider]

@app.on_event("startup")
async def startup_event():
    """Pre-initialize pipeline on server startup"""
    logger.info("Server starting up...")
    if MOCK_PIPELINE:
        logger.info("Mock mode enabled – skipping pipeline initialization.")
        return
    try:
        get_pipeline()
        logger.info("Server ready to accept requests")
    except Exception as e:
        logger.error(f"Startup failed: {e}")

@app.get("/", response_model=HealthResponse)
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns service status and pipeline readiness.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        pipeline_ready=(len(pipelines) > 0 and not MOCK_PIPELINE),
        version="1.0.0"
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
                    "purpose": "Strategic reasoning, quality assessment"
                },
                "mid": {
                    "id": "mock-mid-model",
                    "description": "Static mid reviewer model (mock mode)",
                    "purpose": "Baseline implementation"
                },
                "weak": {
                    "id": "mock-weak-model",
                    "description": "Static weak reviewer model (mock mode)",
                    "purpose": "Simulated weak performance"
                }
            },
            "pipeline_flow": "Mock mode – pipeline execution disabled."
        }
    try:
        p = get_pipeline()
        return {
            "models": {
                "strong": {
                    "id": p.model_strong,
                    "description": "Claude Opus 4.1 - Used for strategic question generation (Step 3), judging (Step 6), and assessment creation (Step 7)",
                    "purpose": "Strategic reasoning, quality assessment, complex reasoning"
                },
                "mid": {
                    "id": p.model_mid,
                    "description": "Claude Sonnet 4.5 - Used for difficulty categories (Step 1), error catalog (Step 2), and mid-tier implementation (Step 4)",
                    "purpose": "Competent implementation baseline, category generation"
                },
                "weak": {
                    "id": p.model_weak,
                    "description": "Claude Haiku 4.5 - Used for weak-tier implementation (Step 5) to generate conceptual errors",
                    "purpose": "Generate realistic errors for assessment creation"
                }
            },
            "pipeline_flow": "Steps 1-2: Mid (Sonnet 4.5) → Step 3: Strong (Opus 4.1) → Step 4: Mid → Step 5: Weak (Haiku 4.5) → Steps 6-7: Strong"
        }
    except Exception as e:
        logger.exception("Failed to get model info")
        raise HTTPException(500, f"Error retrieving model info: {str(e)}")

@app.get("/api/generate-stream")
async def generate_stream(
    topic: str = Query(..., description="AI/ML topic for question generation", min_length=3),
    max_retries: int = Query(3, description="Max retries for hard question", ge=1, le=5),
    provider: str = Query("openai", description="Model provider: 'anthropic' or 'openai'")
):
    """
    Stream the 7-step pipeline execution in real-time using Server-Sent Events (SSE).

    This endpoint allows clients to see each step complete as it happens,
    enabling real-time debugging and progress tracking.

    Each event contains:
    - step_number: Which step (1-7)
    - description: What this step does
    - prompt: The prompt sent to the LLM (for debugging)
    - response: The LLM's response
    - success: Whether the step succeeded
    - timestamp: When the step completed
    - metadata: Additional info (model used, duration, etc.)

    The stream ends with a "done" event containing the final result.
    """
    logger.info(f"Stream request received for topic: {topic}")

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            p = get_pipeline(provider)
            start_time = datetime.now()

            # Send initial event
            yield format_sse_message({
                "event": "start",
                "topic": topic,
                "timestamp": start_time.isoformat()
            }, event_type="start")

            # Run streaming pipeline
            async for step_data in run_pipeline_streaming(p, topic, max_retries):
                yield format_sse_message(step_data, event_type="step")

            # Send completion event
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            yield format_sse_message({
                "event": "done",
                "timestamp": end_time.isoformat(),
                "total_duration_seconds": duration
            }, event_type="done")

        except Exception as e:
            logger.exception("Error during streaming")
            yield format_sse_message({
                "event": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }, event_type="error")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )

@app.post("/api/generate", response_model=QuestionResponse)
async def generate_question(
    request: GenerateRequest,
    provider: str = Query("openai", description="Model provider: 'anthropic' or 'openai'")
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
        pipeline_result = p.run_full_pipeline(
            topic=request.topic,
            max_attempts=request.max_retries
        )

        if not pipeline_result.final_success:
            # Extract error details
            failed_steps = [s for s in pipeline_result.steps_completed if not s.success]
            error_detail = f"Pipeline failed at step {failed_steps[-1].step_number}" if failed_steps else "Unknown error"
            logger.error(f"Pipeline failed: {error_detail}")
            raise HTTPException(
                status_code=500,
                detail=f"Question generation failed: {error_detail}"
            )

        # Extract the assessment from Step 7 response
        step7 = [s for s in pipeline_result.steps_completed if s.step_number == 7]
        if not step7:
            logger.error("Step 7 not found in completed steps")
            raise HTTPException(
                status_code=500,
                detail="Assessment creation step not found"
            )

        # Parse the assessment JSON from Step 7
        import json as json_module
        try:
            assessment = json_module.loads(step7[0].response)
        except json_module.JSONDecodeError as e:
            logger.error(f"Failed to parse Step 7 assessment: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to parse generated assessment"
            )

        # Validate assessment structure
        if not isinstance(assessment, dict) or 'title' not in assessment:
            logger.error(f"Invalid assessment format: {assessment}")
            raise HTTPException(
                status_code=500,
                detail="Generated assessment has invalid format"
            )

        # Add metadata
        generation_time = (datetime.now() - start_time).total_seconds()
        assessment['metadata'] = {
            'generated_at': datetime.now().isoformat(),
            'generation_time_seconds': round(generation_time, 2),
            'topic_requested': request.topic,
            'pipeline_steps': len(pipeline_result.steps_completed),
            'successful_steps': sum(1 for s in pipeline_result.steps_completed if s.success),
            'total_attempts': pipeline_result.total_attempts,
            'differentiation_achieved': pipeline_result.differentiation_achieved
        }

        logger.info(f"Question generated successfully in {generation_time:.2f}s")
        return QuestionResponse(**assessment)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error during question generation")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/api/update-prompt")
async def update_prompt(request: dict):
    """
    Update a prompt override stored in prompts_changes.json.

    Request body:
    {
        "step": "step1_difficulty_categories" | "step2_error_catalog" | ... | "step7_student_assessment",
        "new_prompt": "The new prompt template string"
    }
    """
    import json as json_module

    step = request.get("step")
    new_prompt = request.get("new_prompt")

    if not step or not new_prompt:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields: 'step' and 'new_prompt'"
        )

    valid_steps = [
        "step1_difficulty_categories",
        "step2_error_catalog",
        "step3_strategic_question",
        "step4_test_sonnet",
        "step5_test_haiku",
        "step6_judge_responses",
        "step7_student_assessment"
    ]

    if step not in valid_steps:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid step. Must be one of: {', '.join(valid_steps)}"
        )

    try:
        prompts = load_prompts()
        if step not in prompts:
            raise HTTPException(
                status_code=404,
                detail=f"Step '{step}' not found in prompt configuration"
            )

        changes_path = Path(__file__).resolve().parent / "prompts_changes.json"
        now_iso = datetime.now().isoformat()

        try:
            if changes_path.exists():
                with changes_path.open("r", encoding="utf-8") as fh:
                    prompt_changes = json_module.load(fh)
                    if not isinstance(prompt_changes, dict):
                        prompt_changes = {}
            else:
                prompt_changes = {}
        except json_module.JSONDecodeError as exc:
            logger.exception("Invalid JSON in prompts_changes.json")
            raise HTTPException(
                status_code=500,
                detail=f"Invalid JSON in prompts_changes.json: {exc}"
            ) from exc

        meta = prompt_changes.get("_meta")
        if not isinstance(meta, dict):
            meta = {
                "description": "UI-managed prompt overrides merged on top of prompts.json."
            }
        meta["last_updated"] = now_iso
        prompt_changes["_meta"] = meta

        override_entry = prompt_changes.get(step)
        if not isinstance(override_entry, dict):
            override_entry = {}

        override_entry.update({
            "template": new_prompt,
            "last_updated": now_iso,
            "updated_by": "api"
        })
        prompt_changes[step] = override_entry

        with changes_path.open("w", encoding="utf-8") as fh:
            json_module.dump(prompt_changes, fh, indent=2)

        merged_prompts = load_prompts()
        updated_prompt = merged_prompts.get(step, {})

        logger.info(f"Prompt override saved for step: {step}")

        return {
            "success": True,
            "step": step,
            "updated_prompt": updated_prompt,
            "message": "Prompt override saved to prompts_changes.json. Reload the pipeline to pick up changes."
        }

    except HTTPException:
        raise
    except FileNotFoundError as exc:
        logger.exception("Prompt configuration missing")
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        ) from exc
    except Exception as exc:
        logger.exception("Error updating prompt")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update prompt: {exc}"
        ) from exc


@app.get("/api/get-prompts")
async def get_prompts():
    """
    Get the merged prompt configuration (base + overrides).
    """
    try:
        prompts = load_prompts()
        logger.info("Prompts retrieved successfully")
        return {
            "success": True,
            "prompts": prompts
        }
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        ) from exc
    except Exception as exc:
        logger.exception("Error retrieving prompts")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve prompts: {exc}"
        ) from exc

@app.post("/api/step1")
async def step1_categories(request: dict):
    """
    Generate Step 1 difficulty categories for a topic.

    This endpoint runs only Step 1 of the pipeline to generate difficulty categories,
    which the frontend uses before running the full pipeline.

    Request body:
    {
        "topic": "AI/ML topic for categorization",
        "provider": "anthropic" | "openai" (optional, defaults to "openai")
    }
    """
    topic = request.get("topic")
    provider = request.get("provider", "openai")

    if not topic or len(topic.strip()) < 3:
        raise HTTPException(
            status_code=400,
            detail="Topic is required and must be at least 3 characters long"
        )

    logger.info(f"Step 1 request received for topic: {topic} with provider: {provider}")

    try:
        p = get_pipeline(provider)

        # Run only Step 1
        success, categories, step1_result = p.step1_generate_difficulty_categories(topic.strip())

        if not success:
            logger.error(f"Step 1 failed for topic: {topic}")
            raise HTTPException(
                status_code=500,
                detail=f"Step 1 failed: {step1_result.response if step1_result.response else 'Unknown error'}"
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
                "response": step1_result.response
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error during Step 1")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/api/test-models")
async def test_models(request: dict = {}):
    """
    Test all three models to verify they're accessible and responding.

    This endpoint quickly verifies the models are working by sending a simple prompt to each.

    Request body (optional):
    {
        "provider": "anthropic" | "openai" (optional, defaults to "openai")
    }
    """
    provider = request.get("provider", "openai") if request else "openai"
    logger.info(f"Testing all three models for provider: {provider}...")

    try:
        p = get_pipeline(provider)
        test_prompt = "Respond with: hello"

        # Test all three models
        results = {}

        # Test strong model (Opus 4.1)
        try:
            strong_response = p.invoke_model(p.model_strong, test_prompt)
            results["strong"] = {
                "model_id": p.model_strong,
                "response": strong_response.strip(),
                "success": True
            }
        except Exception as e:
            results["strong"] = {
                "model_id": p.model_strong,
                "error": str(e),
                "success": False
            }

        # Test mid model (Sonnet 4.5)
        try:
            mid_response = p.invoke_model(p.model_mid, test_prompt)
            results["mid"] = {
                "model_id": p.model_mid,
                "response": mid_response.strip(),
                "success": True
            }
        except Exception as e:
            results["mid"] = {
                "model_id": p.model_mid,
                "error": str(e),
                "success": False
            }

        # Test weak model (Haiku 4.5)
        try:
            weak_response = p.invoke_model(p.model_weak, test_prompt)
            results["weak"] = {
                "model_id": p.model_weak,
                "response": weak_response.strip(),
                "success": True
            }
        except Exception as e:
            results["weak"] = {
                "model_id": p.model_weak,
                "error": str(e),
                "success": False
            }

        logger.info(f"Model test results: {list(results.keys())}")

        return {
            "success": True,
            "models": results,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.exception("Error during model testing")
        raise HTTPException(
            status_code=500,
            detail=f"Model testing failed: {str(e)}"
        )

# Helper functions for SSE

def format_sse_message(data: dict, event_type: str = "message") -> str:
    """
    Format a message for Server-Sent Events protocol.

    SSE format:
    event: <event_type>
    data: <json_data>

    """
    json_data = json.dumps(data)
    return f"event: {event_type}\ndata: {json_data}\n\n"

async def run_pipeline_streaming(
    pipeline: CorrectedSevenStepPipeline,
    topic: str,
    max_retries: int
) -> AsyncGenerator[dict, None]:
    """
    Run the pipeline and yield each step as it completes.

    This wraps the synchronous pipeline generator in an async wrapper
    to provide real-time streaming updates via SSE.
    """
    # Run the pipeline generator in a thread pool to avoid blocking
    loop = asyncio.get_event_loop()

    # Create iterator from the streaming pipeline
    def create_generator():
        """Create the synchronous generator"""
        return pipeline.run_full_pipeline_streaming(topic, max_attempts=max_retries)

    # Run in executor
    gen = await loop.run_in_executor(None, create_generator)

    # Iterate through the generator
    while True:
        try:
            # Get next item from generator (in thread pool)
            item = await loop.run_in_executor(None, lambda: next(gen, None))

            if item is None:
                # Generator exhausted
                break

            # Check if this is a final result or a step
            if isinstance(item, dict) and "final_result" in item:
                # This is the final result
                final_result = item["final_result"]
                assessment = item.get("assessment")

                yield {
                    "type": "final",
                    "success": final_result.final_success,
                    "differentiation_achieved": final_result.differentiation_achieved,
                    "total_attempts": final_result.total_attempts,
                    "stopped_at_step": final_result.stopped_at_step,
                    "assessment": assessment,
                    "metadata": {
                        "topic": final_result.topic,
                        "subtopic": final_result.subtopic,
                        "difficulty": final_result.difficulty,
                        "weak_model_failures": final_result.weak_model_failures
                    }
                }
                break
            else:
                # This is a PipelineStep object
                step_data = {
                    "type": "step",
                    "step_number": item.step_number,
                    "description": item.step_name,  # Fixed: step_name not description
                    "model": item.model_used,  # Fixed: model_used not model
                    "success": item.success,
                    "timestamp": item.timestamp,
                    "response_preview": item.response[:500] if item.response else None,
                    "response_full": item.response,  # Full response for debugging
                }

                yield step_data

        except StopIteration:
            # Generator finished
            break
        except Exception as e:
            logger.exception("Error in streaming pipeline")
            yield {
                "type": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            break

if __name__ == "__main__":
    import uvicorn

    # Run server
    # For development: uvicorn api_server:app --reload --port 8000
    # For production: configured via Render
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes (dev only)
        log_level="info"
    )
