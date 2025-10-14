
from corrected_7step_pipeline import CorrectedSevenStepPipeline, RANDOM_SELECTION

pipeline = CorrectedSevenStepPipeline()
result = pipeline.run_full_pipeline(
    topic="Quadratic equations",
    max_attempts=3,
    sampling_strategy_step3=RANDOM_SELECTION,
    sampling_strategy_step7=RANDOM_SELECTION,
)

print("Final success:", result.final_success)
print("Stopped at step:", result.stopped_at_step)
print("Differentiation achieved:", result.differentiation_achieved)
print("Weak model failures:", result.weak_model_failures)
print("Student assessment created:", result.student_assessment_created)
