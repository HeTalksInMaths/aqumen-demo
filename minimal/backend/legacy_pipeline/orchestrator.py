"""Main pipeline orchestrator coordinating all 7 steps."""

import json
import logging
import os
import random
from datetime import datetime
from typing import Any

from clients.provider import get_model_provider
from config.prompts_loader import load_prompts
from config.tools_loader import load_tools
from legacy_pipeline.config import PipelineConfig
from legacy_pipeline.models import SevenStepResult
from legacy_pipeline.persistence.pipeline_logger import PipelineLogger
from legacy_pipeline.steps import (
    AssessmentStep,
    DifficultyStep,
    ErrorCatalogStep,
    JudgmentStep,
    ModelTestingStep,
    QuestionGenerationStep,
)
from roles import load_model_roles
from services.invoke import Invoker

logger = logging.getLogger(__name__)


class LegacyPipelineOrchestrator:
    """
    Orchestrates the corrected 7-step adversarial pipeline.

    This is the refactored version of CorrectedSevenStepPipeline,
    with step logic extracted into focused modules.
    """

    def __init__(self, provider: str = "anthropic"):
        """
        Initialize the pipeline orchestrator.

        Args:
            provider: Model provider to use - either "anthropic" (default) or "openai"
        """
        self.provider = provider
        self.config = PipelineConfig()

        # Get client and models for the specified provider
        try:
            self.runtime_client, models = get_model_provider(provider)
            self.model_strong = models["strong"]
            self.model_mid = models["mid"]
            self.model_weak = models["weak"]

            # For Anthropic, check if judge supports thinking
            if provider == "anthropic":
                self.roles = load_model_roles()
                self.judge_supports_thinking = self.roles["judge"].supports_thinking
            else:
                # OpenAI thinking support TBD
                self.judge_supports_thinking = False

            logger.info(f"Pipeline initialized with provider: {provider}")
            logger.info(f"Models - Strong: {self.model_strong}, Mid: {self.model_mid}, Weak: {self.model_weak}")
        except Exception as e:
            logger.error(f"Failed to initialize pipeline with provider '{provider}': {e}")
            raise

        # Maintain backward compatibility for Bedrock-specific attributes
        if provider == "anthropic":
            self.bedrock_runtime = self.runtime_client
            self.aws_region = "us-west-2"

        self.invoker = Invoker(self.runtime_client)

        # Set up directory structure
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level from legacy_pipeline to backend
        self.script_dir = os.path.dirname(script_dir)

        # Generate timestamped identifier for this run
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Initialize database path
        self.db_path = os.path.join(self.script_dir, "pipeline_results.db")

        # Initialize logger
        self.logger = PipelineLogger(self.script_dir, self.run_timestamp, self.db_path)

        # Load prompts and tools
        try:
            self.prompts = load_prompts()
            self.tools = load_tools()
        except Exception as exc:
            logger.error(f"Failed to load prompt/tool configuration: {exc}")
            raise

        # Initialize step executors
        self._init_step_executors()

    def _init_step_executors(self) -> None:
        """Initialize all step executor modules."""
        self.step1 = DifficultyStep(self.invoker, self.model_mid, self.prompts, self.tools)

        self.step2 = ErrorCatalogStep(self.invoker, self.model_mid, self.prompts, self.tools)

        self.step3 = QuestionGenerationStep(
            self.invoker,
            self.model_strong,
            self.prompts,
            self.tools,
            self.judge_supports_thinking,
        )

        self.step4_5 = ModelTestingStep(self.invoker, self.model_mid, self.model_weak, self.prompts)

        self.step6 = JudgmentStep(self.invoker, self.model_strong, self.prompts, self.tools)

        self.step7 = AssessmentStep(
            self.invoker,
            self.model_strong,
            self.prompts,
            self.tools,
            self.judge_supports_thinking,
            self.config,
        )

    def run_full_pipeline(self, topic: str, max_attempts: int = 3) -> SevenStepResult:
        """
        Run the complete corrected 7-step pipeline.

        Args:
            topic: The topic to generate questions for
            max_attempts: Maximum retry attempts for differentiation (default: 3)

        Returns:
            SevenStepResult with complete execution details
        """
        logger.info(f"Starting corrected 7-step pipeline for: {topic}")

        # Initialize logging
        self.logger.initialize_run(topic)

        steps_completed = []

        # Step 1: Generate difficulty categories
        success, categories, step1, reward1 = self.step1.execute(topic)
        steps_completed.append(step1)
        self.logger.log_step(step1)
        self.logger.log_step_reward(1, reward1)

        if not success:
            result = SevenStepResult(topic, "", "", steps_completed, False, 1, False, False, 1, [])
            self.logger.finalize_run(result)
            return result

        # Randomly select difficulty level and subtopic for testing
        available_difficulties = [
            d for d in ["Beginner", "Intermediate", "Advanced"] if d in categories and categories[d]
        ]
        if available_difficulties:
            difficulty = random.choice(available_difficulties)
            subtopics = categories.get(difficulty, ["General concepts"])
            subtopic = random.choice(subtopics) if subtopics else "General concepts"
        else:
            difficulty = "Intermediate"
            subtopic = "General concepts"

        # Step 2: Generate error catalog (run once)
        success, error_catalog, step2, reward2 = self.step2.execute(topic, subtopic, difficulty)
        steps_completed.append(step2)
        self.logger.log_step(step2)
        self.logger.log_step_reward(2, reward2)

        if not success:
            result = SevenStepResult(topic, subtopic, difficulty, steps_completed, False, 2, False, False, 1, [])
            self.logger.finalize_run(result)
            return result

        # Retry loop for steps 3-6 (strategic question → implementation testing → differentiation judgment)
        previous_failures = []
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Strategic differentiation attempt {attempt} for {topic}")
            attempt_steps = []

            # Enable thinking mode on retries
            use_thinking = attempt > 1 and self.judge_supports_thinking

            # Step 3: Generate strategic implementation challenge
            success, question, step3, reward3 = self.step3.execute(
                topic,
                subtopic,
                difficulty,
                error_catalog,
                previous_failures,
                use_thinking=use_thinking,
            )
            attempt_steps.append(step3)
            self.logger.log_step(step3)
            self.logger.log_step_reward(3, reward3)

            if not success:
                steps_completed.extend(attempt_steps)
                continue

            # Step 4: Test Sonnet implementation
            (
                sonnet_success,
                sonnet_response,
                step4,
                reward4,
            ) = self.step4_5.execute_step4_sonnet(question)
            attempt_steps.append(step4)
            self.logger.log_step(step4)
            self.logger.log_step_reward(4, reward4)

            # Step 5: Test Haiku implementation
            (
                haiku_success,
                haiku_response,
                step5,
                reward5,
            ) = self.step4_5.execute_step5_haiku(question)
            attempt_steps.append(step5)
            self.logger.log_step(step5)
            self.logger.log_step_reward(5, reward5)

            # Step 6: Judge differentiation (KEY DECISION POINT)
            (
                differentiation_achieved,
                judge_payload,
                haiku_failures,
                step6,
                reward6,
            ) = self.step6.execute(question, sonnet_response, haiku_response, error_catalog)
            attempt_steps.append(step6)
            self.logger.log_step(step6)
            self.logger.log_step_reward(6, reward6)

            steps_completed.extend(attempt_steps)

            # Extract judge reasoning for feedback
            judge_reasoning_text = self._extract_judge_reasoning(judge_payload)
            judge_reasoning_lower = judge_reasoning_text.lower()

            if differentiation_achieved:
                logger.info(f"✅ Differentiation achieved on attempt {attempt}")

                # Step 7: Create student assessment based on actual weak model failures
                success, assessment, step7, reward7 = self.step7.execute(
                    question, sonnet_response, haiku_response, haiku_failures
                )
                steps_completed.append(step7)
                self.logger.log_step(step7)
                self.logger.log_step_reward(7, reward7)

                result = SevenStepResult(
                    topic=topic,
                    subtopic=subtopic,
                    difficulty=difficulty,
                    steps_completed=steps_completed,
                    final_success=True,
                    stopped_at_step=7,
                    differentiation_achieved=True,
                    student_assessment_created=success,
                    total_attempts=attempt,
                    weak_model_failures=haiku_failures,
                )
                self.logger.finalize_run(result, assessment if success else None)
                return result
            else:
                logger.info(f"❌ Attempt {attempt} failed differentiation - Step 6 blocked progression")

                # Build detailed failure context for next attempt
                failure_text = self._build_failure_feedback(
                    attempt,
                    judge_reasoning_text,
                    judge_reasoning_lower,
                    sonnet_response,
                    haiku_response,
                )
                previous_failures.append(failure_text)

        # All attempts failed - stopped at Step 6
        result = SevenStepResult(
            topic=topic,
            subtopic=subtopic,
            difficulty=difficulty,
            steps_completed=steps_completed,
            final_success=False,
            stopped_at_step=6,
            differentiation_achieved=False,
            student_assessment_created=False,
            total_attempts=max_attempts,
            weak_model_failures=[],
        )
        self.logger.finalize_run(result)
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
        logger.info(f"Starting streaming 7-step pipeline for: {topic}")

        # Initialize logging
        self.logger.initialize_run(topic)

        steps_completed = []

        # Step 1: Generate difficulty categories
        success, categories, step1, reward1 = self.step1.execute(topic)
        steps_completed.append(step1)
        self.logger.log_step(step1)
        self.logger.log_step_reward(1, reward1)
        yield step1  # ← Yield immediately!

        if not success:
            result = SevenStepResult(topic, "", "", steps_completed, False, 1, False, False, 1, [])
            self.logger.finalize_run(result)
            yield {"final_result": result}
            return

        # Randomly select difficulty level and subtopic
        available_difficulties = [
            d for d in ["Beginner", "Intermediate", "Advanced"] if d in categories and categories[d]
        ]
        if available_difficulties:
            difficulty = random.choice(available_difficulties)
            subtopics = categories.get(difficulty, ["General concepts"])
            subtopic = random.choice(subtopics) if subtopics else "General concepts"
        else:
            difficulty = "Intermediate"
            subtopic = "General concepts"

        # Step 2: Generate error catalog
        success, error_catalog, step2, reward2 = self.step2.execute(topic, subtopic, difficulty)
        steps_completed.append(step2)
        self.logger.log_step(step2)
        self.logger.log_step_reward(2, reward2)
        yield step2  # ← Yield immediately!

        if not success:
            result = SevenStepResult(topic, subtopic, difficulty, steps_completed, False, 2, False, False, 1, [])
            self.logger.finalize_run(result)
            yield {"final_result": result}
            return

        # Retry loop for steps 3-6
        previous_failures = []
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Strategic differentiation attempt {attempt} for {topic}")
            attempt_steps = []

            # Enable thinking mode on retries
            use_thinking = attempt > 1 and self.judge_supports_thinking

            # Step 3: Generate strategic implementation challenge
            success, question, step3, reward3 = self.step3.execute(
                topic,
                subtopic,
                difficulty,
                error_catalog,
                previous_failures,
                use_thinking=use_thinking,
            )
            attempt_steps.append(step3)
            self.logger.log_step(step3)
            self.logger.log_step_reward(3, reward3)
            yield step3  # ← Yield immediately!

            if not success:
                steps_completed.extend(attempt_steps)
                continue

            # Step 4: Test Sonnet implementation
            (
                sonnet_success,
                sonnet_response,
                step4,
                reward4,
            ) = self.step4_5.execute_step4_sonnet(question)
            attempt_steps.append(step4)
            self.logger.log_step(step4)
            self.logger.log_step_reward(4, reward4)
            yield step4  # ← Yield immediately!

            # Step 5: Test Haiku implementation
            (
                haiku_success,
                haiku_response,
                step5,
                reward5,
            ) = self.step4_5.execute_step5_haiku(question)
            attempt_steps.append(step5)
            self.logger.log_step(step5)
            self.logger.log_step_reward(5, reward5)
            yield step5  # ← Yield immediately!

            # Step 6: Judge differentiation
            (
                differentiation_achieved,
                judge_payload,
                haiku_failures,
                step6,
                reward6,
            ) = self.step6.execute(question, sonnet_response, haiku_response, error_catalog)
            attempt_steps.append(step6)
            self.logger.log_step(step6)
            self.logger.log_step_reward(6, reward6)
            yield step6  # ← Yield immediately!

            steps_completed.extend(attempt_steps)

            # Extract judge reasoning
            judge_reasoning_text = self._extract_judge_reasoning(judge_payload)
            judge_reasoning_lower = judge_reasoning_text.lower()

            if differentiation_achieved:
                logger.info(f"✅ Differentiation achieved on attempt {attempt}")

                # Step 7: Create student assessment
                success, assessment, step7, reward7 = self.step7.execute(
                    question, sonnet_response, haiku_response, haiku_failures
                )
                steps_completed.append(step7)
                self.logger.log_step(step7)
                self.logger.log_step_reward(7, reward7)
                yield step7  # ← Yield immediately!

                # Yield final result
                final_result = SevenStepResult(
                    topic=topic,
                    subtopic=subtopic,
                    difficulty=difficulty,
                    steps_completed=steps_completed,
                    final_success=True,
                    stopped_at_step=7,
                    differentiation_achieved=True,
                    student_assessment_created=success,
                    total_attempts=attempt,
                    weak_model_failures=haiku_failures,
                )
                self.logger.finalize_run(final_result, assessment if success else None)
                yield {"final_result": final_result, "assessment": assessment}
                return
            else:
                logger.info(f"❌ Attempt {attempt} failed differentiation")

                # Build failure feedback
                failure_text = self._build_failure_feedback(
                    attempt,
                    judge_reasoning_text,
                    judge_reasoning_lower,
                    sonnet_response,
                    haiku_response,
                )
                previous_failures.append(failure_text)

        # All attempts failed - stopped at Step 6
        final_result = SevenStepResult(
            topic=topic,
            subtopic=subtopic,
            difficulty=difficulty,
            steps_completed=steps_completed,
            final_success=False,
            stopped_at_step=6,
            differentiation_achieved=False,
            student_assessment_created=False,
            total_attempts=max_attempts,
            weak_model_failures=[],
        )
        self.logger.finalize_run(final_result)
        yield {"final_result": final_result}

    def _extract_judge_reasoning(self, judge_payload: dict[str, Any]) -> str:
        """Extract reasoning text from judge payload."""
        if isinstance(judge_payload, dict):
            raw_reasoning = judge_payload.get("reasoning")
            if isinstance(raw_reasoning, str):
                return raw_reasoning.strip()
            # Fallback: stringify entire payload
            try:
                return json.dumps(judge_payload, ensure_ascii=False)
            except (TypeError, ValueError):
                return str(judge_payload)
        return ""

    def _build_failure_feedback(
        self,
        attempt: int,
        judge_reasoning_text: str,
        judge_reasoning_lower: str,
        sonnet_response: str,
        haiku_response: str,
    ) -> str:
        """Build detailed failure feedback for next attempt."""
        if "both models succeeded" in judge_reasoning_lower:
            return (
                f"Attempt {attempt}: Both models avoided errors. "
                f"Sonnet: {sonnet_response[:300]}... | "
                f"Haiku: {haiku_response[:300]}... | "
                "Need MORE SUBTLE conceptual traps"
            )
        elif "neither model succeeded" in judge_reasoning_lower:
            return (
                f"Attempt {attempt}: Neither model succeeded. "
                f"Question may be too ambiguous. "
                f"Judge said: {judge_reasoning_text[:200]}"
            )
        else:
            return f"Attempt {attempt}: Insufficient differentiation. Judge: {judge_reasoning_text[:300]}"

    def run_batch_test(self, topics: list[str]) -> list[SevenStepResult]:
        """
        Run corrected 7-step pipeline on multiple topics.

        Args:
            topics: List of topics to process

        Returns:
            List of SevenStepResult objects
        """
        results = []

        for i, topic in enumerate(topics, 1):
            print(f"\n{'=' * 60}")
            print(f"CORRECTED PIPELINE - TOPIC {i}/{len(topics)}: {topic}")
            print(f"{'=' * 60}")

            result = self.run_full_pipeline(topic)
            results.append(result)

            # Print immediate result
            if result.differentiation_achieved:
                print(f"✅ SUCCESS: Achieved differentiation in {result.total_attempts} attempts")
                if result.weak_model_failures:
                    print(f"   Weak model failures: {', '.join(result.weak_model_failures)}")
            else:
                print(f"❌ FAILED: Stopped at Step {result.stopped_at_step} after {result.total_attempts} attempts")

        return results

    @staticmethod
    def extract_common_failures(
        results: list[SevenStepResult],
    ) -> dict[str, int]:
        """
        Extract common patterns from weak model failures.

        Args:
            results: List of pipeline results

        Returns:
            Dictionary of failure patterns with their counts
        """
        failure_counts = {}
        for result in results:
            for failure in result.weak_model_failures:
                # Normalize failure text for counting
                normalized = failure.lower().strip()
                if normalized:
                    failure_counts[normalized] = failure_counts.get(normalized, 0) + 1

        # Return top 5 most common failures
        sorted_failures = sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_failures[:5])
