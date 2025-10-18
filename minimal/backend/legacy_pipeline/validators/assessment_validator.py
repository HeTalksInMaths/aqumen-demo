"""Validation logic for Step 7 student assessments."""

import json
import logging
import re
from typing import Any

from legacy_pipeline.config import PipelineConfig

logger = logging.getLogger(__name__)


class AssessmentValidator:
    """Validates Step 7 assessment payloads against frontend expectations."""

    def __init__(self, config: PipelineConfig):
        """
        Initialize the validator with pipeline configuration.

        Args:
            config: Pipeline configuration containing validation thresholds
        """
        self.config = config

    def validate_assessment(self, payload: dict[str, Any]) -> tuple[bool, dict[str, Any], list[str]]:
        """
        Run deterministic checks to ensure Step 7 output matches frontend expectations.

        Args:
            payload: The assessment payload from the model

        Returns:
            Tuple of (is_valid, sanitized_payload, error_messages)
        """
        errors: list[str] = []

        if not isinstance(payload, dict):
            return False, {}, ["Model did not return a JSON object."]

        # Validate title
        title = payload.get("title")
        if not isinstance(title, str) or not title.strip():
            errors.append("Title must be a non-empty string.")
        else:
            title = title.strip()

        # Validate difficulty
        difficulty = payload.get("difficulty")
        if not isinstance(difficulty, str) or difficulty not in self.config.ALLOWED_DIFFICULTIES:
            errors.append(f"Difficulty must be one of {sorted(self.config.ALLOWED_DIFFICULTIES)}.")

        # Validate content_type
        content_type = payload.get("content_type")
        if not isinstance(content_type, str):
            if isinstance(payload.get("code"), list):
                content_type = "code"
            else:
                errors.append("content_type must be provided and be one of the supported modalities.")
                content_type = "code"
        content_type = content_type.strip().lower()
        if content_type not in self.config.ALLOWED_CONTENT_TYPES:
            errors.append(f"content_type must be one of {sorted(self.config.ALLOWED_CONTENT_TYPES)}.")

        # Validate content/code array
        content_lines = payload.get("content")
        if content_lines is None:
            content_lines = payload.get("code")

        if isinstance(content_lines, str):
            try:
                parsed = json.loads(content_lines)
                if isinstance(parsed, list) and all(isinstance(line, str) for line in parsed):
                    content_lines = parsed
                    logger.warning(
                        f"Step 7 auto-fix: Converted stringified array to native JSON array ({len(parsed)} lines)"
                    )
                else:
                    # content_lines is a string, split it
                    content_lines = str(content_lines).splitlines()
            except (json.JSONDecodeError, TypeError):
                # content_lines is a string, split it
                content_lines = str(content_lines).splitlines()

        if not isinstance(content_lines, list) or not all(isinstance(line, str) for line in content_lines):
            errors.append("content must be an array of strings.")
            content_lines = []
        else:
            content_lines = [line.rstrip("\r\n") for line in content_lines]
            if not (self.config.MIN_CODE_LINES <= len(content_lines) <= self.config.MAX_CODE_LINES):
                errors.append(
                    f"content must contain between {self.config.MIN_CODE_LINES} and "
                    f"{self.config.MAX_CODE_LINES} lines (found {len(content_lines)})."
                )

        # Validate errors array
        errors_list = payload.get("errors")
        if not isinstance(errors_list, list) or not all(isinstance(item, dict) for item in (errors_list or [])):
            errors.append("Errors must be an array of objects.")
            errors_list = []

        if errors_list and not (self.config.MIN_ERRORS <= len(errors_list) <= self.config.MAX_ERRORS):
            errors.append(
                f"Errors array must contain between {self.config.MIN_ERRORS} and "
                f"{self.config.MAX_ERRORS} entries (found {len(errors_list)})."
            )

        # Validate error spans in content
        joined_content = "\n".join(content_lines)
        marked_spans = re.findall(r"<<([^<>]+)>>", joined_content)

        if not marked_spans:
            errors.append("No << >> error spans were found in the content.")

        # Ensure raw delimiter counts are balanced
        if joined_content.count("<<") != joined_content.count(">>"):
            errors.append("Unbalanced number of << and >> delimiters in the content.")

        # Validate individual error entries
        sanitized_errors = []
        seen_ids = set()

        for idx, error_entry in enumerate(errors_list):
            error_id = error_entry.get("id")
            description = error_entry.get("description")

            if not isinstance(error_id, str) or not error_id.strip():
                errors.append(f"Error #{idx + 1} is missing a valid 'id'.")
                continue

            error_id = error_id.strip()
            if error_id in seen_ids:
                errors.append(f"Error id '{error_id}' is duplicated.")
            else:
                seen_ids.add(error_id)

            if not (self.config.MIN_ERROR_SPAN <= len(error_id) <= self.config.MAX_ERROR_SPAN):
                errors.append(
                    f"Error id '{error_id}' must be between {self.config.MIN_ERROR_SPAN} and "
                    f"{self.config.MAX_ERROR_SPAN} characters (found {len(error_id)})."
                )

            occurrences = joined_content.count(f"<<{error_id}>>")
            if occurrences != 1:
                errors.append(f"Error id '{error_id}' must appear exactly once in the content; found {occurrences}.")

            if error_id not in marked_spans:
                errors.append(f"Error id '{error_id}' is not wrapped in << >> within the content.")

            if not isinstance(description, str) or not description.strip():
                errors.append(f"Error id '{error_id}' is missing a description.")
            else:
                desc = description.strip()
                if len(desc) > 180:
                    errors.append(f"Error description for id '{error_id}' is too long ({len(desc)} chars, max 180).")
                description = desc

            sanitized_errors.append({"id": error_id, "description": description})

        # Check span count matches error count
        if marked_spans and errors_list and len(marked_spans) != len(errors_list):
            errors.append(
                f"Number of marked spans ({len(marked_spans)}) does not match "
                f"number of error entries ({len(errors_list)})."
            )

        if errors:
            return False, {}, errors

        sanitized_payload = {
            "title": title,
            "difficulty": difficulty,
            "content_type": content_type,
            "content": content_lines,
            "code": content_lines,  # Backward compatibility
            "errors": sanitized_errors,
        }

        return True, sanitized_payload, []
