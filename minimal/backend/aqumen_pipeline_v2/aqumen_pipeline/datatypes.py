from dataclasses import dataclass, field
from typing import Any


@dataclass
class PipelineStep:
    step_number: int
    step_name: str
    model_used: str
    success: bool
    response: str
    timestamp: str

@dataclass
class SevenStepResult:
    topic: str
    subtopic: str
    difficulty: str
    steps_completed: list[PipelineStep]
    final_success: bool
    stopped_at_step: int
    differentiation_achieved: bool
    student_assessment_created: bool
    total_attempts: int
    weak_model_failures: list[str]
    token_usage: dict[str, Any] = field(default_factory=dict)
    total_cost_usd: float = 0.0
