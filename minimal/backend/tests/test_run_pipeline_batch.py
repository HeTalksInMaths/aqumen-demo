import io
import json
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
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

if "openai" not in sys.modules:
    sys.modules["openai"] = MagicMock()

from minimal.backend import run_pipeline_batch


class RunPipelineBatchCLITests(TestCase):
    """Confirms the CLI wrapper forwards topics correctly."""

    def setUp(self):
        self.argv_backup = list(sys.argv)

    def tearDown(self):
        sys.argv = self.argv_backup

    def test_cli_with_file_argument(self):
        """`--file` should load topics from disk and pass them to main()."""
        topics = ["topic_from_file_1", "topic_from_file_2"]
        with tempfile.TemporaryDirectory() as tmp_dir:
            dataset_file = Path(tmp_dir) / "test_dataset.json"
            dataset_file.write_text(json.dumps(topics), encoding="utf-8")

            sys.argv = ["run_pipeline_batch.py", "--file", str(dataset_file)]
            with patch.object(run_pipeline_batch, "main", MagicMock()) as mock_main:
                run_pipeline_batch.run_from_cli()
                mock_main.assert_called_once()
                args, kwargs = mock_main.call_args
                self.assertEqual(list(args[0]), topics)
                self.assertFalse(kwargs["parallel"])
                self.assertEqual(kwargs["max_workers"], run_pipeline_batch.DEFAULT_WORKERS)

    def test_cli_with_positional_arguments(self):
        """Passing topics as positional args should invoke main() with them."""
        topics = ["Topic_A", "Topic_B", "Topic_C"]
        sys.argv = ["run_pipeline_batch.py", *topics]
        with patch.object(run_pipeline_batch, "main", MagicMock()) as mock_main:
            run_pipeline_batch.run_from_cli()
            mock_main.assert_called_once()
            args, kwargs = mock_main.call_args
            self.assertEqual(list(args[0]), topics)
            self.assertFalse(kwargs["parallel"])
            self.assertEqual(kwargs["max_workers"], run_pipeline_batch.DEFAULT_WORKERS)

    def test_cli_with_parallel_flag(self):
        """`--parallel` should toggle parallel execution and respect worker overrides."""
        topics = ["Topic_A", "Topic_B"]
        sys.argv = ["run_pipeline_batch.py", "--parallel", "--workers", "3", *topics]
        with patch.object(run_pipeline_batch, "main", MagicMock()) as mock_main:
            run_pipeline_batch.run_from_cli()
            mock_main.assert_called_once()
            args, kwargs = mock_main.call_args
            self.assertEqual(list(args[0]), topics)
            self.assertTrue(kwargs["parallel"])
            self.assertEqual(kwargs["max_workers"], 3)

    def test_cli_with_no_arguments(self):
        """No arguments should exit and emit a usage hint."""
        sys.argv = ["run_pipeline_batch.py"]
        with patch.object(run_pipeline_batch, "main", MagicMock()) as mock_main:
            stderr_buffer = io.StringIO()
            stdout_buffer = io.StringIO()
            with self.assertRaises(SystemExit):
                with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                    run_pipeline_batch.run_from_cli()

            mock_main.assert_not_called()
            combined_output = stdout_buffer.getvalue() + stderr_buffer.getvalue()
            self.assertIn("usage:", combined_output)
            self.assertIn("No topics provided", combined_output)


if __name__ == "__main__":
    main()
