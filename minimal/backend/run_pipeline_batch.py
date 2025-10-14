import time
from corrected_7step_pipeline import CorrectedSevenStepPipeline

def main(topics):
    """Run the corrected 7-step pipeline with a batch of topics and track execution time."""
    print(f"Starting batch run with {len(topics)} topics...")

    start_time = time.time()

    pipeline = CorrectedSevenStepPipeline()
    results = pipeline.run_batch_test(topics)

    end_time = time.time()
    total_time = end_time - start_time

    print(f"\nBatch run completed in {total_time:.2f} seconds.")

    # Basic cost estimation (replace with actual token counts and pricing)
    # This is a very rough estimate and should be replaced with a more accurate calculation.
    # Assuming an average cost per topic run.
    cost_per_topic = 0.50  # Example cost, replace with a better estimate
    total_cost = cost_per_topic * len(topics)
    print(f"Estimated total cost: ${total_cost:.2f}")

if __name__ == "__main__":
    # This script is now designed to be imported and called from another script.
    # To run it directly, you would need to provide a list of topics to the main function.
    # For example:
    # topics = ["Prompt Engineering", "LangChain"]
    # main(topics)
    pass

