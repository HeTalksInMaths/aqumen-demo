"""Step 2: Generate conceptual error catalog."""

import logging
from datetime import datetime
from typing import Any, Optional

from analytics.rewards import StepRewardsReport, rewards_step2
from legacy_pipeline.models import PipelineStep

logger = logging.getLogger(__name__)


class ErrorCatalogStep:
    """Handles Step 2: Generate conceptual error catalog."""

    def __init__(self, invoker, model_mid: str, prompts: dict, tools: dict):
        """
        Initialize the error catalog generation step.

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

    def execute(
        self, topic: str, subtopic: str, difficulty: str
    ) -> tuple[bool, list[dict], PipelineStep, Optional[StepRewardsReport]]:
        """
        Execute Step 2: Generate conceptual error catalog.

        Args:
            topic: The main topic
            subtopic: Specific subtopic within the topic
            difficulty: Difficulty level

        Returns:
            Tuple of (success, errors_list, pipeline_step, rewards_report)
        """
        logger.info(
            f"Step 2: Generating error catalog for {topic} - {subtopic} ({difficulty})"
        )

        template = self._get_prompt_template("step2_error_catalog")
        prompt = template.format(topic=topic, difficulty=difficulty, subtopic=subtopic)
        tools = self._get_tools("step2_error_catalog")

        response = self.invoker.tools(self.model_mid, prompt, tools)
        step = PipelineStep(
            2,
            "Generate conceptual error catalog",
            self.model_mid,
            False,
            str(response),
            datetime.now().isoformat(),
        )

        errors: list[dict[str, Any]] = []
        try:
            if isinstance(response, dict) and isinstance(response.get("errors"), list):
                raw_errors = response["errors"]
                for entry in raw_errors:
                    if not isinstance(entry, dict):
                        continue
                    entry_copy = dict(entry)
                    # Normalize field names
                    if "match_hint" not in entry_copy and "code_pattern" in entry_copy:
                        entry_copy["match_hint"] = entry_copy["code_pattern"]
                    if "code_pattern" not in entry_copy and "match_hint" in entry_copy:
                        entry_copy["code_pattern"] = entry_copy["match_hint"]
                    errors.append(entry_copy)

            step.success = len(errors) == 6
        except Exception:
            step.success = False
            errors = []

        # Calculate rewards
        reward_report = rewards_step2(errors)

        if not step.success:
            errors = []

        return step.success, errors, step, reward_report

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
