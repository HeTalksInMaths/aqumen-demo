# Batch Run Checklist

Use this when spinning up a fresh session to run the 10-topic pipeline test and capture metrics.

## 1. Topics (initial set)
1. Quadratic equations  
2. Bayesian A/B testing  
3. Renewable energy grid management  
4. GDPR compliance  
5. Evidence-based nursing  
6. Macroeconomic policy  
7. Classical mechanics  
8. Software supply chain security  
9. Literary symbolism  
10. Digital accessibility

Feel free to edit `backend/batch_runner.py` if you want to swap any of these. Each scenario should surface deliberate errors or inconsistencies for the learner to flag.

## 2. Environment
- `cd /Users/hetalksinmaths/adversarial demo`
- `source .venv/bin/activate`
- Ensure FastAPI server is stopped (`lsof -i :8000` → kill if needed).

## 3. Run the batch
- `python backend/batch_runner.py`
  - Produces `backend/batch_results_<timestamp>.csv`
  - Prints summary + SQL metrics (via `analyze_sql.py`)

## 4. Artefacts to capture
- `backend/batch_results_<timestamp>.csv`
- `backend/results/metrics_<timestamp>.json` (for per-run rewards)
- `backend/logs/current/pipeline_run_<timestamp>.txt` (spot-check any failures)
- Output of `python backend/analyze_sql.py` (if you need to rerun separately)

## 5. Follow-up
- Inspect CSV for:
  - Final success / differentiation / validation rates
  - Token usage & cost per topic
  - Latency per topic
- Review SQLite summary for reward pass-rates & overall latency distribution.

## 6. Cleanup (optional)
- Archive logs/results if the run is final (`mv logs/current/* logs/archived/` etc.).
- Deactivate venv: `deactivate`.
