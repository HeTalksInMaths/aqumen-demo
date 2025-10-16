import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable, List

from corrected_7step_pipeline import CorrectedSevenStepPipeline

DEFAULT_WORKERS = 5


def _run_parallel(pipeline: CorrectedSevenStepPipeline, topics: Iterable[str], max_workers: int) -> List:
    """Execute each topic in its own thread and stream progress."""
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_topic = {executor.submit(pipeline.run_full_pipeline, topic): topic for topic in topics}
        for index, future in enumerate(as_completed(future_to_topic), 1):
            topic = future_to_topic[future]
            try:
                result = future.result()
                results.append(result)
                print(f"\n{'=' * 60}")
                print(f"COMPLETED: TOPIC {index}/{len(future_to_topic)}: {topic}")
                print(f"{'=' * 60}")
                if getattr(result, "differentiation_achieved", False):
                    print(f"✅ SUCCESS: Achieved differentiation in {result.total_attempts} attempts")
                    failures = getattr(result, "weak_model_failures", [])
                    if failures:
                        print(f"   Weak model failures: {', '.join(failures)}")
                else:
                    stopped = getattr(result, "stopped_at_step", 'unknown')
                    attempts = getattr(result, "total_attempts", 'unknown')
                    print(f"❌ FAILED: Stopped at Step {stopped} after {attempts} attempts")
            except Exception as exc:  # pylint: disable=broad-except
                print(f"{topic} generated an exception: {exc}")
    return results


def main(topics, *, parallel: bool = False, max_workers: int = DEFAULT_WORKERS):
    """Run the corrected 7-step pipeline with a batch of topics and track execution time."""
    if not topics:
        print("No topics provided to run.")
        return

    print(f"Starting batch run with {len(topics)} topics...")
    print("Running in parallel mode." if parallel else "Running in sequential mode.")
    start_time = time.time()

    pipeline = CorrectedSevenStepPipeline()

    if parallel:
        results = _run_parallel(pipeline, topics, max_workers)
    else:
        results = pipeline.run_batch_test(topics)

    end_time = time.time()
    total_time = end_time - start_time

    print(f"\nBatch run completed in {total_time:.2f} seconds.")

    # Basic cost estimation
    cost_per_topic = 0.50  # Example cost
    total_cost = cost_per_topic * len(topics)
    print(f"Estimated total cost: ${total_cost:.2f}")

    try:
        pipeline.save_results(results)
    except AttributeError:
        # Older pipeline implementations may not expose save_results
        pass

def run_from_cli():
    """Parses command-line arguments and executes the main function."""
    parser = argparse.ArgumentParser(
        description="Run the 7-step pipeline in batch mode with a list of topics.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to a JSON file containing a list of topics."
    )
    parser.add_argument(
        "topics",
        nargs="*",
        type=str,
        help="One or more topics to run."
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run topics in parallel using a thread pool."
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help=f"Maximum parallel workers when --parallel is supplied (default: {DEFAULT_WORKERS})."
    )

    args = parser.parse_args()

    topics_to_run = []
    if args.file:
        try:
            with open(args.file, "r") as f:
                topics_to_run = json.load(f)
            if not isinstance(topics_to_run, list):
                print(f"Error: The file {args.file} does not contain a JSON list.", file=sys.stderr)
                exit(1)
        except FileNotFoundError:
            print(f"Error: The file {args.file} was not found.", file=sys.stderr)
            exit(1)
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from the file {args.file}.", file=sys.stderr)
            exit(1)
    elif args.topics:
        topics_to_run = args.topics
    
    if topics_to_run:
        workers = max(1, args.workers)
        main(topics_to_run, parallel=args.parallel, max_workers=workers)
    else:
        print("No topics provided. Please provide topics as arguments or use the --file option.", file=sys.stderr)
        parser.print_help()
        exit(1)

if __name__ == "__main__":
    run_from_cli()
