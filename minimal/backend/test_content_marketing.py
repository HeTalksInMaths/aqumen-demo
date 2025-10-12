"""
Test Step 7 improvements with LLM Rubrics for Content Marketing Generation topic
"""

import logging
from corrected_7step_pipeline import CorrectedSevenStepPipeline

# Set up logging to see auto-fix messages
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

def test_content_marketing_topic():
    """Test pipeline with content marketing topic"""
    pipeline = CorrectedSevenStepPipeline()

    topic = "LLM Rubrics for Content Marketing Generation"

    print("🧪 Testing Step 7 Improvements")
    print("="*70)
    print(f"Topic: {topic}")
    print("="*70)
    print("\nExpected improvements:")
    print("  • Stronger tool schema with explicit examples")
    print("  • Auto-fix fallback for stringified arrays")
    print("  • Expected retry rate: 50% → <5%")
    print("="*70)

    try:
        result = pipeline.run_full_pipeline(topic, max_attempts=3)

        print(f"\n{'='*70}")
        print(f"🏆 RESULTS FOR: {topic}")
        print(f"{'='*70}")
        print(f"Final Success: {result.final_success}")
        print(f"Stopped at Step: {result.stopped_at_step}")
        print(f"Differentiation Achieved: {result.differentiation_achieved}")
        print(f"Total Attempts (Step 7): {result.total_attempts}")
        print(f"Steps Completed: {len(result.steps_completed)}")

        if result.final_success and result.stopped_at_step == 7:
            print("\n✅ SUCCESS! Assessment generated successfully.")
            print(f"   Step 7 attempts: {result.total_attempts}")
            if result.total_attempts == 1:
                print("   🎉 No retries needed! (Improvement validated)")
            elif result.total_attempts <= 2:
                print("   ✨ Minimal retries (Good improvement)")
            else:
                print("   ⚠️  Multiple retries still needed")
        else:
            print(f"\n❌ FAILED at step {result.stopped_at_step}")

        if result.weak_model_failures:
            print("\nWeak Model Failure Patterns:")
            for failure in result.weak_model_failures:
                print(f"  • {failure}")

        # Save result
        print("\nSaving results to database...")
        pipeline.save_results([result])
        print("✅ Results saved!")

        return result

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_content_marketing_topic()
