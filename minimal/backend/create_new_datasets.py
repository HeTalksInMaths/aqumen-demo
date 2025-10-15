import os
import sqlite3
import json
from pathlib import Path

# Get the absolute path of the directory containing this script
BASE_DIR = Path(__file__).resolve().parent

# Define default paths relative to the script's location
DEFAULT_DATASETS_DIR = BASE_DIR / "datasets"
DEFAULT_DB_PATH = BASE_DIR / "pipeline_results.db"

def get_existing_topics(datasets_dir: Path) -> set[str]:
    """Get all topics from existing dataset files."""
    existing_topics = set()
    if not datasets_dir.exists():
        return existing_topics

    for filename in os.listdir(datasets_dir):
        if filename.startswith("dataset_") and filename.endswith(".json"):
            with open(datasets_dir / filename, "r") as f:
                try:
                    topics = json.load(f)
                    if isinstance(topics, list):
                        existing_topics.update(topics)
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode JSON from {filename}")
    return existing_topics

def get_database_topics(db_path: Path) -> set[str]:
    """Get all topics from the database."""
    if not db_path.exists():
        return set()
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("SELECT DISTINCT topic FROM enhanced_step_responses")
    db_topics = {row[0] for row in cursor.fetchall()}
    conn.close()
    return db_topics

def create_new_dataset_files(new_topics: set[str], datasets_dir: Path):
    """Create new dataset files for new topics."""
    if not datasets_dir.exists():
        datasets_dir.mkdir(parents=True)

    dataset_files = [f for f in os.listdir(datasets_dir) if f.startswith("dataset_") and f.endswith(".json")]
    next_dataset_number = len(dataset_files) + 1

    # Sort topics for deterministic file creation
    for i, topic in enumerate(sorted(list(new_topics))):
        new_dataset_filename = datasets_dir / f"dataset_{next_dataset_number + i}.json"
        with open(new_dataset_filename, "w") as f:
            json.dump([topic], f, indent=4)
        print(f"Created {new_dataset_filename}")

def main(datasets_dir: Path = DEFAULT_DATASETS_DIR, db_path: Path = DEFAULT_DB_PATH):
    """Create new dataset files for new topics."""
    existing_topics = get_existing_topics(datasets_dir)
    db_topics = get_database_topics(db_path)

    new_topics = db_topics - existing_topics

    if new_topics:
        print(f"Found {len(new_topics)} new topics. Creating new dataset files...")
        create_new_dataset_files(new_topics, datasets_dir)
    else:
        print("No new topics found in the database.")

if __name__ == "__main__":
    main()