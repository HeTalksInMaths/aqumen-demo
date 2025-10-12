"""
Utilities for loading pipeline prompt templates with UI-managed overrides.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_FILE = BASE_DIR / "prompts.json"
PROMPTS_CHANGES_FILE = BASE_DIR / "prompts_changes.json"


def _load_json(path: Path, *, allow_missing: bool = False) -> Dict[str, Any]:
    """
    Load a JSON file from disk.

    Returns an empty dict when allow_missing=True and the file is absent.
    Raises on decode errors so callers are aware of invalid JSON.
    """
    if not path.exists():
        if allow_missing:
            return {}
        raise FileNotFoundError(f"Required configuration file not found: {path}")

    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    if not isinstance(data, dict):
        raise ValueError(f"Configuration file must contain a JSON object: {path}")

    return data


def merge_prompt_changes(
    base_prompts: Dict[str, Dict[str, Any]],
    overrides: Dict[str, Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    """
    Merge UI overrides into the base prompt configuration.

    Overrides replace the matching keys from the base definition while keeping any
    untouched metadata so downstream callers always see a complete prompt entry.
    """
    merged: Dict[str, Dict[str, Any]] = {}

    for key, value in base_prompts.items():
        merged[key] = deepcopy(value) if isinstance(value, dict) else value

    for step, override in overrides.items():
        if step.startswith("_"):
            continue  # metadata entries

        if not isinstance(override, dict):
            merged[step] = deepcopy(override)
            continue

        base_entry = merged.get(step, {})
        if isinstance(base_entry, dict):
            merged_entry = deepcopy(base_entry)
            merged_entry.update({k: deepcopy(v) for k, v in override.items()})
        else:
            merged_entry = deepcopy(override)

        merged[step] = merged_entry

    return merged


def load_prompts(
    *,
    prompts_path: Path | None = None,
    overrides_path: Path | None = None
) -> Dict[str, Dict[str, Any]]:
    """
    Load prompt templates, applying any overrides saved by the Dev Mode UI.
    """
    prompts_file = prompts_path or PROMPTS_FILE
    overrides_file = overrides_path or PROMPTS_CHANGES_FILE

    base = _load_json(prompts_file, allow_missing=False)
    overrides = _load_json(overrides_file, allow_missing=True)

    return merge_prompt_changes(base, overrides)
