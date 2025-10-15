import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from refactored_pipeline.pipeline.orchestrator import Orchestrator
from typing import List
from datetime import datetime
import os
import json

def run_batch_test(pipeline: Orchestrator, topics: List[str]):
    """Run the corrected 7-step pipeline with a batch of topics and track execution time."""

    parallel = "--parallel" in sys.argv

    print(f"Starting batch run with {len(topics)} topics...")
    if parallel:
        print("Running in parallel mode.")
    else:
        print("Running in sequential mode.")

    start_time = time.time()

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
        results = []
        for topic in topics:
            results.append(pipeline.run_full_pipeline(topic))

    end_time = time.time()
    total_time = end_time - start_time

    print(f"\nBatch run completed in {total_time:.2f} seconds.")

    # Basic cost estimation (replace with actual token counts and pricing)
    # This is a very rough estimate and should be replaced with a more accurate calculation.
    # Assuming an average cost per topic run.
    cost_per_topic = 0.50  # Example cost, replace with a better estimate
    total_cost = cost_per_topic * len(topics)
    print(f"Estimated total cost: ${total_cost:.2f}")

    save_results(pipeline, results)

def save_results(pipeline: Orchestrator, results: List):
    '''Save comprehensive results'''
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Convert to serializable format
    results_data = []
    for result in results:
        steps_data = []
        for step in result.steps_completed:
            steps_data.append({
                "step_number": step.step_number,
                "step_name": step.step_name,
                "model_used": step.model_used,
                "success": step.success,
                "timestamp": step.timestamp,
                "response_length": len(step.response)
            })

        results_data.append({
            "topic": result.topic,
            "subtopic": result.subtopic,
            "difficulty": result.difficulty,
            "final_success": result.final_success,
            "stopped_at_step": result.stopped_at_step,
            "differentiation_achieved": result.differentiation_achieved,
            "student_assessment_created": result.student_assessment_created,
            "total_attempts": result.total_attempts,
            "weak_model_failures": result.weak_model_failures,
            "steps_completed": steps_data
        })

    final_data = {
        "pipeline_version": "refactored_7step_v2",
        "run_info": {
            "timestamp": datetime.now().isoformat(),
            "total_topics": len(results),
            "model_config": {
                "strong": pipeline.model_strong,
                "mid": pipeline.model_mid,
                "weak": pipeline.model_weak
            }
        },
        "results": results_data,
        "summary": {
            "topics_with_differentiation": len([r for r in results if r.differentiation_achieved]),
            "topics_stopped_at_step6": len([r for r in results if r.stopped_at_step == 6]),
            "average_attempts": sum(r.total_attempts for r in results) / len(results) if results else 0,
            "full_pipeline_success_rate": len([r for r in results if r.final_success]) / len(results) if results else 0,
            "common_weak_model_failures": _extract_common_failures(results)
        }
    }

    filename = os.path.join(pipeline.script_dir, "..", "..", f"corrected_7step_results_{timestamp}.json")
    with open(filename, "w") as f:
        json.dump(final_data, f, indent=2)

    print(f"\n📊 Results saved to: {filename}")
    print(f"📝 Detailed logs in: {pipeline.log_file}")
    print(f"💾 Full step data stored in database: {pipeline.db_path}")

def _extract_common_failures(results: List) -> dict:
    '''Extract common patterns from weak model failures'''
    failure_counts = {}
    for result in results:
        for failure in result.weak_model_failures:
            # Normalize failure text for counting
            normalized = failure.lower().strip()
            if normalized:
                failure_counts[normalized] = failure_counts.get(normalized, 0) + 1

    # Return top 5 most common failures
    sorted_failures = sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)
    return dict(sorted_failures[:5])

def main():
    """Run corrected 7-step pipeline test"""
    pipeline = Orchestrator()

    test_topics = [
        "LLM Post-Training with DPO",
        "Model Quantization and Optimization",
        "Reinforcement Learning from Human Feedback (RLHF)"
    ]

    print("🧠 REFACTORED 7-Step Adversarial Pipeline Test")
    print("="*50)

    run_batch_test(pipeline, test_topics)

if __name__ == "__main__":
    main()