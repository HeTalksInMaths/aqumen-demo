"""
Corrected 7-Step Adversarial Pipeline Implementation - Backward Compatibility Wrapper

This module now delegates to the refactored modular implementation in legacy_pipeline/.
Maintained for backward compatibility with existing integrations.

For new code, use: from legacy_pipeline import LegacyPipelineOrchestrator
"""

import logging

from legacy_pipeline import LegacyPipelineOrchestrator
from legacy_pipeline.models import PipelineStep, SevenStepResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Re-export data classes for backward compatibility
__all__ = ["PipelineStep", "SevenStepResult", "CorrectedSevenStepPipeline"]


class CorrectedSevenStepPipeline:
    """
    Backward compatibility wrapper around LegacyPipelineOrchestrator.

    This class maintains the same API as the original monolithic implementation
    but delegates all work to the refactored modular architecture.
    """

    def __init__(self, provider: str = "anthropic"):
        """
        Initialize the corrected 7-step pipeline with timestamped logging.

        Args:
            provider: Model provider to use - either "anthropic" (default) or "openai"
        """
        # Delegate to the refactored orchestrator
        self._orchestrator = LegacyPipelineOrchestrator(provider=provider)

        # Expose commonly accessed attributes for backward compatibility
        self.provider = self._orchestrator.provider
        self.runtime_client = self._orchestrator.runtime_client
        self.model_strong = self._orchestrator.model_strong
        self.model_mid = self._orchestrator.model_mid
        self.model_weak = self._orchestrator.model_weak
        self.judge_supports_thinking = self._orchestrator.judge_supports_thinking
        self.invoker = self._orchestrator.invoker
        self.script_dir = self._orchestrator.script_dir
        self.db_path = self._orchestrator.db_path
        self.prompts = self._orchestrator.prompts
        self.tools = self._orchestrator.tools

        # These will be set on each run now (lazy initialization)
        self.run_timestamp = None
        self.logger = None
        self.log_file = None
        self.results_file = None
        self.repo = None

        # Expose Bedrock-specific attributes for backward compatibility
        if provider == "anthropic":
            self.bedrock_runtime = self._orchestrator.bedrock_runtime
            self.aws_region = self._orchestrator.aws_region

        # Expose config attributes
        self.allowed_difficulties = self._orchestrator.config.ALLOWED_DIFFICULTIES
        self.step7_max_attempts = self._orchestrator.config.STEP7_MAX_ATTEMPTS
        self.min_code_lines = self._orchestrator.config.MIN_CODE_LINES
        self.max_code_lines = self._orchestrator.config.MAX_CODE_LINES
        self.min_errors = self._orchestrator.config.MIN_ERRORS
        self.max_errors = self._orchestrator.config.MAX_ERRORS
        self.min_error_span = self._orchestrator.config.MIN_ERROR_SPAN
        self.max_error_span = self._orchestrator.config.MAX_ERROR_SPAN

    def run_full_pipeline(self, topic: str, max_attempts: int = 3) -> SevenStepResult:
        """
        Run the complete corrected 7-step pipeline.

        Args:
            topic: The topic to generate questions for
            max_attempts: Maximum retry attempts for differentiation

        Returns:
            SevenStepResult with complete execution details
        """
        result = self._orchestrator.run_full_pipeline(topic, max_attempts)
        # Sync lazy-initialized attributes back to wrapper for backward compatibility
        self.run_timestamp = self._orchestrator.run_timestamp
        self.logger = self._orchestrator.logger
        if self.logger:
            self.log_file = self.logger.log_file
            self.results_file = self.logger.results_file
            self.repo = self.logger.repo
        return result

    def run_full_pipeline_streaming(self, topic: str, max_attempts: int = 3):
        """
        Generator version of run_full_pipeline that yields each step as it completes.

        This enables real-time streaming via SSE for debugging and progress tracking.

        Args:
            topic: The topic to generate questions for
            max_attempts: Maximum retry attempts for differentiation

        Yields:
            PipelineStep objects as each step completes
            Final yield contains dict with final result including all metadata
        """
        for step_or_result in self._orchestrator.run_full_pipeline_streaming(topic, max_attempts):
            yield step_or_result
        # Sync lazy-initialized attributes back to wrapper for backward compatibility
        self.run_timestamp = self._orchestrator.run_timestamp
        self.logger = self._orchestrator.logger
        if self.logger:
            self.log_file = self.logger.log_file
            self.results_file = self.logger.results_file
            self.repo = self.logger.repo

    def run_batch_test(self, topics: list[str]) -> list[SevenStepResult]:
        """
        Run corrected 7-step pipeline on multiple topics.

        Args:
            topics: List of topics to process

        Returns:
            List of SevenStepResult objects
        """
        return self._orchestrator.run_batch_test(topics)

    def _extract_common_failures(self, results: list[SevenStepResult]) -> dict[str, int]:
        """Extract common patterns from weak model failures"""
        return LegacyPipelineOrchestrator.extract_common_failures(results)

    def _validate_assessment_payload(self, payload: dict) -> tuple[bool, dict, list[str]]:
        """Validate Step 7 assessment payload (exposed for testing)."""
        from legacy_pipeline.validators.assessment_validator import AssessmentValidator

        validator = AssessmentValidator(self._orchestrator.config)
        return validator.validate_assessment(payload)

    def _get_prompt_template(self, step_key: str) -> str:
        """Retrieve the prompt template string for a pipeline step (exposed for testing)."""
        entry = self.prompts.get(step_key)
        if isinstance(entry, dict):
            template = entry.get("template")
        else:
            template = entry

        if not isinstance(template, str):
            raise KeyError(f"Prompt template missing for step '{step_key}'")

        return template

    def step1_generate_difficulty_categories(self, topic: str) -> tuple[bool, dict, "PipelineStep"]:
        """Execute Step 1: Generate difficulty categories (exposed for API)."""
        success, categories, step1, _ = self._orchestrator.step1.execute(topic)
        return success, categories, step1

    def invoke_model(self, model_id: str, prompt: str, max_tokens: int = 2048, temperature: float = 0.0) -> str:
        """Invoke a model directly (exposed for testing)."""
        return self._orchestrator.invoker.text(model_id, prompt, max_tokens)


