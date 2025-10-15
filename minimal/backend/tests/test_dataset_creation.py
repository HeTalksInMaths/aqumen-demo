import sqlite3
import json
from pathlib import Path

# Assuming the test file is in tests/ and the script is in the parent directory
# This allows pytest to find the module
from .. import create_new_datasets

def test_creates_new_dataset_for_new_topic(tmp_path: Path):
    """
    Verify that only topics present in the database but not in existing
    dataset files are added to a new dataset file.
    """
    # 1. Setup: Create a temporary environment
    datasets_dir = tmp_path / "datasets"
    datasets_dir.mkdir()
    db_path = tmp_path / "pipeline_results.db"

    # Create an existing dataset file with an old topic
    old_topic = "old_topic"
    with open(datasets_dir / "dataset_1.json", "w") as f:
        json.dump([old_topic], f)

    # Create a database and add both the old topic and a new topic
    new_topic = "new_topic"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS enhanced_step_responses (
            id INTEGER PRIMARY KEY,
            topic TEXT NOT NULL,
            run_timestamp TEXT, step_number INTEGER, step_name TEXT,
            model_used TEXT, success BOOLEAN, response_length INTEGER,
            full_response TEXT, timestamp TEXT
        )
    """)
    # Insert topics
    cursor.execute("INSERT INTO enhanced_step_responses (topic) VALUES (?)", (old_topic,))
    cursor.execute("INSERT INTO enhanced_step_responses (topic) VALUES (?)", (new_topic,))
    conn.commit()
    conn.close()

    # 2. Execution: Run the main function pointing to the temporary paths
    create_new_datasets.main(datasets_dir=datasets_dir, db_path=db_path)

    # 3. Assertion: Verify the outcome
    new_dataset_path = datasets_dir / "dataset_2.json"
    
    # Check that the new file was created
    assert new_dataset_path.exists(), "A new dataset file (dataset_2.json) should have been created."

    # Check the content of the new file
    with open(new_dataset_path, "r") as f:
        content = json.load(f)
    
    assert isinstance(content, list), "The new dataset file should contain a JSON list."
    assert len(content) == 1, "The new dataset should contain exactly one topic."
    assert content[0] == new_topic, f"The new dataset should contain the '{new_topic}'."

    # Also check that no other dataset file was created
    all_files = [f for f in datasets_dir.iterdir() if f.is_file()]
    assert len(all_files) == 2, "There should be exactly two dataset files in total."
