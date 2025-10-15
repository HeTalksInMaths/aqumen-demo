from dataclasses import dataclass, field
from typing import List, Any, Dict

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
    steps_completed: List[PipelineStep]
    final_success: bool
    stopped_at_step: int
    differentiation_achieved: bool
    student_assessment_created: bool
    total_attempts: int
    weak_model_failures: List[str] = field(default_factory=list)
    assessment: Dict[str, Any] = field(default_factory=dict)