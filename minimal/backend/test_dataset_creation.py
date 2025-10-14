import os
import sqlite3
import subprocess
import json

DATASETS_DIR = "datasets"
DB_PATH = "pipeline_results.db"
CREATE_NEW_DATASETS_SCRIPT = "create_new_datasets.py"

def main():
    """Test the automatic dataset creation process."""
    print("Test script started.")
    test_topic = "dynamic programming"

    # 1. Clean up before the test
    print("Cleaning up before the test...")
    if os.path.exists(DATASETS_DIR):
        for filename in os.listdir(DATASETS_DIR):
            if filename.startswith("dataset_") and filename.endswith(".json"):
                os.remove(os.path.join(DATASETS_DIR, filename))
    else:
        os.makedirs(DATASETS_DIR)
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM enhanced_step_responses WHERE topic = ?", (test_topic,))
    conn.commit()
    conn.close()

    # 2. Create dummy dataset files
    print("Creating dummy dataset files...")
    with open(os.path.join(DATASETS_DIR, "dataset_1.json"), "w") as f:
        json.dump(["Quadratic equations", "Executive assistant meeting scheduling", "Finite Group Theory", "Prompt Engineering", "LangChain"], f)
    with open(os.path.join(DATASETS_DIR, "dataset_2.json"), "w") as f:
        json.dump(["ChatGPT API", "Debugging Generative AI", "AI Agents", "Gradio", "Diffusion Models", "Advanced Retrieval (RAG)", "Finetuning LLMs", "Reinforcement Learning (RLHF)"], f)

    # 3. Add a new test topic to the database
    print(f"Adding test topic '{test_topic}' to the database...")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO enhanced_step_responses (run_timestamp, topic, step_number, step_name, model_used, success, response_length, full_response, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                 ("20251014_000000", test_topic, 1, "test_step", "test_model", True, 0, "", "2025-10-14T00:00:00"))
    conn.commit()
    conn.close()

    # 4. Run the dataset creation script
    print("Running the dataset creation script...")
    subprocess.run(["python3", CREATE_NEW_DATASETS_SCRIPT], cwd=os.path.dirname(os.path.abspath(__file__)), check=True)

    # 5. Verify that a new dataset file was created
    print("Verifying the new dataset file...")
    new_dataset_file = os.path.join(DATASETS_DIR, "dataset_3.json")
    if os.path.exists(new_dataset_file):
        with open(new_dataset_file, "r") as f:
            try:
                content = json.load(f)
                if test_topic in content:
                    print(f"✅ Success: Found new dataset file 'dataset_3.json' with the test topic.")
                else:
                    print("❌ Failure: Found dataset_3.json, but it did not contain the test topic.")
            except json.JSONDecodeError:
                print("❌ Failure: Could not decode JSON from dataset_3.json")
    else:
        print("❌ Failure: Did not find a new dataset file named dataset_3.json.")

    # 6. Clean up after the test
    print("Cleaning up after the test...")
    if os.path.exists(new_dataset_file):
        os.remove(new_dataset_file)
        print(f"Removed {new_dataset_file}")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM enhanced_step_responses WHERE topic = ?", (test_topic,))
    conn.commit()
    conn.close()
    print(f"Removed test topic '{test_topic}' from the database.")

if __name__ == "__main__":
    main()
