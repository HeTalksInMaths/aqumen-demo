"""Step 3: Generate strategic implementation challenge questions."""

import logging
from datetime import datetime
from typing import Any

from analytics.rewards import StepRewardsReport, rewards_step3
from legacy_pipeline.models import PipelineStep

logger = logging.getLogger(__name__)


class QuestionGenerationStep:
    """Handles Step 3: Generate strategic implementation challenge questions."""

    def __init__(
        self,
        invoker,
        model_strong: str,
        prompts: dict,
        tools: dict,
        judge_supports_thinking: bool = False,
    ):
        """
        Initialize the question generation step.

        Args:
            invoker: Model invocation service
            model_strong: Strong model ID to use
            prompts: Prompt templates dictionary
            tools: Tool specifications dictionary
            judge_supports_thinking: Whether the model supports thinking mode
        """
        self.invoker = invoker
        self.model_strong = model_strong
        self.prompts = prompts
        self.tools = tools
        self.judge_supports_thinking = judge_supports_thinking

    def execute(
        self,
        topic: str,
        subtopic: str,
        difficulty: str,
        error_catalog: list[dict],
        previous_failures: list[str] | None = None,
        use_thinking: bool = False,
    ) -> tuple[bool, dict, PipelineStep, StepRewardsReport | None]:
        """
        Execute Step 3: Generate strategic implementation challenge.

        Args:
            topic: The main topic
            subtopic: Specific subtopic
            difficulty: Difficulty level
            error_catalog: Error catalog from Step 2
            previous_failures: Validation feedback from previous attempts
            use_thinking: Whether to enable thinking mode

        Returns:
            Tuple of (success, question_dict, pipeline_step, rewards_report)
        """
        logger.info(f"Step 3: Generating strategic question for {topic} - {subtopic} ({difficulty})")

        template = self._get_prompt_template("step3_strategic_question")

        failure_feedback = ""
        if previous_failures:
            failure_feedback = "\nVALIDATION FEEDBACK (resolve before returning a new challenge):\n" + "\n".join(
                f"- {failure}" for failure in previous_failures
            )

        catalog_names: list[str] = []
        for error in error_catalog or []:
            name = error.get("mistake")
            if isinstance(name, str) and name.strip():
                catalog_names.append(f"- {name.strip()}")

        prompt = template.format(
            topic=topic,
            subtopic=subtopic,
            difficulty=difficulty,
            catalog_names="\n".join(catalog_names) if catalog_names else "- (no catalog names available)",
            failure_feedback=failure_feedback,
        )

        tools = self._get_tools("step3_strategic_question")

        response = self.invoker.tools(
            self.model_strong,
            prompt,
            tools,
            use_thinking=use_thinking and self.judge_supports_thinking,
            thinking_budget=2048,
        )
        step = PipelineStep(
            3,
            "Generate strategic implementation challenge",
            self.model_strong,
            False,
            str(response),
            datetime.now().isoformat(),
        )

        question: dict[str, Any] = {}
        try:
            if isinstance(response, dict) and "error" not in response:
                candidate = response
                requirements = candidate.get("requirements")
                artifact_type = candidate.get("artifact_type")
                required_fields_present = all(
                    isinstance(candidate.get(field), str) and bool(str(candidate.get(field)).strip())
                    for field in (
                        "title",
                        "question_text",
                        "context",
                        "success_criteria",
                    )
                )
                valid_req_count = isinstance(requirements, list) and 4 <= len(requirements) <= 6
                valid_artifact = isinstance(artifact_type, str) and artifact_type in {
                    "code",
                    "prose",
                    "math",
                    "email",
                    "table",
                    "diagram",
                    "plan",
                    "pseudo",
                    "query",
                    "other",
                }

                if required_fields_present and valid_req_count and valid_artifact:
                    question = candidate
                    step.success = True
                else:
                    step.success = False
            else:
                step.success = False
        except Exception:
            step.success = False
            question = {}

        # Calculate rewards
        reward_report = rewards_step3(question if step.success else {})

        if not step.success:
            question = {}

        return step.success, question, step, reward_report

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

    def _get_tools(self, step_key: str) -> list[dict[str, Any]]:
        """Retrieve tool specifications for a pipeline step."""
        from copy import deepcopy

        tool_entry = self.tools.get(step_key)

        if tool_entry is None:
            raise KeyError(f"Tool configuration missing for step '{step_key}'")

        if isinstance(tool_entry, list):
            return deepcopy(tool_entry)

        return [deepcopy(tool_entry)]
