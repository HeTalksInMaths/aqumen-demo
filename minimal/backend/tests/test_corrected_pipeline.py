import sys
from pathlib import Path
from unittest import TestCase, main
from unittest.mock import MagicMock, patch

# Ensure the repository root is importable when running as a script.
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Stub optional dependencies so the pipeline module imports cleanly.
if "openai" not in sys.modules:
    sys.modules["openai"] = MagicMock()

from minimal.backend.corrected_7step_pipeline import CorrectedSevenStepPipeline


class CorrectedPipelineTests(TestCase):
    """Validates early pipeline steps using lightweight mocks."""

    def setUp(self):
        """Patch heavyweight dependencies so tests execute in isolation."""
        self.roles_patcher = patch(
            "minimal.backend.corrected_7step_pipeline.load_model_roles",
            return_value={
                "judge": MagicMock(id="claude-3-opus-20240229", supports_thinking=True),
                "mid": MagicMock(id="claude-3-sonnet-20240229"),
                "weak": MagicMock(id="claude-3-haiku-20240307"),
            },
        )
        self.prompts_patcher = patch(
            "minimal.backend.corrected_7step_pipeline.load_prompts",
            return_value={
                "step1_difficulty_categories": {"template": "..."},
                "step2_error_catalog": {"template": "..."},
            },
        )
        self.tools_patcher = patch(
            "minimal.backend.corrected_7step_pipeline.load_tools",
            return_value={
                "step1_difficulty_categories": [{}],
                "step2_error_catalog": [{}],
            },
        )
        self.bedrock_patcher = patch("minimal.backend.corrected_7step_pipeline.BedrockRuntime", MagicMock())
        self.invoker_patcher = patch("minimal.backend.corrected_7step_pipeline.Invoker", MagicMock())
        self.repo_patcher = patch("minimal.backend.corrected_7step_pipeline.Repo", MagicMock())

        for patcher in (
            self.roles_patcher,
            self.prompts_patcher,
            self.tools_patcher,
            self.bedrock_patcher,
            self.invoker_patcher,
            self.repo_patcher,
        ):
            patcher.start()

        self.addCleanup(self.roles_patcher.stop)
        self.addCleanup(self.prompts_patcher.stop)
        self.addCleanup(self.tools_patcher.stop)
        self.addCleanup(self.bedrock_patcher.stop)
        self.addCleanup(self.invoker_patcher.stop)
        self.addCleanup(self.repo_patcher.stop)

        self.pipeline = CorrectedSevenStepPipeline()

    def test_step1_generate_difficulty_categories_success(self):
        """Step 1 succeeds when the model returns a complete difficulty map."""
        mock_model_response = {
            "Beginner": ["Subtopic 1", "Subtopic 2", "Subtopic 3"],
            "Intermediate": ["Subtopic 4", "Subtopic 5", "Subtopic 6"],
            "Advanced": ["Subtopic 7", "Subtopic 8", "Subtopic 9"],
        }
        with patch.object(self.pipeline, "invoke_model_with_tools", return_value=mock_model_response) as mock_invoke:
            success, categories, step_result = self.pipeline.step1_generate_difficulty_categories("Test Topic")

        self.assertTrue(success)
        self.assertEqual(categories, mock_model_response)
        mock_invoke.assert_called_once()
        self.assertTrue(step_result.success)
        self.assertEqual(step_result.step_number, 1)

    def test_step1_generate_difficulty_categories_failure_malformed(self):
        """Step 1 fails gracefully when a non-mapping payload arrives."""
        malformed_response = "I am just a string, not a dictionary."
        with patch.object(self.pipeline, "invoke_model_with_tools", return_value=malformed_response) as mock_invoke:
            success, categories, step_result = self.pipeline.step1_generate_difficulty_categories("Test Topic")

        self.assertFalse(success)
        self.assertEqual(categories, {})
        mock_invoke.assert_called_once()
        self.assertFalse(step_result.success)

    def test_step1_generate_difficulty_categories_failure_incomplete(self):
        """Step 1 rejects responses that omit required difficulty tiers."""
        incomplete_response = {
            "Beginner": ["Subtopic 1", "Subtopic 2", "Subtopic 3"],
            # Missing Intermediate/Advanced
        }
        with patch.object(self.pipeline, "invoke_model_with_tools", return_value=incomplete_response) as mock_invoke:
            success, categories, step_result = self.pipeline.step1_generate_difficulty_categories("Test Topic")

        self.assertFalse(success)
        self.assertEqual(categories, {})
        mock_invoke.assert_called_once()
        self.assertFalse(step_result.success)

    def test_step2_generate_error_catalog_success(self):
        """Step 2 succeeds with a full six-item error list."""
        response = {
            "errors": [
                {"mistake": "off-by-one"},
                {"mistake": "wrong-variable"},
                {"mistake": "bad-logic"},
                {"mistake": "typo"},
                {"mistake": "misunderstanding"},
                {"mistake": "edge-case"},
            ]
        }
        with patch.object(self.pipeline, "invoke_model_with_tools", return_value=response) as mock_invoke:
            success, errors, step_result = self.pipeline.step2_generate_error_catalog("Topic", "Subtopic", "Beginner")

        self.assertTrue(success)
        self.assertEqual(len(errors), 6)
        self.assertEqual(errors[0]["mistake"], "off-by-one")
        mock_invoke.assert_called_once()
        self.assertTrue(step_result.success)

    def test_step2_generate_error_catalog_failure_not_enough_errors(self):
        """Step 2 flags incomplete error catalogs."""
        response = {"errors": [{"mistake": "off-by-one"}]}
        with patch.object(self.pipeline, "invoke_model_with_tools", return_value=response) as mock_invoke:
            success, errors, step_result = self.pipeline.step2_generate_error_catalog("Topic", "Subtopic", "Beginner")

        self.assertFalse(success)
        self.assertEqual(errors, [])
        mock_invoke.assert_called_once()
        self.assertFalse(step_result.success)


if __name__ == "__main__":
    main()