def main():
    """Run corrected 7-step pipeline test"""
    pipeline = CorrectedSevenStepPipeline()

    test_topics = [
        "LLM Post-Training with DPO",
        "Model Quantization and Optimization",
        "Reinforcement Learning from Human Feedback (RLHF)",
    ]

    print("🧠 CORRECTED 7-Step Adversarial Pipeline Test")
    print("=" * 50)
    print("Key Changes:")
    print("- Step 3: Strategic questions (NO pre-embedded errors)")
    print("- Steps 4-5: Models provide complete implementations")
    print("- Step 6: Judge compares implementations vs error catalog")
    print("- Step 7: Creates assessment based on actual weak failures")
    print("=" * 50)

    results = pipeline.run_batch_test(test_topics)

    # Summary analysis
    successful = len([r for r in results if r.differentiation_achieved])
    stopped_at_6 = len([r for r in results if r.stopped_at_step == 6])

    print("\n🏆 CORRECTED PIPELINE RESULTS")
    print(f"Topics with successful differentiation: {successful}/{len(results)}")
    print(f"Topics stopped at Step 6 (no differentiation): {stopped_at_6}/{len(results)}")
    print(f"Step 6 blocking rate: {(stopped_at_6 / len(results)) * 100:.1f}%")

    # Show common failure patterns
    if results:
        common_failures = pipeline._extract_common_failures(results)
        if common_failures:
            print("\n📊 Common Weak Model Failure Patterns:")
            for failure, count in common_failures.items():
                print(f"  {count}x: {failure}")


if __name__ == "__main__":
    main()
