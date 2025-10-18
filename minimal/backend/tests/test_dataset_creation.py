import json
import sqlite3
import sys
import tempfile
from pathlib import Path
from unittest import TestCase, main

# Ensure the repository root is on the Python path when running as a script.
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from minimal.backend import create_new_datasets


class DatasetCreationTests(TestCase):
    """Exercises dataset generation against a temporary sqlite store."""

    def test_creates_new_dataset_for_new_topic(self):
        """Only unseen topics should populate a freshly minted dataset file."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            datasets_dir = base_dir / "datasets"
            datasets_dir.mkdir()
            db_path = base_dir / "pipeline_results.db"

            old_topic = "old_topic"
            new_topic = "new_topic"
            with open(datasets_dir / "dataset_1.json", "w", encoding="utf-8") as handle:
                json.dump([old_topic], handle)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS enhanced_step_responses (
                    id INTEGER PRIMARY KEY,
                    topic TEXT NOT NULL,
                    run_timestamp TEXT,
                    step_number INTEGER,
                    step_name TEXT,
                    model_used TEXT,
                    success BOOLEAN,
                    response_length INTEGER,
                    full_response TEXT,
                    timestamp TEXT
                )
                """
            )
            cursor.execute("INSERT INTO enhanced_step_responses (topic) VALUES (?)", (old_topic,))
            cursor.execute("INSERT INTO enhanced_step_responses (topic) VALUES (?)", (new_topic,))
            conn.commit()
            conn.close()

            create_new_datasets.main(datasets_dir=datasets_dir, db_path=db_path)

            new_dataset_path = datasets_dir / "dataset_2.json"
            self.assertTrue(new_dataset_path.exists(), "Expected dataset_2.json to be created.")

            with open(new_dataset_path, "r", encoding="utf-8") as handle:
                content = json.load(handle)

            self.assertIsInstance(content, list)
            self.assertEqual(len(content), 1)
            self.assertEqual(content[0], new_topic)

            dataset_files = [f for f in datasets_dir.iterdir() if f.is_file()]
            self.assertEqual(len(dataset_files), 2)


if __name__ == "__main__":
    main()
