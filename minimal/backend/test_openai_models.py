#!/usr/bin/env python3
"""
Quick test script to verify OpenAI/Azure models are accessible.
Tests all three tiers: strong (gpt-5), mid (gpt-5-mini), weak (gpt-5-nano)
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from clients.openai_client import OpenAIRuntime

def test_all_models():
    """Test all three OpenAI models with a simple prompt"""
    print("🧪 Testing OpenAI Models\n")
    print("=" * 60)

    # Initialize client
    try:
        client = OpenAIRuntime()
        print("✅ OpenAI client initialized successfully")
        print(f"   Using Azure: {client._is_azure}")
        if client._is_azure:
            endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "not set")
            deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "not set")
            print(f"   Endpoint: {endpoint}")
            print(f"   Deployment: {deployment}")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return

    # Test models
    models = {
        "strong (gpt-5)": "gpt-5",
        "mid (gpt-5-mini)": "gpt-5-mini",
        "weak (gpt-5-nano)": "gpt-5-nano"
    }

    test_prompt = "Say hello in one sentence."

    for name, model_id in models.items():
        print(f"📡 Testing {name}...")
        print(f"   Model: {model_id}")

        try:
            # For GPT-5 models, don't pass temperature (only default 1 is supported)
            # Use higher token limit to account for reasoning tokens
            if "gpt-5" in model_id:
                response = client.invoke(
                    model_id=model_id,
                    prompt=test_prompt,
                    max_tokens=500,  # Higher to account for reasoning tokens
                    temperature=1.0  # Will be ignored for GPT-5 in client
                )
            else:
                response = client.invoke(
                    model_id=model_id,
                    prompt=test_prompt,
                    max_tokens=200,
                    temperature=0.0
                )

            print(f"✅ Success!")
            print(f"   Response: {response.strip()}")

            # Show cost if available
            if client.usage_log:
                last_usage = client.usage_log[-1]
                token_info = f"   Tokens: {last_usage.input_tokens} in, {last_usage.output_tokens} out"
                if last_usage.reasoning_tokens > 0:
                    token_info += f" ({last_usage.reasoning_tokens} reasoning)"
                print(token_info)
                print(f"   Cost: ${last_usage.total_cost_usd:.6f}")
                print(f"   Time: {last_usage.response_time_ms}ms")

        except Exception as e:
            print(f"❌ Failed: {e}")

        print()

    # Summary
    print("=" * 60)
    if client.usage_log:
        summary = client.get_usage_summary()
        print(f"📊 Summary:")
        print(f"   Total calls: {summary['total_calls']}")
        print(f"   Total cost: ${summary['total_cost_usd']:.6f}")
        print(f"   Total tokens: {summary['total_input_tokens']} in, {summary['total_output_tokens']} out")

if __name__ == "__main__":
    test_all_models()
