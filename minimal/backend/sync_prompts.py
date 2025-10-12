#!/usr/bin/env python3
"""
Prompt configuration helper for managing base templates and UI overrides.

Usage:
    python sync_prompts.py --extract   # Snapshot merged prompts (base + overrides)
    python sync_prompts.py --apply     # Merge prompts_changes.json overrides into prompts.json
    python sync_prompts.py --diff      # Show differences between base prompts and overrides
"""

import argparse
import difflib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from config import load_prompts, merge_prompt_changes

JSON_FILE = Path(__file__).parent / "prompts.json"
PROMPTS_CHANGES_FILE = Path(__file__).parent / "prompts_changes.json"


def _load_json_file(path: Path, *, allow_missing: bool = False) -> Dict[str, Any]:
    """Load a JSON object from disk."""
    if not path.exists():
        if allow_missing:
            return {}
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")

    return data


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    """Persist a JSON object to disk."""
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def extract_prompts_from_python() -> None:
    """
    Snapshot the merged prompt configuration to a timestamped JSON file.

    Useful for reviewing the exact templates the pipeline will use.
    """
    prompts = load_prompts()
    snapshot_path = JSON_FILE.with_name(f"prompts_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    _write_json(snapshot_path, prompts)
    print(f"📝 Snapshot saved to {snapshot_path}")


def apply_prompts_to_python() -> None:
    """
    Merge overrides into prompts.json and clear the applied entries.
    """
    print(f"📖 Loading base prompts from {JSON_FILE}")
    base_prompts = _load_json_file(JSON_FILE)

    print(f"📖 Loading overrides from {PROMPTS_CHANGES_FILE}")
    overrides = _load_json_file(PROMPTS_CHANGES_FILE, allow_missing=True)

    merged = merge_prompt_changes(base_prompts, overrides)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = JSON_FILE.with_suffix(f".json.backup.{timestamp}")

    print(f"💾 Writing backup of base prompts to {backup_path}")
    _write_json(backup_path, base_prompts)

    print(f"💾 Writing merged prompts to {JSON_FILE}")
    _write_json(JSON_FILE, merged)

    # Preserve metadata while clearing applied overrides
    meta = overrides.get("_meta")
    if not isinstance(meta, dict):
        meta = {"description": "UI-managed prompt overrides merged on top of prompts.json."}
    meta["last_applied"] = datetime.now().isoformat()

    cleaned_overrides: Dict[str, Any] = {"_meta": meta}

    print(f"🧹 Clearing applied overrides in {PROMPTS_CHANGES_FILE}")
    _write_json(PROMPTS_CHANGES_FILE, cleaned_overrides)

    print("✅ Overrides merged successfully.")


def show_diff() -> None:
    """
    Display differences between base prompts and overrides.
    """
    base_prompts = _load_json_file(JSON_FILE, allow_missing=True)
    overrides = _load_json_file(PROMPTS_CHANGES_FILE, allow_missing=True)

    override_steps = [k for k in overrides.keys() if not k.startswith("_")]
    if not override_steps:
        print("✅ No overrides found in prompts_changes.json")
        return

    merged = merge_prompt_changes(base_prompts, overrides)

    for step in sorted(merged.keys()):
        if step.startswith("_"):
            continue

        base_entry = base_prompts.get(step, {})
        merged_entry = merged.get(step, {})

        base_template = base_entry.get("template") if isinstance(base_entry, dict) else None
        merged_template = merged_entry.get("template") if isinstance(merged_entry, dict) else None

        if base_template == merged_template:
            continue

        print(f"\n🔄 Differences for {step}:")
        base_lines = (base_template or "").splitlines()
        merged_lines = (merged_template or "").splitlines()

        diff = difflib.unified_diff(
            base_lines,
            merged_lines,
            fromfile=f"{step} (base)",
            tofile=f"{step} (merged)",
            lineterm=""
        )

        has_diff = False
        for line in diff:
            has_diff = True
            print(line)

        if not has_diff:
            print("  (Only metadata differences)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage pipeline prompt templates and overrides.")
    parser.add_argument("--extract", action="store_true", help="Snapshot merged prompts to a timestamped file.")
    parser.add_argument("--apply", action="store_true", help="Merge overrides into prompts.json and clear them.")
    parser.add_argument("--diff", action="store_true", help="Show differences between base prompts and overrides.")

    args = parser.parse_args()

    if not any((args.extract, args.apply, args.diff)):
        parser.print_help()
        return

    if args.extract:
        extract_prompts_from_python()

    if args.apply:
        apply_prompts_to_python()

    if args.diff:
        show_diff()


if __name__ == "__main__":
    main()
