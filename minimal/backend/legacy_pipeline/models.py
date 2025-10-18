"""Data models for the 7-step adversarial pipeline."""

from dataclasses import dataclass


@dataclass
class PipelineStep:
    """Represents a single step execution in the pipeline."""

    step_number: int
    step_name: str
    model_used: str
    success: bool
    response: str
    timestamp: str


@dataclass
class SevenStepResult:
    """Comprehensive result from a complete pipeline run."""

    topic: str
    subtopic: str
    difficulty: str
    steps_completed: list[PipelineStep]
    final_success: bool
    stopped_at_step: int
    differentiation_achieved: bool
    student_assessment_created: bool
    total_attempts: int
    weak_model_failures: list[str]  # Track actual failure patterns
