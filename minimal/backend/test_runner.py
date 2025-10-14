import os
import json
import run_pipeline_batch

DATASETS_DIR = "datasets"

def main():
    """Dynamically discover and run datasets."""
    if not os.path.exists(DATASETS_DIR):
        print("Datasets directory not found.")
        return

    dataset_files = sorted([f for f in os.listdir(DATASETS_DIR) if f.startswith("dataset_") and f.endswith(".json")])

    if not dataset_files:
        print("No dataset files found.")
        return

    print("Please select a dataset to run:")
    for i, filename in enumerate(dataset_files):
        print(f"{i + 1}. {filename}")

    try:
        choice = int(input(f"Enter your choice (1-{len(dataset_files)}): ")) - 1
        if 0 <= choice < len(dataset_files):
            dataset_filename = os.path.join(DATASETS_DIR, dataset_files[choice])
            with open(dataset_filename, "r") as f:
                try:
                    topics = json.load(f)
                    if topics:
                        print(f"\nRunning {dataset_files[choice]}...")
                        run_pipeline_batch.main(topics)
                    else:
                        print(f"No topics found in {dataset_files[choice]}.")
                except json.JSONDecodeError:
                    print(f"Error: Could not decode JSON from {dataset_files[choice]}")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()
