"""Step 1: Generate difficulty categories for a topic."""

import logging
from datetime import datetime
from typing import Any

from analytics.rewards import StepRewardsReport, rewards_step1
from legacy_pipeline.models import PipelineStep

logger = logging.getLogger(__name__)


class DifficultyStep:
    """Handles Step 1: Generate difficulty categories."""

    def __init__(self, invoker, model_mid: str, prompts: dict, tools: dict):
        """
        Initialize the difficulty category generation step.

        Args:
            invoker: Model invocation service
            model_mid: Mid-tier model ID to use
            prompts: Prompt templates dictionary
            tools: Tool specifications dictionary
        """
        self.invoker = invoker
        self.model_mid = model_mid
        self.prompts = prompts
        self.tools = tools

    def execute(self, topic: str) -> tuple[bool, dict[str, list[str]], PipelineStep, StepRewardsReport | None]:
        """
        Execute Step 1: Generate difficulty categories.

        Args:
            topic: The topic to generate difficulty categories for

        Returns:
            Tuple of (success, categories_dict, pipeline_step, rewards_report)
        """
        logger.info(f"Step 1: Generating difficulty categories for topic: {topic}")

        template = self._get_prompt_template("step1_difficulty_categories")
        prompt = template.format(topic=topic)
        tools = self._get_tools("step1_difficulty_categories")

        response = self.invoker.tools(self.model_mid, prompt, tools)
        step = PipelineStep(
            1,
            "Generate difficulty categories",
            self.model_mid,
            False,
            str(response),
            datetime.now().isoformat(),
        )

        categories: dict[str, list[str]] = {}
        try:
            if isinstance(response, dict) and "error" not in response:
                candidate = response
                required_keys = {"Beginner", "Intermediate", "Advanced"}
                key_set = set(candidate.keys())
                counts_valid = all(
                    isinstance(candidate.get(key), list) and 3 <= len(candidate.get(key, [])) <= 5
                    for key in required_keys
                )
                if key_set == required_keys and counts_valid:
                    categories = candidate
                    step.success = True
                else:
                    step.success = False
            else:
                step.success = False
        except Exception:
            step.success = False
            categories = {}

        # Calculate rewards
        reward_report = rewards_step1(categories if step.success else {})

        if not step.success:
            categories = {}

        return step.success, categories, step, reward_report

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
