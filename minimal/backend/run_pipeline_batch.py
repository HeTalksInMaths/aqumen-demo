import time
from corrected_7step_pipeline import CorrectedSevenStepPipeline

def main():
    """Run the corrected 7-step pipeline with a batch of topics and track execution time."""
    topics = [
        "Prompt Engineering",
        "LangChain",
        "ChatGPT API",
        "Debugging Generative AI",
        "AI Agents",
        "Gradio",
        "Diffusion Models",
        "Advanced Retrieval (RAG)",
        "Finetuning LLMs",
        "Reinforcement Learning (RLHF)"
    ]

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
    main()

