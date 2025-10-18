"""Steps 4-5: Test model implementations (Sonnet and Haiku)."""

import logging
from datetime import datetime

from analytics.rewards import StepRewardsReport, rewards_step45
from legacy_pipeline.models import PipelineStep

logger = logging.getLogger(__name__)


class ModelTestingStep:
    """Handles Steps 4-5: Test mid-tier and weak-tier model implementations."""

    def __init__(self, invoker, model_mid: str, model_weak: str, prompts: dict):
        """
        Initialize the model testing step.

        Args:
            invoker: Model invocation service
            model_mid: Mid-tier model ID (Sonnet/Haiku 3.5)
            model_weak: Weak-tier model ID (Haiku 3)
            prompts: Prompt templates dictionary
        """
        self.invoker = invoker
        self.model_mid = model_mid
        self.model_weak = model_weak
        self.prompts = prompts

    def execute_step4_sonnet(self, question: dict) -> tuple[bool, str, PipelineStep, StepRewardsReport | None]:
        """
        Execute Step 4: Test Sonnet (mid-tier) implementation response.

        Args:
            question: The question dictionary from Step 3

        Returns:
            Tuple of (success, response_text, pipeline_step, rewards_report)
        """
        logger.info("Step 4: Testing Sonnet (mid-tier) implementation")

        template = self._get_prompt_template("step4_test_sonnet")
        requirements = question.get("requirements", []) or []
        prompt = template.format(
            context=question.get("context", "the domain"),
            artifact=question.get("artifact_type", "artifact"),
            title=question.get("title", "Implementation Challenge"),
            question_text=question.get("question_text", ""),
            requirements="\n".join(f"- {req}" for req in requirements)
            if requirements
            else "- (no requirements provided)",
            success_criteria=question.get(
                "success_criteria",
                "Meets requirements with sound reasoning and robustness",
            ),
        )

        response = self.invoker.text(self.model_mid, prompt)
        step = PipelineStep(
            4,
            "Test Sonnet (mid-tier) implementation",
            self.model_mid,
            True,
            response,
            datetime.now().isoformat(),
        )

        # Calculate rewards
        reward_report = rewards_step45(response, requirements)

        return True, response, step, reward_report

    def execute_step5_haiku(self, question: dict) -> tuple[bool, str, PipelineStep, StepRewardsReport | None]:
        """
        Execute Step 5: Test Haiku (weak-tier) implementation response.

        Args:
            question: The question dictionary from Step 3

        Returns:
            Tuple of (success, response_text, pipeline_step, rewards_report)
        """
        logger.info("Step 5: Testing Haiku (weak-tier) implementation")

        template = self._get_prompt_template("step5_test_haiku")
        requirements = question.get("requirements", []) or []
        prompt = template.format(
            context=question.get("context", "the domain"),
            artifact=question.get("artifact_type", "artifact"),
            title=question.get("title", "Implementation Challenge"),
            question_text=question.get("question_text", ""),
            requirements="\n".join(f"- {req}" for req in requirements)
            if requirements
            else "- (no requirements provided)",
            success_criteria=question.get(
                "success_criteria",
                "Meets requirements with sound reasoning and robustness",
            ),
        )

        response = self.invoker.text(self.model_weak, prompt)
        step = PipelineStep(
            5,
            "Test Haiku (weak-tier) implementation",
            self.model_weak,
            True,
            response,
            datetime.now().isoformat(),
        )

        # Calculate rewards
        reward_report = rewards_step45(response, requirements)

        return True, response, step, reward_report

    def _get_prompt_template(self, step_key: str) -> str:
        """Retrieve the prompt template string for a pipeline step."""
        entry = self.prompts.get(step_key)
        if isinstance(entry, dict):
            template = entry.get("template")
        else:
            template = entry

        if not isinstance(template, str):
            raise KeyError(f"Prompt template missing for step '{step_key}'")

        return template
