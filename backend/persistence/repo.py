import json
import psycopg2
from typing import Any, Dict, List


class Repo:
    def __init__(self, db_uri: str):
        self.db_uri = db_uri

    def save_step(
        self,
        run_timestamp: str,
        topic: str,
        step_number: int,
        step_name: str,
        model_used: str,
        success: bool,
        response: str,
        timestamp: str,
    ) -> None:
        with psycopg2.connect(self.db_uri) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO enhanced_step_responses
                    (run_timestamp, topic, step_number, step_name, model_used, success,
                     response_length, full_response, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        run_timestamp,
                        topic,
                        step_number,
                        step_name,
                        model_used,
                        success,
                        len(response or ""),
                        response or "",
                        timestamp,
                    ),
                )

    def save_rewards(
        self,
        run_timestamp: str,
        step_number: int,
        pass_rate: float,
        details: List[Dict[str, Any]],
    ) -> None:
        with psycopg2.connect(self.db_uri) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO step_rewards (run_timestamp, step_number, pass_rate, num_tests, detail_json)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        run_timestamp,
                        step_number,
                        pass_rate,
                        len(details),
                        json.dumps(details),
                    ),
                )

    def mark_run_start(self, run_timestamp: str, topic: str) -> None:
        with psycopg2.connect(self.db_uri) as conn:
            with conn.cursor() as cursor:
                # Use ON CONFLICT DO NOTHING for PostgreSQL compatibility
                cursor.execute(
                    """
                    INSERT INTO enhanced_pipeline_runs (run_timestamp, topic)
                    VALUES (%s, %s)
                    ON CONFLICT (run_timestamp) DO NOTHING
                    """,
                    (run_timestamp, topic),
                )

    def mark_run_end(
        self,
        run_timestamp: str,
        total_steps: int,
        differentiation_achieved: bool,
        final_success: bool,
    ) -> None:
        with psycopg2.connect(self.db_uri) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE enhanced_pipeline_runs
                    SET
                        completed_at = CURRENT_TIMESTAMP,
                        total_steps = %s,
                        differentiation_achieved = %s,
                        final_success = %s
                    WHERE run_timestamp = %s
                    """,
                    (
                        total_steps,
                        differentiation_achieved,
                        final_success,
                        run_timestamp,
                    ),
                )
