"""Step 7: Create student assessment based on weak model failures."""

import json
import logging
from datetime import datetime
from typing import Any, Optional

from analytics.rewards import StepRewardsReport, rewards_step7
from legacy_pipeline.config import PipelineConfig
from legacy_pipeline.models import PipelineStep
from legacy_pipeline.validators.assessment_validator import AssessmentValidator

logger = logging.getLogger(__name__)


class AssessmentStep:
    """Handles Step 7: Create student assessment from weak model failures."""

    def __init__(
        self,
        invoker,
        model_strong: str,
        prompts: dict,
        tools: dict,
        judge_supports_thinking: bool = False,
        config: Optional[PipelineConfig] = None,
    ):
        """
        Initialize the assessment creation step.

        Args:
            invoker: Model invocation service
            model_strong: Strong model ID to use
            prompts: Prompt templates dictionary
            tools: Tool specifications dictionary
            judge_supports_thinking: Whether the model supports thinking mode
            config: Pipeline configuration (uses default if None)
        """
        self.invoker = invoker
        self.model_strong = model_strong
        self.prompts = prompts
        self.tools = tools
        self.judge_supports_thinking = judge_supports_thinking
        self.config = config or PipelineConfig()
        self.validator = AssessmentValidator(self.config)

    def execute(
        self,
        question: dict,
        sonnet_response: str,
        haiku_response: str,
        haiku_failures: list[str],
    ) -> tuple[bool, dict, PipelineStep, Optional[StepRewardsReport]]:
        """
        Execute Step 7: Create student assessment with error spans.

        Args:
            question: The question from Step 3
            sonnet_response: Mid-tier model response
            haiku_response: Weak-tier model response
            haiku_failures: Actual weak model failures identified in Step 6

        Returns:
            Tuple of (success, assessment_dict, pipeline_step, rewards_report)
        """
        logger.info("Step 7: Creating student assessment from weak model failures")

        topic = question.get("context", "AI/ML implementation")
        subtopic = question.get("title", "Implementation Challenge")

        validation_feedback: Optional[list[str]] = None
        last_step: Optional[PipelineStep] = None

        for attempt in range(1, self.config.STEP7_MAX_ATTEMPTS + 1):
            prompt, tools = self._build_step7_prompt(
                topic=topic,
                subtopic=subtopic,
                haiku_failures=haiku_failures,
                haiku_response=haiku_response,
                sonnet_response=sonnet_response,
                validation_feedback=validation_feedback,
            )

            use_thinking = attempt > 1 and self.judge_supports_thinking
            response = self.invoker.tools(
                self.model_strong,
                prompt,
                tools,
                use_thinking=use_thinking,
            )
            step = PipelineStep(
                7,
                f"Create student assessment from weak model failures (attempt {attempt})",
                self.model_strong,
                False,
                json.dumps(response)
                if isinstance(response, (dict, list, str))
                else str(response),
                datetime.now().isoformat(),
            )

            validation_feedback = []

            if not isinstance(response, dict) or "error" in response:
                validation_feedback.append(
                    "The model did not return valid structured output via the student_assessment_tool."
                )
                step.response = json.dumps(
                    {"model_response": response, "validation_errors": validation_feedback}
                )
                payload = response if isinstance(response, dict) else {}
                reward_report = rewards_step7(payload)
                last_step = step
                continue

            # Validate the response
            is_valid, sanitized_payload, validation_errors = (
                self.validator.validate_assessment(response)
            )

            if is_valid:
                step.success = True
                step.response = json.dumps(sanitized_payload)
                reward_report = rewards_step7(sanitized_payload)
                return True, sanitized_payload, step, reward_report

            # Failed validation - prepare feedback for retry
            validation_feedback = validation_errors
            step.response = json.dumps(
                {"model_response": response, "validation_errors": validation_errors}
            )
            reward_report = rewards_step7(response)
            last_step = step

        # If we exhaust retries, return failure with the last logged step
        if last_step is None:
            last_step = PipelineStep(
                7,
                "Create student assessment from weak model failures",
                self.model_strong,
                False,
                json.dumps(
                    {
                        "validation_errors": validation_feedback
                        or ["Unknown Step 7 failure."]
                    }
                ),
                datetime.now().isoformat(),
            )
        
        reward_report = rewards_step7({})
        return False, {}, last_step, reward_report

    def _build_step7_prompt(
        self,
        topic: str,
        subtopic: str,
        haiku_failures: list[str],
        haiku_response: str,
        sonnet_response: str,
        validation_feedback: Optional[list[str]] = None,
    ) -> tuple[str, list[dict[str, Any]]]:
        """
        Compose the Step 7 prompt (optionally injecting feedback from validation failures).

        Args:
            topic: Main topic
            subtopic: Specific subtopic
            haiku_failures: List of failures from weak model
            haiku_response: Weak model response text
            sonnet_response: Mid-tier model response text
            validation_feedback: Validation errors from previous attempt

        Returns:
            Tuple of (formatted_prompt, tools_list)
        """
        validation_block = ""
        if validation_feedback:
            feedback_lines = "\n".join(f"- {issue}" for issue in validation_feedback)
            validation_block = (
                "\n\nVALIDATION FEEDBACK FROM THE LAST ATTEMPT:\n"
                "Fix every issue below before returning the next result:\n"
                f"{feedback_lines}\n"
            )

        template = self._get_prompt_template("step7_student_assessment")
        prompt = template.format(
            haiku_failures="\n".join(f"- {failure}" for failure in haiku_failures),
            haiku_response_preview=haiku_response[:2000],
            sonnet_response_preview=sonnet_response[:1000],
            min_code_lines=self.config.MIN_CODE_LINES,
            max_code_lines=self.config.MAX_CODE_LINES,
            min_error_span=self.config.MIN_ERROR_SPAN,
            max_error_span=self.config.MAX_ERROR_SPAN,
            min_errors=self.config.MIN_ERRORS,
            max_errors=self.config.MAX_ERRORS,
            allowed_difficulties=", ".join(sorted(self.config.ALLOWED_DIFFICULTIES)),
            topic=topic,
            subtopic=subtopic,
            validation_feedback=validation_block,
        )

        tools = self._get_tools("step7_student_assessment")
        if tools:
            difficulty_schema = (
                tools[0]
                .get("input_schema", {})
                .get("properties", {})
                .get("difficulty")
            )
            if isinstance(difficulty_schema, dict):
                difficulty_schema["enum"] = sorted(self.config.ALLOWED_DIFFICULTIES)

        return prompt, tools

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
