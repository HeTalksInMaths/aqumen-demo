"""
Pydantic models for API request/response validation.

These models define the structure and validation rules for all API endpoints.
"""

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Request model for question generation endpoints."""

    topic: str = Field(..., description="AI/ML topic for question generation", min_length=3, max_length=200)
    difficulty_preference: str | None = Field(
        None, description="Preferred difficulty: Beginner, Intermediate, Advanced, Expert"
    )
    max_retries: int = Field(3, description="Maximum retries if question isn't hard enough", ge=1, le=5)


class QuestionResponse(BaseModel):
    """Response model for generated questions."""

    title: str
    difficulty: str
    code: list[str]
    errors: list[dict]
    metadata: dict


class HealthResponse(BaseModel):
    """Response model for health check endpoints."""

    status: str
    timestamp: str
    pipeline_ready: bool
    version: str
