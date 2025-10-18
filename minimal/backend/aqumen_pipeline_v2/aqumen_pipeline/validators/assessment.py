import re
from typing import Any

from ..config import ALLOWED_DIFFICULTIES, MAX_CODE_LINES, MAX_ERROR_SPAN, MIN_CODE_LINES, MIN_ERROR_SPAN


def validate_assessment_payload(payload: dict[str, Any]) -> tuple[bool, dict[str, Any], list[str]]:
    """Deterministic checks for Step 7 output with small auto-fixes."""
    errors: list[str] = []
    if not isinstance(payload, dict):
        return False, {}, ["Model did not return a JSON object."]

    title = payload.get("title")
    if not isinstance(title, str) or not title.strip():
        errors.append("Title must be a non-empty string.")
    else:
        title = title.strip()

    difficulty = payload.get("difficulty")
    if not isinstance(difficulty, str) or difficulty not in ALLOWED_DIFFICULTIES:
        errors.append(f"Difficulty must be one of {sorted(ALLOWED_DIFFICULTIES)}.")

    # content (lines)
    lines = payload.get("content")
    if isinstance(lines, str):
        lines = [ln.rstrip("\r\n") for ln in lines.splitlines()]
    if not isinstance(lines, list) or not all(isinstance(ln, str) for ln in (lines or [])):
        errors.append("content must be an array of strings.")
        lines = []
    else:
        if not (MIN_CODE_LINES <= len(lines) <= MAX_CODE_LINES):
            errors.append(f"content must have {MIN_CODE_LINES}-{MAX_CODE_LINES} lines (found {len(lines)})." )

    # errors[]
    err_items = payload.get("errors")
    if not isinstance(err_items, list) or not all(isinstance(e, dict) for e in (err_items or [])):
        errors.append("errors must be an array of objects.")
        err_items = []

    joined = "\n".join(lines)
    spans = re.findall(r"<<([^<>]+)>>", joined)
    if not spans:
        errors.append("No << >> spans found in content.")

    if spans and err_items and len(spans) != len(err_items):
        errors.append(f"Number of spans ({len(spans)}) must equal number of errors ({len(err_items)})." )

    for ln in lines:
        if ln.count("<<") != ln.count(">>"):
            errors.append("Unbalanced << >> in a line.")

    sanitized_errors = []
    seen_ids = set()
    for i, e in enumerate(err_items):
        sid = e.get("id")
        desc = e.get("description")
        if not isinstance(sid, str) or not sid.strip():
            errors.append(f"Error #{i+1} missing 'id'.")
            continue
        sid = sid.strip()
        if sid in seen_ids:
            errors.append(f"Duplicate error id '{sid}'.")
        seen_ids.add(sid)
        if not (MIN_ERROR_SPAN <= len(sid) <= MAX_ERROR_SPAN):
            errors.append(f"Error id '{sid}' length must be {MIN_ERROR_SPAN}-{MAX_ERROR_SPAN} (found {len(sid)})." )
        if joined.count(f"<<{sid}>>") != 1:
            errors.append(f"Error id '{sid}' must appear exactly once in content.")
        if not isinstance(desc, str) or not desc.strip():
            errors.append(f"Error '{sid}' missing description.")
        else:
            d2 = desc.strip()
            if len(d2) > 180:
                errors.append(f"Description for '{sid}' too long ({len(d2)} chars)." )
            desc = d2
        sanitized_errors.append({"id": sid, "description": desc})

    if errors:
        return False, {}, errors

    sanitized = {
        "title": title,
        "difficulty": difficulty,
        "content": [ln.rstrip("\r\n") for ln in lines],
        "errors": sanitized_errors
    }
    if isinstance(payload.get("content_type"), str):
        sanitized["content_type"] = payload["content_type"]
    return True, sanitized, []
