import json
import sqlite3
from typing import Any


class Repo:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS enhanced_pipeline_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_timestamp TEXT NOT NULL UNIQUE,
            topic TEXT NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            total_steps INTEGER,
            differentiation_achieved BOOLEAN,
            final_success BOOLEAN
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS enhanced_step_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_timestamp TEXT NOT NULL,
            topic TEXT NOT NULL,
            step_number INTEGER NOT NULL,
            step_name TEXT NOT NULL,
            model_used TEXT NOT NULL,
            success BOOLEAN NOT NULL,
            response_length INTEGER NOT NULL,
            full_response TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS step_rewards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_timestamp TEXT NOT NULL,
            step_number INTEGER NOT NULL,
            pass_rate REAL NOT NULL,
            num_tests INTEGER NOT NULL,
            detail_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
        conn.close()

    def save_step(self, run_ts: str, topic: str, step: int, step_name: str,
                  model_used: str, success: bool, response: str, timestamp: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
        INSERT INTO enhanced_step_responses
        (run_timestamp, topic, step_number, step_name, model_used, success,
         response_length, full_response, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (run_ts, topic, step, step_name, model_used, int(bool(success)), len(response or ""), response or "", timestamp))
        conn.commit()
        conn.close()

    def save_rewards(self, run_ts: str, step: int, pass_rate: float, details: list[dict[str, Any]]):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
        INSERT INTO step_rewards (run_timestamp, step_number, pass_rate, num_tests, detail_json)
        VALUES (?, ?, ?, ?, ?)
        """, (run_ts, step, float(pass_rate), len(details), json.dumps(details)))
        conn.commit()
        conn.close()

    def mark_run_start(self, run_ts: str, topic: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
        INSERT OR IGNORE INTO enhanced_pipeline_runs (run_timestamp, topic)
        VALUES (?, ?)
        """, (run_ts, topic))
        conn.commit()
        conn.close()

    def mark_run_end(self, run_ts: str, total_steps: int, differentiation_achieved: bool, final_success: bool):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
        UPDATE enhanced_pipeline_runs
        SET completed_at = CURRENT_TIMESTAMP, total_steps = ?, differentiation_achieved = ?, final_success = ?
        WHERE run_timestamp = ?
        """, (int(total_steps), int(bool(differentiation_achieved)), int(bool(final_success)), run_ts))
        conn.commit()
        conn.close()
