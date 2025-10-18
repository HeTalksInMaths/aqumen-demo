#!/usr/bin/env python3
"""
Run batch pipeline with comprehensive metrics tracking.

This script runs the 7-step pipeline on multiple topics and tracks:
- Total execution time
- Total cost (from actual API usage)
- Success/failure rates
- Per-topic averages

Results are saved to the batch_runs database table.
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import List

from corrected_7step_pipeline import CorrectedSevenStepPipeline, SevenStepResult
from persistence.repo import Repo


def calculate_total_cost(pipeline: CorrectedSevenStepPipeline) -> float:
    """Calculate total cost from the pipeline's runtime client usage logs."""
    try:
        # Get the runtime client based on provider
        client = pipeline.runtime_client

        # Check if client has usage_log (OpenAI) or cost tracking (Bedrock)
        if hasattr(client, 'get_total_cost'):
            return client.get_total_cost()
        elif hasattr(client, 'usage_log'):
            return sum(m.total_cost_usd for m in client.usage_log)
        else:
            print("Warning: Could not retrieve cost from pipeline client")
            return 0.0
    except Exception as e:
        print(f"Warning: Error calculating cost: {e}")
        return 0.0


def _run_single_topic(provider: str, topic: str):
    """
    Run pipeline for a single topic with its own pipeline instance.

    This ensures thread-safety by creating a separate pipeline instance
    per topic, avoiding shared mutable state (run_timestamp, current_topic, log_file).

    Returns:
        tuple: (result, cost) where cost is the total cost for this topic
    """
    pipeline = CorrectedSevenStepPipeline(provider=provider)
    result = pipeline.run_full_pipeline(topic)
    cost = calculate_total_cost(pipeline)
    return result, cost


def run_batch_with_metrics(
    topics: List[str],
    dataset_file: str,
    provider: str = "openai",
    parallel: bool = False,
    max_workers: int = 5
):
    """Run batch pipeline and save metrics to database."""
    # Generate batch ID
    batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print(f"{'='*60}")
    print(f"BATCH RUN: {batch_id}")
    print(f"{'='*60}")
    print(f"Dataset: {dataset_file}")
    print(f"Topics: {len(topics)}")
    print(f"Provider: {provider}")
    print(f"Parallel: {parallel}")
    if parallel:
        print(f"Workers: {max_workers}")
    print(f"{'='*60}\n")

    # Start timer
    start_time = time.time()

    # Run batch
    if parallel:
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results = []
        topic_costs = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Each worker gets its own pipeline instance to avoid thread-safety issues
            future_to_topic = {
                executor.submit(_run_single_topic, provider, topic): topic
                for topic in topics
            }

            for index, future in enumerate(as_completed(future_to_topic), 1):
                topic = future_to_topic[future]
                try:
                    result, cost = future.result()
                    results.append(result)
                    topic_costs.append(cost)
                    success = getattr(result, "differentiation_achieved", False)
                    status = "✅ SUCCESS" if success else "❌ FAILED"
                    print(f"[{index}/{len(topics)}] {topic}: {status}")
                except Exception as exc:
                    print(f"[{index}/{len(topics)}] {topic}: ❌ ERROR - {exc}")
                    results.append(None)
                    topic_costs.append(0.0)
    else:
        # Sequential execution - single pipeline instance is fine
        pipeline = CorrectedSevenStepPipeline(provider=provider)
        results = pipeline.run_batch_test(topics)

        # Print progress
        for i, result in enumerate(results, 1):
            topic = topics[i-1] if i-1 < len(topics) else "unknown"
            if result:
                success = getattr(result, "differentiation_achieved", False)
                status = "✅ SUCCESS" if success else "❌ FAILED"
                print(f"[{i}/{len(topics)}] {topic}: {status}")

    # End timer
    end_time = time.time()
    total_time = end_time - start_time

    # Calculate metrics
    if parallel:
        total_cost = sum(topic_costs)
    else:
        total_cost = calculate_total_cost(pipeline)

    successful = sum(
        1 for r in results
        if r and getattr(r, "differentiation_achieved", False)
    )
    failed = len(results) - successful

    # Save to database
    repo = Repo()
    repo.save_batch_run(
        batch_id=batch_id,
        dataset_file=dataset_file,
        provider=provider,
        parallel=parallel,
        max_workers=max_workers if parallel else None,
        total_topics=len(topics),
        successful_topics=successful,
        failed_topics=failed,
        total_time_seconds=total_time,
        total_cost_usd=total_cost,
        metadata={
            "topics": topics,
            "timestamp": datetime.now().isoformat(),
        }
    )

    # Print summary
    print(f"\n{'='*60}")
    print(f"BATCH COMPLETE: {batch_id}")
    print(f"{'='*60}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Total cost: ${total_cost:.4f}")
    print(f"Success rate: {successful}/{len(topics)} ({successful/len(topics)*100:.1f}%)")
    print(f"Avg time per topic: {total_time/len(topics):.2f}s")
    print(f"Avg cost per topic: ${total_cost/len(topics):.4f}")
    print(f"\nSaved to batch_runs table: {batch_id}")
    print(f"{'='*60}\n")

    return results, batch_id


def main():
    """Parse arguments and run batch with metrics."""
    parser = argparse.ArgumentParser(
        description="Run pipeline batch with comprehensive metrics tracking",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="Path to JSON file containing list of topics (e.g., datasets/dataset_1.json)"
    )

    parser.add_argument(
        "--provider",
        type=str,
        default="openai",
        choices=["anthropic", "openai"],
        help="Model provider to use (default: openai)"
    )

    parser.add_argument(
        "--parallel",
        action="store_true",
        default=True,
        help="Run topics in parallel using ThreadPoolExecutor (default: True, use --no-parallel to disable)"
    )

    parser.add_argument(
        "--no-parallel",
        action="store_false",
        dest="parallel",
        help="Run topics sequentially instead of in parallel"
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=5,
        help="Max parallel workers when --parallel is used (default: 5)"
    )

    args = parser.parse_args()

    # Load topics from file
    try:
        with open(args.file, 'r') as f:
            topics = json.load(f)

        if not isinstance(topics, list):
            print(f"Error: {args.file} must contain a JSON array", file=sys.stderr)
            sys.exit(1)

        if not topics:
            print(f"Error: {args.file} contains no topics", file=sys.stderr)
            sys.exit(1)

    except FileNotFoundError:
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.file}: {e}", file=sys.stderr)
        sys.exit(1)

    # Run batch
    run_batch_with_metrics(
        topics=topics,
        dataset_file=args.file,
        provider=args.provider,
        parallel=args.parallel,
        max_workers=args.workers
    )


if __name__ == "__main__":
    main()
