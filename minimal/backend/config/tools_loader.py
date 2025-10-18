"""
Utilities for loading pipeline tool specifications with UI-managed overrides.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
TOOLS_FILE = BASE_DIR / "tools.json"
TOOLS_CHANGES_FILE = BASE_DIR / "tools_changes.json"


def _load_json(path: Path, *, allow_missing: bool = False) -> dict[str, Any]:
    """
    Load a JSON configuration file, returning {} when missing and allowed.
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


def merge_tool_changes(
    base_tools: dict[str, Any],
    overrides: dict[str, Any]
) -> dict[str, Any]:
    """
    Merge override entries into the base tool specification.
    """
    merged: dict[str, Any] = {}

    for key, value in base_tools.items():
        merged[key] = deepcopy(value)

    for step, override in overrides.items():
        if step.startswith("_"):
            continue

        if isinstance(override, dict):
            base_entry = merged.get(step, {})
            if isinstance(base_entry, dict):
                merged_entry = deepcopy(base_entry)
                merged_entry.update({k: deepcopy(v) for k, v in override.items()})
                merged[step] = merged_entry
            else:
                merged[step] = deepcopy(override)
        else:
            merged[step] = deepcopy(override)

    return merged


def load_tools(
    *,
    tools_path: Path | None = None,
    overrides_path: Path | None = None
) -> dict[str, Any]:
    """
    Load tool definitions with overrides applied.
    """
    tools_file = tools_path or TOOLS_FILE
    overrides_file = overrides_path or TOOLS_CHANGES_FILE

    base = _load_json(tools_file, allow_missing=False)
    overrides = _load_json(overrides_file, allow_missing=True)

    return merge_tool_changes(base, overrides)
