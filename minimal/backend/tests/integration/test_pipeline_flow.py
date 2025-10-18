"""
Integration tests for the 7-step pipeline flow.

These tests capture the current behavior of corrected_7step_pipeline.py before refactoring.
Note: These tests require valid AWS credentials or mock implementations.
"""

from unittest.mock import Mock, patch


class TestPipelineConfiguration:
    """Test suite for pipeline initialization and configuration."""

    def test_pipeline_import(self):
        """Test that pipeline module can be imported."""
        from corrected_7step_pipeline import CorrectedSevenStepPipeline

        assert CorrectedSevenStepPipeline is not None

    @patch("legacy_pipeline.orchestrator.get_model_provider")
    def test_pipeline_initialization_with_anthropic(self, mock_provider):
        """Test pipeline initializes with Anthropic provider."""
        # Mock the provider response
        mock_runtime = Mock()
        mock_models = {"strong": "claude-opus-4", "mid": "claude-sonnet-3.5", "weak": "claude-haiku-3"}
        mock_provider.return_value = (mock_runtime, mock_models)

        from corrected_7step_pipeline import CorrectedSevenStepPipeline

        pipeline = CorrectedSevenStepPipeline(provider="anthropic")
        assert pipeline.provider == "anthropic"
        assert pipeline.model_strong == "claude-opus-4"
        assert pipeline.model_mid == "claude-sonnet-3.5"
        assert pipeline.model_weak == "claude-haiku-3"

    @patch("legacy_pipeline.orchestrator.get_model_provider")
    def test_pipeline_initialization_with_openai(self, mock_provider):
        """Test pipeline initializes with OpenAI provider."""
        mock_runtime = Mock()
        mock_models = {"strong": "gpt-4", "mid": "gpt-3.5-turbo", "weak": "gpt-3.5-turbo"}
        mock_provider.return_value = (mock_runtime, mock_models)

        from corrected_7step_pipeline import CorrectedSevenStepPipeline

        pipeline = CorrectedSevenStepPipeline(provider="openai")
        assert pipeline.provider == "openai"
        assert pipeline.model_strong == "gpt-4"


class TestPipelineStepDataclasses:
    """Test suite for pipeline data structures."""

    def test_pipeline_step_creation(self):
        """Test PipelineStep dataclass can be created."""
        from datetime import datetime

        from corrected_7step_pipeline import PipelineStep

        step = PipelineStep(
            step_number=1,
            step_name="Test Step",
            model_used="test-model",
            success=True,
            response="test response",
            timestamp=datetime.now().isoformat(),
        )

        assert step.step_number == 1
        assert step.step_name == "Test Step"
        assert step.success is True

    def test_seven_step_result_creation(self):
        """Test SevenStepResult dataclass can be created."""
        from datetime import datetime

        from corrected_7step_pipeline import PipelineStep, SevenStepResult

        step = PipelineStep(
            step_number=1,
            step_name="Test",
            model_used="model",
            success=True,
            response="response",
            timestamp=datetime.now().isoformat(),
        )

        result = SevenStepResult(
            topic="Test Topic",
            subtopic="Test Subtopic",
            difficulty="Intermediate",
            steps_completed=[step],
            final_success=True,
            stopped_at_step=7,
            differentiation_achieved=True,
            student_assessment_created=True,
            total_attempts=1,
            weak_model_failures=[],
        )

        assert result.topic == "Test Topic"
        assert result.final_success is True
        assert len(result.steps_completed) == 1


class TestPipelineValidation:
    """Test suite for validation methods."""

    @patch("legacy_pipeline.orchestrator.get_model_provider")
    def test_validate_assessment_payload_structure(self, mock_provider):
        """Test assessment validation checks required fields."""
        # Setup mock
        mock_runtime = Mock()
        mock_models = {"strong": "claude-opus-4", "mid": "claude-sonnet-3.5", "weak": "claude-haiku-3"}
        mock_provider.return_value = (mock_runtime, mock_models)

        from corrected_7step_pipeline import CorrectedSevenStepPipeline

        pipeline = CorrectedSevenStepPipeline(provider="anthropic")

        # Test invalid payload (missing required fields)
        invalid_payload = {"title": "Test"}
        is_valid, sanitized, errors = pipeline._validate_assessment_payload(invalid_payload)
        assert is_valid is False
        assert len(errors) > 0

    @patch("legacy_pipeline.orchestrator.get_model_provider")
    def test_validate_assessment_difficulty(self, mock_provider):
        """Test assessment validation checks difficulty values."""
        mock_runtime = Mock()
        mock_models = {"strong": "claude-opus-4", "mid": "claude-sonnet-3.5", "weak": "claude-haiku-3"}
        mock_provider.return_value = (mock_runtime, mock_models)

        from corrected_7step_pipeline import CorrectedSevenStepPipeline

        pipeline = CorrectedSevenStepPipeline(provider="anthropic")

        # Invalid difficulty
        payload = {
            "title": "Test Assessment",
            "difficulty": "InvalidLevel",
            "content_type": "code",
            "content": ["line1", "line2"] * 15,  # 30 lines
            "errors": [{"id": "test error description", "description": "Test error"}],
        }

        is_valid, sanitized, errors = pipeline._validate_assessment_payload(payload)
        assert is_valid is False
        assert any("Difficulty" in error for error in errors)


