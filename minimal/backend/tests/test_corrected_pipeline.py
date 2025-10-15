from unittest.mock import MagicMock
import pytest
from ..corrected_7step_pipeline import CorrectedSevenStepPipeline, PipelineStep

# This fixture automatically mocks all external dependencies loaded in the pipeline's __init__.
# This ensures tests are fast, isolated, and don't require real credentials or files.
@pytest.fixture(autouse=True)
def mock_init_dependencies(monkeypatch):
    """Mocks dependencies loaded in the CorrectedSevenStepPipeline.__init__ method."""
    # Mock file/config loaders
    monkeypatch.setattr("corrected_7step_pipeline.load_model_roles", MagicMock(return_value={
        "judge": MagicMock(id="claude-3-opus-20240229", supports_thinking=True),
        "mid": MagicMock(id="claude-3-sonnet-20240229"),
        "weak": MagicMock(id="claude-3-haiku-20240307"),
    }))
    monkeypatch.setattr("corrected_7step_pipeline.load_prompts", MagicMock(return_value={
        "step1_difficulty_categories": {"template": "..."},
        "step2_error_catalog": {"template": "..."},
    }))
    monkeypatch.setattr("corrected_7step_pipeline.load_tools", MagicMock(return_value={
        "step1_difficulty_categories": [{}],
        "step2_error_catalog": [{}],
    }))

    # Mock AWS/DB services
    monkeypatch.setattr("corrected_7step_pipeline.BedrockRuntime", MagicMock())
    monkeypatch.setattr("corrected_7step_pipeline.Invoker", MagicMock())
    monkeypatch.setattr("corrected_7step_pipeline.Repo", MagicMock())

@pytest.fixture
def pipeline() -> CorrectedSevenStepPipeline:
    """Returns an initialized CorrectedSevenStepPipeline instance for testing."""
    return CorrectedSevenStepPipeline()

def test_step1_generate_difficulty_categories_success(pipeline: CorrectedSevenStepPipeline, monkeypatch):
    """
    Tests a successful run of Step 1, verifying it correctly parses a valid model response.
    """
    # 1. Setup: Define the successful response the mock model should return
    mock_model_response = {
        "Beginner": ["Subtopic 1", "Subtopic 2", "Subtopic 3"],
        "Intermediate": ["Subtopic 4", "Subtopic 5", "Subtopic 6"],
        "Advanced": ["Subtopic 7", "Subtopic 8", "Subtopic 9"],
    }
    mock_invoke = MagicMock(return_value=mock_model_response)
    monkeypatch.setattr(pipeline, "invoke_model_with_tools", mock_invoke)

    # 2. Execution: Run the method being tested
    success, categories, step_result = pipeline.step1_generate_difficulty_categories(topic="Test Topic")

    # 3. Assertion: Verify the results
    assert success is True
    assert categories == mock_model_response
    mock_invoke.assert_called_once()
    assert step_result.success is True
    assert step_result.step_number == 1

def test_step1_generate_difficulty_categories_failure_malformed(pipeline: CorrectedSevenStepPipeline, monkeypatch):
    """
    Tests a failed run of Step 1 where the model returns malformed data (e.g., not a dict).
    """
    # 1. Setup: Define a malformed response
    mock_model_response = "I am just a string, not a dictionary."
    mock_invoke = MagicMock(return_value=mock_model_response)
    monkeypatch.setattr(pipeline, "invoke_model_with_tools", mock_invoke)

    # 2. Execution
    success, categories, step_result = pipeline.step1_generate_difficulty_categories(topic="Test Topic")

    # 3. Assertion
    assert success is False
    assert categories == {}  # Should return an empty dict on failure
    mock_invoke.assert_called_once()
    assert step_result.success is False

def test_step1_generate_difficulty_categories_failure_incomplete(pipeline: CorrectedSevenStepPipeline, monkeypatch):
    """
    Tests a failed run of Step 1 where the model returns incomplete data (missing keys).
    """
    # 1. Setup: Define an incomplete response
    mock_model_response = {
        "Beginner": ["Subtopic 1", "Subtopic 2", "Subtopic 3"],
        # Missing "Intermediate" and "Advanced"
    }
    mock_invoke = MagicMock(return_value=mock_model_response)
    monkeypatch.setattr(pipeline, "invoke_model_with_tools", mock_invoke)

    # 2. Execution
    success, categories, step_result = pipeline.step1_generate_difficulty_categories(topic="Test Topic")

    # 3. Assertion
    assert success is False
    assert categories == {}
    mock_invoke.assert_called_once()
    assert step_result.success is False

def test_step2_generate_error_catalog_success(pipeline: CorrectedSevenStepPipeline, monkeypatch):
    """
    Tests a successful run of Step 2, verifying it correctly parses a valid error catalog.
    """
    # 1. Setup
    mock_model_response = {
        "errors": [
            {"mistake": "off-by-one"}, {"mistake": "wrong-variable"}, {"mistake": "bad-logic"},
            {"mistake": "typo"}, {"mistake": "misunderstanding"}, {"mistake": "edge-case"}
        ]
    }
    mock_invoke = MagicMock(return_value=mock_model_response)
    monkeypatch.setattr(pipeline, "invoke_model_with_tools", mock_invoke)

    # 2. Execution
    success, errors, step_result = pipeline.step2_generate_error_catalog("Topic", "Subtopic", "Beginner")

    # 3. Assertion
    assert success is True
    assert len(errors) == 6
    assert errors[0]["mistake"] == "off-by-one"
    mock_invoke.assert_called_once()
    assert step_result.success is True

def test_step2_generate_error_catalog_failure_not_enough_errors(pipeline: CorrectedSevenStepPipeline, monkeypatch):
    """
    Tests a failed run of Step 2 where the model returns too few errors.
    """
    # 1. Setup
    mock_model_response = {
        "errors": [
            {"mistake": "off-by-one"}
        ]
    }
    mock_invoke = MagicMock(return_value=mock_model_response)
    monkeypatch.setattr(pipeline, "invoke_model_with_tools", mock_invoke)

    # 2. Execution
    success, errors, step_result = pipeline.step2_generate_error_catalog("Topic", "Subtopic", "Beginner")

    # 3. Assertion
    assert success is False
    assert errors == []
    mock_invoke.assert_called_once()
    assert step_result.success is False
