import sys
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Import the script we are testing
from .. import run_pipeline_batch

@pytest.fixture
def mock_main_function(monkeypatch):
    """Replaces the real main function with a mock so we can check if it's called correctly."""
    mock = MagicMock()
    monkeypatch.setattr(run_pipeline_batch, "main", mock)
    return mock

def test_cli_with_file_argument(mock_main_function, tmp_path: Path, monkeypatch):
    """Verify the script calls main() with topics from a JSON file specified by --file."""
    # 1. Setup
    topics = ["topic_from_file_1", "topic_from_file_2"]
    dataset_file = tmp_path / "test_dataset.json"
    dataset_file.write_text(json.dumps(topics))

    # Simulate command-line arguments: `python script.py --file <path>`
    monkeypatch.setattr(sys, "argv", ["run_pipeline_batch.py", "--file", str(dataset_file)])

    # 2. Execution
    run_pipeline_batch.run_from_cli()

    # 3. Assertion
    mock_main_function.assert_called_once_with(topics)

def test_cli_with_positional_arguments(mock_main_function, monkeypatch):
    """Verify the script calls main() with topics passed as direct arguments."""
    # 1. Setup
    topics = ["Topic_A", "Topic_B", "Topic_C"]
    
    # Simulate command-line arguments: `python script.py Topic_A Topic_B ...`
    monkeypatch.setattr(sys, "argv", ["run_pipeline_batch.py"] + topics)

    # 2. Execution
    run_pipeline_batch.run_from_cli()

    # 3. Assertion
    mock_main_function.assert_called_once_with(topics)

def test_cli_with_no_arguments(mock_main_function, monkeypatch, capsys):
    """Verify the script exits and prints help when no arguments are given."""
    # 1. Setup
    # Simulate command-line arguments: `python script.py`
    monkeypatch.setattr(sys, "argv", ["run_pipeline_batch.py"])

    # 2. Execution & Assertion
    with pytest.raises(SystemExit):
        run_pipeline_batch.run_from_cli()

    # Check that the main function was NOT called
    mock_main_function.assert_not_called()

    # Check that a help message was printed to stderr
    captured = capsys.readouterr()
    assert "usage:" in captured.err
    assert "No topics provided" in captured.err