class TestPipelineLogging:
    """Test suite for pipeline logging functionality."""

    @patch("legacy_pipeline.orchestrator.get_model_provider")
    def test_log_file_creation(self, mock_provider):
        """Test that pipeline creates timestamped log files."""
        mock_runtime = Mock()
        mock_models = {"strong": "claude-opus-4", "mid": "claude-sonnet-3.5", "weak": "claude-haiku-3"}
        mock_provider.return_value = (mock_runtime, mock_models)

        from corrected_7step_pipeline import CorrectedSevenStepPipeline

        pipeline = CorrectedSevenStepPipeline(provider="anthropic")

        # Check log file path is set
        assert hasattr(pipeline, "log_file")
        assert "pipeline_run_" in pipeline.log_file
        assert pipeline.log_file.endswith(".txt")

    @patch("legacy_pipeline.orchestrator.get_model_provider")
    def test_results_file_creation(self, mock_provider):
        """Test that pipeline creates timestamped results files."""
        mock_runtime = Mock()
        mock_models = {"strong": "claude-opus-4", "mid": "claude-sonnet-3.5", "weak": "claude-haiku-3"}
        mock_provider.return_value = (mock_runtime, mock_models)

        from corrected_7step_pipeline import CorrectedSevenStepPipeline

        pipeline = CorrectedSevenStepPipeline(provider="anthropic")

        # Check results file path is set
        assert hasattr(pipeline, "results_file")
        assert "corrected_7step_results_" in pipeline.results_file
        assert pipeline.results_file.endswith(".json")


class TestPromptTemplates:
    """Test suite for prompt template loading."""

    @patch("legacy_pipeline.orchestrator.get_model_provider")
    def test_prompts_loaded(self, mock_provider):
        """Test that prompts are loaded during initialization."""
        mock_runtime = Mock()
        mock_models = {"strong": "claude-opus-4", "mid": "claude-sonnet-3.5", "weak": "claude-haiku-3"}
        mock_provider.return_value = (mock_runtime, mock_models)

        from corrected_7step_pipeline import CorrectedSevenStepPipeline

        pipeline = CorrectedSevenStepPipeline(provider="anthropic")

        assert hasattr(pipeline, "prompts")
        assert isinstance(pipeline.prompts, dict)

        # Check for expected prompt keys
        expected_keys = [
            "step1_difficulty_categories",
            "step2_error_catalog",
            "step3_strategic_question",
            "step4_test_sonnet",
            "step5_test_haiku",
            "step6_judge_responses",
            "step7_student_assessment",
        ]

        for key in expected_keys:
            assert key in pipeline.prompts, f"Missing prompt: {key}"

    @patch("legacy_pipeline.orchestrator.get_model_provider")
    def test_get_prompt_template(self, mock_provider):
        """Test _get_prompt_template method."""
        mock_runtime = Mock()
        mock_models = {"strong": "claude-opus-4", "mid": "claude-sonnet-3.5", "weak": "claude-haiku-3"}
        mock_provider.return_value = (mock_runtime, mock_models)

        from corrected_7step_pipeline import CorrectedSevenStepPipeline

        pipeline = CorrectedSevenStepPipeline(provider="anthropic")

        # Get a prompt template
        template = pipeline._get_prompt_template("step1_difficulty_categories")
        assert isinstance(template, str)
        assert len(template) > 0


class TestDatabaseIntegration:
    """Test suite for database operations."""

    @patch("legacy_pipeline.orchestrator.get_model_provider")
    def test_repo_initialized(self, mock_provider):
        """Test that database repository is initialized."""
        mock_runtime = Mock()
        mock_models = {"strong": "claude-opus-4", "mid": "claude-sonnet-3.5", "weak": "claude-haiku-3"}
        mock_provider.return_value = (mock_runtime, mock_models)

        from corrected_7step_pipeline import CorrectedSevenStepPipeline

        pipeline = CorrectedSevenStepPipeline(provider="anthropic")

        assert hasattr(pipeline, "repo")
        assert hasattr(pipeline, "db_path")
        assert pipeline.db_path.endswith("pipeline_results.db")


# Configuration
pytest_plugins = ["pytest_asyncio"]
