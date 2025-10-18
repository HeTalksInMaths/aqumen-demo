import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

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

    parallel = "--parallel" in sys.argv

    print(f"Starting batch run with {len(topics)} topics...")
    if parallel:
        print("Running in parallel mode.")
    else:
        print("Running in sequential mode.")

    start_time = time.time()

    pipeline = CorrectedSevenStepPipeline()

    if parallel:
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_topic = {executor.submit(pipeline.run_full_pipeline, topic): topic for topic in topics}
            for i, future in enumerate(as_completed(future_to_topic), 1):
                topic = future_to_topic[future]
                try:
                    result = future.result()
                    results.append(result)
                    print(f"\n{'='*60}")
                    print(f"COMPLETED: TOPIC {i}/{len(topics)}: {topic}")
                    print(f"{'='*60}")
                    if result.differentiation_achieved:
                        print(f"✅ SUCCESS: Achieved differentiation in {result.total_attempts} attempts")
                        if result.weak_model_failures:
                            print(f"   Weak model failures: {', '.join(result.weak_model_failures)}")
                    else:
                        print(f"❌ FAILED: Stopped at Step {result.stopped_at_step} after {result.total_attempts} attempts")
                except Exception as exc:
                    print(f'{topic} generated an exception: {exc}')
    else:
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

    pipeline.save_results(results)

if __name__ == "__main__":
    main()
