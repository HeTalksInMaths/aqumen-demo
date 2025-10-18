"""Legacy 7-Step Adversarial Pipeline - Modular Architecture

This package contains the refactored corrected_7step_pipeline.py implementation,
split into focused modules following the aqumen_pipeline_v2 pattern.
"""

from legacy_pipeline.models import PipelineStep, SevenStepResult
from legacy_pipeline.orchestrator import LegacyPipelineOrchestrator

__all__ = [
    "PipelineStep",
    "SevenStepResult",
    "LegacyPipelineOrchestrator",
]
