import json
import sqlite3
from pathlib import Path
import sys

import pytest

# Ensure backend modules are importable
BACKEND_ROOT = Path(__file__).resolve().parents[3] / "minimal" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.append(str(BACKEND_ROOT))

from persistence.repo import Repo  # noqa: E402


def test_repo_persistence_flow(tmp_path):
    db_path = tmp_path / "pipeline_test.db"
    repo = Repo(db_url=str(db_path))

    run_timestamp = "2024-01-01T00:00:00Z"
    topic = "Unit Testing"
    repo.mark_run_start(run_timestamp, topic)

    repo.save_step(
        run_timestamp=run_timestamp,
        topic=topic,
        step_number=1,
        step_name="kickoff",
        model_used="mock-model",
        success=True,
        response="Sample pipeline response",
        timestamp="2024-01-01T00:01:00Z",
    )

    repo.save_rewards(
        run_timestamp=run_timestamp,
        step_number=1,
        pass_rate=0.75,
        details=[{"case": "A", "passed": True}, {"case": "B", "passed": False}],
    )

    repo.mark_run_end(
        run_timestamp=run_timestamp,
        total_steps=7,
        differentiation_achieved=True,
        final_success=False,
    )

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute(
        "SELECT topic, total_steps, differentiation_achieved, final_success FROM enhanced_pipeline_runs WHERE run_timestamp = ?",
        (run_timestamp,),
    )
    run_row = cursor.fetchone()
    assert run_row == (
        topic,
        7,
        1,  # SQLite stores booleans as integers
        0,
    )

    cursor.execute(
        "SELECT step_number, step_name, model_used, success, response_length FROM enhanced_step_responses WHERE run_timestamp = ?",
        (run_timestamp,),
    )
    step_row = cursor.fetchone()
    assert step_row == (
        1,
        "kickoff",
        "mock-model",
        1,
        len("Sample pipeline response"),
    )

    cursor.execute(
        "SELECT pass_rate, num_tests, detail_json FROM step_rewards WHERE run_timestamp = ?",
        (run_timestamp,),
    )
    reward_row = cursor.fetchone()
    assert pytest.approx(reward_row[0]) == 0.75
    assert reward_row[1] == 2
    assert json.loads(reward_row[2]) == [
        {"case": "A", "passed": True},
        {"case": "B", "passed": False},
    ]

    conn.close()
