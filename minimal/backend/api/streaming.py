"""
Server-Sent Events (SSE) streaming implementation for real-time pipeline updates.

This module handles the streaming of pipeline execution steps to clients,
allowing them to see each step complete as it happens.
"""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from datetime import datetime

logger = logging.getLogger(__name__)


def format_sse_message(data: dict, event_type: str = "message") -> str:
    """
    Format a message for Server-Sent Events protocol.

    SSE format:
    event: <event_type>
    data: <json_data>

    Args:
        data: Dictionary to send as JSON data
        event_type: Type of event (message, step, done, error, etc.)

    Returns:
        Formatted SSE message string
    """
    json_data = json.dumps(data)
    return f"event: {event_type}\ndata: {json_data}\n\n"


async def run_pipeline_streaming(pipeline, topic: str, max_retries: int) -> AsyncGenerator[dict, None]:
    """
    Run the pipeline and yield each step as it completes.

    This wraps the synchronous pipeline generator in an async wrapper
    to provide real-time streaming updates via SSE.

    Args:
        pipeline: CorrectedSevenStepPipeline instance
        topic: Topic for question generation
        max_retries: Maximum retry attempts for differentiation

    Yields:
        Dictionary containing step data or final results
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
                        "weak_model_failures": final_result.weak_model_failures,
                    },
                }
                break
            else:
                # This is a PipelineStep object
                step_data = {
                    "type": "step",
                    "step_number": item.step_number,
                    "description": item.step_name,
                    "model": item.model_used,
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
            yield {"type": "error", "error": str(e), "timestamp": datetime.now().isoformat()}
            break
