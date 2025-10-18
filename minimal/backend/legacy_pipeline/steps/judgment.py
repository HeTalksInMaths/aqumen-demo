"""Step 6: Judge implementation differentiation against error catalog."""

import json
import logging
from datetime import datetime
from typing import Any

from analytics.rewards import StepRewardsReport, rewards_step6
from legacy_pipeline.models import PipelineStep

logger = logging.getLogger(__name__)


class JudgmentStep:
    """Handles Step 6: Judge if differentiation was achieved between implementations."""

    def __init__(self, invoker, model_strong: str, prompts: dict, tools: dict):
        """
        Initialize the judgment step.

        Args:
            invoker: Model invocation service
            model_strong: Strong model ID to use
            prompts: Prompt templates dictionary
            tools: Tool specifications dictionary
        """
        self.invoker = invoker
        self.model_strong = model_strong
        self.prompts = prompts
        self.tools = tools

    def execute(
        self,
        question: dict,
        sonnet_response: str,
        haiku_response: str,
        error_catalog: list[dict],
    ) -> tuple[bool, dict[str, Any], list[str], PipelineStep, StepRewardsReport | None]:
        """
        Execute Step 6: Judge implementation differentiation.

        Args:
            question: The question from Step 3
            sonnet_response: Mid-tier model response from Step 4
            haiku_response: Weak-tier model response from Step 5
            error_catalog: Error catalog from Step 2

        Returns:
            Tuple of (differentiation_achieved, judge_payload, failures_weaker, pipeline_step, rewards_report)
        """
        logger.info("Step 6: Judging implementation differentiation")

        # Format entire error catalog for judge visibility
        error_patterns_text = ""
        for i, error in enumerate(error_catalog or [], 1):
            error_patterns_text += (
                f"\n{i}. {error.get('mistake', 'Unknown error')}\n"
                f"   Why problematic: {error.get('why_wrong', 'Issues not specified')}\n"
                f"   Code pattern: {error.get('code_pattern', error.get('match_hint', 'Not specified'))}"
            )

        template = self._get_prompt_template("step6_judge_responses")
        prompt = template.format(
            question_text=question.get("question_text", ""),
            context=question.get("context", ""),
            requirements=", ".join(question.get("requirements", [])),
            error_patterns_text=error_patterns_text,
            sonnet_response=sonnet_response,
            haiku_response=haiku_response,
        )

        tools = self._get_tools("step6_judge_responses")
        response = self.invoker.tools(self.model_strong, prompt, tools)
        step = PipelineStep(
            6,
            "Judge implementation differentiation",
            self.model_strong,
            False,
            json.dumps(response) if isinstance(response, (dict, list, str)) else str(response),
            datetime.now().isoformat(),
        )

        judge_payload: dict[str, Any] = {}
        failures_weaker: list[str] = []
        differentiation_achieved = False

        try:
            if isinstance(response, dict) and "error" not in response:
                candidate = dict(response)

                diff_val = candidate.get("differentiation_achieved")
                if isinstance(diff_val, str):
                    differentiation_achieved = diff_val.strip().lower() in {
                        "yes",
                        "true",
                        "1",
                    }
                elif isinstance(diff_val, bool):
                    differentiation_achieved = diff_val
                else:
                    differentiation_achieved = False
                candidate["differentiation_achieved"] = differentiation_achieved

                failures_raw = candidate.get("failures_weaker", [])
                if isinstance(failures_raw, list):
                    failures_weaker = [
                        str(item).strip()
                        for item in failures_raw
                        if isinstance(item, (str, int, float)) and str(item).strip()
                    ]
                else:
                    failures_weaker = []

                judge_payload = candidate
                step.success = True
                step.response = json.dumps(judge_payload)
            else:
                step.success = False
        except Exception:
            step.success = False
            judge_payload = {}
            failures_weaker = []

        # Calculate rewards
        catalog_names = [
            str((entry or {}).get("mistake", "")).strip() for entry in (error_catalog or []) if isinstance(entry, dict)
        ]
        reward_report = rewards_step6(judge_payload if step.success else {}, catalog_names, haiku_response)

        return (
            differentiation_achieved,
            judge_payload,
            failures_weaker,
            step,
            reward_report,
        )

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
