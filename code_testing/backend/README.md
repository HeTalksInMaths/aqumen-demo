# Backend Test Harness

- **Framework:** [Pytest](https://docs.pytest.org/).
- **Scope:** Validates that `Repo` correctly bootstraps SQLite storage, records pipeline steps, aggregates reward metadata, and marks run completion.
- **Test Files:**
  - `tests/test_repo.py`
- **Running Tests:** From repository root run:
  ```bash
  python -m pytest code_testing/backend/tests
  ```
- **Dependencies:** Listed in `requirements.txt`. Install with:
  ```bash
  pip install -r code_testing/backend/requirements.txt
  ```
