import os
from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class ModelRole:
    id: str
    name: str        # 'judge' | 'mid-tier' | 'weak-tier'
    supports_thinking: bool = False

def load_model_roles() -> Dict[str, ModelRole]:
    return {
        "judge": ModelRole(
            id=os.getenv("AQU_MODEL_JUDGE_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0"),
            name="judge",
            supports_thinking=os.getenv("AQU_MODEL_JUDGE_SUPPORTS_THINKING", "1") == "1",
        ),
        "mid": ModelRole(
            id=os.getenv("AQU_MODEL_MID_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0"),
            name="mid-tier",
        ),
        "weak": ModelRole(
            id=os.getenv("AQU_MODEL_WEAK_ID", "anthropic.claude-3-haiku-20240307-v1:0"),
            name="weak-tier",
        ),
    }
