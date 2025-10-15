import json
import re
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

class AssessmentValidator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.allowed_difficulties = set(config.get('allowed_difficulties', []))
        self.min_code_lines = config.get('min_code_lines', 24)
        self.max_code_lines = config.get('max_code_lines', 60)
        self.min_errors = config.get('min_errors', 1)
        self.max_errors = config.get('max_errors', 5)
        self.min_error_span = config.get('min_error_span', 20)
        self.max_error_span = config.get('max_error_span', 120)

    def validate(self, payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        Runs deterministic checks to ensure Step 7 output matches frontend expectations.
        Returns a tuple of (is_valid, sanitized_payload, errors).
        """
        errors: List[str] = []

        if not isinstance(payload, dict):
            return False, {}, ["Model did not return a JSON object."]

        # Validate and sanitize title
        title = payload.get("title")
        if not isinstance(title, str) or not title.strip():
            errors.append("Title must be a non-empty string.")
        else:
            title = title.strip()

        # Validate difficulty
        difficulty = payload.get("difficulty")
        if not isinstance(difficulty, str) or difficulty not in self.allowed_difficulties:
            errors.append(f"Difficulty must be one of {sorted(self.allowed_difficulties)}.")

        # Validate and determine content_type
        allowed_content_types = {"code", "prose", "math", "email", "table", "diagram", "plan", "pseudo", "query", "other"}
        content_type = payload.get("content_type")
        if not isinstance(content_type, str):
            if isinstance(payload.get("code"), list):
                content_type = "code" # Auto-detect for back-compat
            else:
                errors.append("content_type must be provided and be one of the supported modalities.")
                content_type = "code" # Default to avoid downstream errors

        content_type = content_type.strip().lower()
        if content_type not in allowed_content_types:
            errors.append(f"content_type must be one of {sorted(allowed_content_types)}.")

        # Validate and sanitize content lines
        content_lines = payload.get("content")
        if content_lines is None:
            content_lines = payload.get("code") # Backward compatibility

        if isinstance(content_lines, str):
            try:
                parsed = json.loads(content_lines)
                if isinstance(parsed, list) and all(isinstance(line, str) for line in parsed):
                    content_lines = parsed
                    logger.warning(f"Step 7 auto-fix: Converted stringified content to native JSON array.")
                else:
                    content_lines = content_lines.splitlines()
            except (json.JSONDecodeError, TypeError):
                content_lines = content_lines.splitlines()

        if not isinstance(content_lines, list) or not all(isinstance(line, str) for line in content_lines):
            errors.append("`content` must be an array of strings.")
            content_lines = []
        else:
            content_lines = [line.rstrip("\r\n") for line in content_lines]
            if not (self.min_code_lines <= len(content_lines) <= self.max_code_lines):
                errors.append(f"`content` must contain between {self.min_code_lines} and {self.max_code_lines} lines (found {len(content_lines)}).")

        # Validate errors list
        errors_list = payload.get("errors")
        if not isinstance(errors_list, list) or not all(isinstance(item, dict) for item in (errors_list or [])):
            errors.append("`errors` must be an array of objects.")
            errors_list = []

        if errors_list and not (self.min_errors <= len(errors_list) <= self.max_errors):
            errors.append(f"`errors` array must contain between {self.min_errors} and {self.max_errors} entries (found {len(errors_list)}).")

        joined_content = "\n".join(content_lines)
        marked_spans = re.findall(r"<<([^<>]+)>>", joined_content)

        if not marked_spans:
            errors.append("No <<...>> error spans were found in the `content`.")

        if joined_content.count("<<") != joined_content.count(">>"):
            errors.append("Unbalanced number of << and >> delimiters in the `content`.")

        # Validate individual errors and their relation to content
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

            if not (self.min_error_span <= len(error_id) <= self.max_error_span):
                errors.append(f"Error id '{error_id}' must be between {self.min_error_span} and {self.max_error_span} characters (found {len(error_id)}).")

            occurrences = joined_content.count(f"<<{error_id}>>")
            if occurrences != 1:
                errors.append(f"Error id '{error_id}' must appear exactly once in the `content`; found {occurrences}.")

            if error_id not in marked_spans:
                errors.append(f"Error id '{error_id}' is not wrapped in <<...>> within the `content`.")

            if not isinstance(description, str) or not description.strip():
                errors.append(f"Error id '{error_id}' is missing a description.")
            else:
                desc = description.strip()
                if len(desc) > 180:
                    errors.append(f"Error description for id '{error_id}' is too long ({len(desc)} chars, max 180).")
                description = desc

            sanitized_errors.append({"id": error_id, "description": description})

        if marked_spans and errors_list and len(marked_spans) != len(errors_list):
            errors.append(f"Number of marked spans ({len(marked_spans)}) does not match number of error entries ({len(errors_list)}).")

        if errors:
            return False, {}, errors

        # If all checks pass, build the sanitized payload
        sanitized_payload = {
            "title": title,
            "difficulty": difficulty,
            "content_type": content_type,
            "content": content_lines,
            "code": content_lines,  # For backward compatibility
            "errors": sanitized_errors
        }

        return True, sanitized_payload, []