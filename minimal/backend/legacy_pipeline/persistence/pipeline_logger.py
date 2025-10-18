"""Pipeline logging and persistence utilities."""

import json
import logging
import os
from datetime import datetime
from typing import Any

from analytics.rewards import StepRewardsReport
from legacy_pipeline.models import PipelineStep, SevenStepResult
from persistence.repo import Repo

logger = logging.getLogger(__name__)


class PipelineLogger:
    """Handles logging and database persistence for pipeline execution."""

    def __init__(self, script_dir: str, run_timestamp: str, db_path: str):
        """
        Initialize the pipeline logger.

        Args:
            script_dir: Base directory for log files and results
            run_timestamp: Timestamp identifier for this run
            db_path: Path to SQLite database
        """
        self.script_dir = script_dir
        self.run_timestamp = run_timestamp
        self.db_path = db_path
        self.repo = Repo(db_path)

        # Set up log and results paths
        log_dir = os.path.join(script_dir, "logs", "current")
        self.log_file = os.path.join(log_dir, f"pipeline_run_{run_timestamp}.txt")
        self.results_file = os.path.join(script_dir, f"corrected_7step_results_{run_timestamp}.json")

        # Ensure directories exist
        os.makedirs(log_dir, exist_ok=True)
        os.makedirs(os.path.join(script_dir, "logs", "archived"), exist_ok=True)
        os.makedirs(os.path.join(script_dir, "results"), exist_ok=True)

        self.current_topic: str | None = None

    def initialize_run(self, topic: str) -> None:
        """
        Initialize a new pipeline run with header information.

        Args:
            topic: The topic for this pipeline run
        """
        self.current_topic = topic

        with open(self.log_file, "w") as f:
            f.write(f"Pipeline Run Started: {datetime.now()}\n")
            f.write(f"Run ID: {self.run_timestamp}\n")
            f.write(f"Topic: {topic}\n")
            f.write("=" * 80 + "\n")

        # Mark run start in database
        self.repo.mark_run_start(self.run_timestamp, topic)

    def log_step(self, step: PipelineStep) -> None:
        """
        Log a pipeline step to both file and database.

        Args:
            step: The pipeline step to log
        """
        # Log to timestamped file
        with open(self.log_file, "a") as f:
            f.write(f"\n{'=' * 80}\n")
            f.write(f"STEP {step.step_number}: {step.step_name}\n")
            f.write(f"MODEL: {step.model_used}\n")
            f.write(f"TIMESTAMP: {step.timestamp}\n")
            f.write(f"SUCCESS: {step.success}\n")
            f.write(f"RESPONSE:\n{step.response}\n")

        # Log to database
        self.repo.save_step(
            self.run_timestamp,
            self.current_topic or "Unknown",
            step.step_number,
            step.step_name,
            step.model_used,
            step.success,
            step.response,
            step.timestamp,
        )

    def log_step_reward(self, step_number: int, report: StepRewardsReport | None) -> None:
        """
        Log step reward metrics to file and database.

        Args:
            step_number: The step number
            report: The rewards report (None if not available)
        """
        if report is None:
            return

        details = [
            {
                "name": result.name,
                "passed": bool(result.passed),
                "detail": result.detail,
            }
            for result in report.results
        ]

        # Save to metrics JSON file
        metrics_path = os.path.join(self.script_dir, "results", f"metrics_{self.run_timestamp}.json")
        if os.path.exists(metrics_path):
            with open(metrics_path, encoding="utf-8") as f:
                metrics = json.load(f)
        else:
            metrics = {"run_timestamp": self.run_timestamp, "steps": {}}

        metrics["steps"][str(step_number)] = {
            "pass_rate": report.pass_rate,
            "results": details,
        }

        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        # Save to database
        self._save_reward_to_database(step_number, report)

    def finalize_run(
        self,
        final_result: SevenStepResult,
        assessment: dict[str, Any] | None = None,
    ) -> None:
        """
        Write final result to file and update database.

        Args:
            final_result: The final pipeline result
            assessment: Optional assessment data from Step 7
        """
        steps_data = []
        for step in final_result.steps_completed:
            steps_data.append(
                {
                    "step_number": step.step_number,
                    "step_name": step.step_name,
                    "model_used": step.model_used,
                    "success": bool(step.success),
                    "timestamp": step.timestamp,
                    "response": step.response,
                }
            )

        payload: dict[str, Any] = {
            "run_timestamp": self.run_timestamp,
            "topic": final_result.topic,
            "subtopic": final_result.subtopic,
            "difficulty": final_result.difficulty,
            "final_success": bool(final_result.final_success),
            "stopped_at_step": final_result.stopped_at_step,
            "differentiation_achieved": bool(final_result.differentiation_achieved),
            "student_assessment_created": bool(final_result.student_assessment_created),
            "total_attempts": final_result.total_attempts,
            "weak_model_failures": final_result.weak_model_failures,
            "steps": steps_data,
            "generated_at": datetime.now().isoformat(),
        }

        if assessment is not None:
            payload["assessment"] = assessment

        try:
            with open(self.results_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception as exc:
            logger.warning("Failed to write final result artifact: %s", exc)

        # Update database
        self.repo.mark_run_end(
            self.run_timestamp,
            total_steps=len(final_result.steps_completed),
            differentiation_achieved=final_result.differentiation_achieved,
            final_success=final_result.final_success,
        )

    def _save_reward_to_database(self, step_number: int, report: StepRewardsReport) -> None:
        """Save reward metrics to database."""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        details = [
            {
                "name": result.name,
                "passed": bool(result.passed),
                "detail": result.detail,
            }
            for result in report.results
        ]
        cursor.execute(
            """
            INSERT INTO step_rewards (run_timestamp, step_number, pass_rate, num_tests, detail_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                self.run_timestamp,
                step_number,
                float(report.pass_rate),
                len(details),
                json.dumps(details),
            ),
        )
        conn.commit()
        conn.close()
