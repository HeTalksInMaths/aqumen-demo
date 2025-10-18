"""Pipeline configuration and constants."""


class PipelineConfig:
    """Configuration for the 7-step adversarial pipeline."""

    # Step 7 validation thresholds
    ALLOWED_DIFFICULTIES = {"Beginner", "Intermediate", "Advanced", "Expert"}
    STEP7_MAX_ATTEMPTS = 3
    MIN_CODE_LINES = 24
    MAX_CODE_LINES = 60
    MIN_ERRORS = 1
    MAX_ERRORS = 5
    MIN_ERROR_SPAN = 20
    MAX_ERROR_SPAN = 120

    # Retry configuration for differentiation attempts (Steps 3-6)
    MAX_DIFFERENTIATION_ATTEMPTS = 3

    # Allowed content types for student assessments
    ALLOWED_CONTENT_TYPES = {
        "code",
        "prose",
        "math",
        "email",
        "table",
        "diagram",
        "plan",
        "pseudo",
        "query",
        "other",
    }
