import os
import sqlite3
import json

DATASETS_DIR = "datasets"
DB_PATH = "pipeline_results.db"

def get_existing_topics():
    """Get all topics from existing dataset files."""
    existing_topics = set()
    if not os.path.exists(DATASETS_DIR):
        return existing_topics

    for filename in os.listdir(DATASETS_DIR):
        if filename.startswith("dataset_") and filename.endswith(".json"):
            with open(os.path.join(DATASETS_DIR, filename), "r") as f:
                try:
                    topics = json.load(f)
                    existing_topics.update(topics)
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode JSON from {filename}")
    return existing_topics

def get_database_topics():
    """Get all topics from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT DISTINCT topic FROM enhanced_step_responses")
    db_topics = {row[0] for row in cursor.fetchall()}
    conn.close()
    return db_topics

def create_new_dataset_files(new_topics):
    """Create new dataset files for new topics."""
    if not os.path.exists(DATASETS_DIR):
        os.makedirs(DATASETS_DIR)

    dataset_files = [f for f in os.listdir(DATASETS_DIR) if f.startswith("dataset_") and f.endswith(".json")]
    next_dataset_number = len(dataset_files) + 1

    for i, topic in enumerate(new_topics):
        new_dataset_filename = os.path.join(DATASETS_DIR, "dataset_{}.json".format(next_dataset_number + i))
        with open(new_dataset_filename, "w") as f:
            json.dump([topic], f, indent=4)
        print(f"Created {new_dataset_filename}")

def main():
    """Create new dataset files for new topics."""
    existing_topics = get_existing_topics()
    db_topics = get_database_topics()

    new_topics = db_topics - existing_topics

    if new_topics:
        print(f"Found {len(new_topics)} new topics. Creating new dataset files...")
        create_new_dataset_files(new_topics)
    else:
        print("No new topics found in the database.")

if __name__ == "__main__":
    main()
