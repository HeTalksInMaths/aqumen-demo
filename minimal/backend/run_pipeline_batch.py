import time
import argparse
import json
import sys
from corrected_7step_pipeline import CorrectedSevenStepPipeline

def main(topics):
    """Run the corrected 7-step pipeline with a batch of topics and track execution time."""
    if not topics:
        print("No topics provided to run.")
        return

    print(f"Starting batch run with {len(topics)} topics...")
    start_time = time.time()

    pipeline = CorrectedSevenStepPipeline()
    results = pipeline.run_batch_test(topics)

    end_time = time.time()
    total_time = end_time - start_time

    print(f"\nBatch run completed in {total_time:.2f} seconds.")

    # Basic cost estimation
    cost_per_topic = 0.50  # Example cost
    total_cost = cost_per_topic * len(topics)
    print(f"Estimated total cost: ${total_cost:.2f}")

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
        main(topics_to_run)
    else:
        print("No topics provided. Please provide topics as arguments or use the --file option.", file=sys.stderr)
        parser.print_help()
        exit(1)

if __name__ == "__main__":
    run_from_cli()
