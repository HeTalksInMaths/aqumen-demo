#!/usr/bin/env python3
"""
CLI for GPT-5 Nano UI Testing Agent

Usage:
    python cli_gpt5.py --start-url http://localhost:5173
    python cli_gpt5.py --model gpt-4o --show
"""

import argparse
from agent.gpt5_agent import GPT5Agent
from computers import computers_config

try:
    from api_logger import write_session_summary
except ImportError:
    def write_session_summary():
        return None


def main():
    parser = argparse.ArgumentParser(
        description="UI Testing Agent using GPT-5 Nano (or GPT-4o)"
    )
    parser.add_argument(
        "--computer",
        choices=computers_config.keys(),
        help="Choose the computer environment to use.",
        default="local-playwright",
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Model to use (gpt-5-nano, gpt-5-mini, gpt-4o, etc.)",
        default="gpt-5-nano",
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Initial input instead of interactive mode.",
        default=None,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode for detailed output.",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show screenshots during execution.",
    )
    parser.add_argument(
        "--start-url",
        type=str,
        help="Start the browsing session with a specific URL.",
        default="http://localhost:5173",
    )
    parser.add_argument(
        "--system-prompt",
        type=str,
        help="Custom system prompt for the agent.",
        default=None,
    )

    args = parser.parse_args()

    # Get computer class
    ComputerClass = computers_config[args.computer]

    print(f"\n🚀 Starting GPT-5 UI Testing Agent")
    print(f"   Model: {args.model}")
    print(f"   Computer: {args.computer}")
    print(f"   URL: {args.start_url}")
    print()

    try:
        # Start computer environment
        with ComputerClass() as computer:
            # Create agent
            agent = GPT5Agent(
                model=args.model,
                computer=computer,
                system_prompt=args.system_prompt,
            )

            # Navigate to start URL for browser environments
            if args.computer == "local-playwright":
                if not args.start_url.startswith("http"):
                    args.start_url = "https://" + args.start_url

                print(f"📍 Navigating to {args.start_url}...")
                computer.goto(args.start_url)
                computer.wait(2000)  # Wait for page load
                print("✅ Page loaded\n")

            # Run in interactive mode or single-shot
            if args.input:
                # Single-shot mode
                agent.run_turn(
                    args.input,
                    print_steps=True,
                    show_images=args.show,
                    debug=args.debug
                )
            else:
                # Interactive mode
                agent.run_interactive_loop(
                    print_steps=True,
                    show_images=args.show,
                    debug=args.debug
                )
    finally:
        try:
            write_session_summary()
        except Exception as logging_error:
            print(f"Logging summary failed: {logging_error}")


if __name__ == "__main__":
    main()
