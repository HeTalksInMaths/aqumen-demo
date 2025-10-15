from refactored_pipeline.pipeline.orchestrator import Orchestrator


def main() -> None:
    pipeline = Orchestrator()
    topic = "LLM Post-Training with DPO"

    print(f"▶️  Starting pipeline for topic: {topic}")
    result = pipeline.run_full_pipeline(topic)

    print("\n================ FINAL RESULT ================")
    if result.final_success:
        print("✅ Pipeline completed successfully")
        print(f"   Attempts: {result.total_attempts}")
        print(f"   Differentiation achieved: {result.differentiation_achieved}")
        print(f"   Student assessment created: {result.student_assessment_created}")
    else:
        print("❌ Pipeline failed to complete")
        print(f"   Stopped at step: {result.stopped_at_step}")
        print(f"   Attempts: {result.total_attempts}")

    print(f"   Weak model failures captured: {result.weak_model_failures}")
    print("Logs and metrics:")
    print(f"   Step log file .......... {pipeline.log_file}")
    print(f"   Final results JSON ..... {pipeline.results_file}")
    print(f"   Metrics snapshot ....... results/metrics_{pipeline.run_timestamp}.json")


if __name__ == "__main__":
    main()
