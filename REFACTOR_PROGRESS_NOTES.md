# Pipeline Refactor Progress Notes

## Completed So Far
- Prompts/tools aligned with the modular aqumen pipeline (Steps 1–7 updated).
- Step 6 judge interaction now returns structured `failures_weaker`; Step 7 consumes the new schema and validator checks the v2 contract (`content_type` + `content`).
- Bedrock runtime/roles/persistence extracted from the v2 repo:
  - `clients/bedrock.py` and `services/invoke.py` wrap all model calls.
  - `roles.py` loads model IDs from env vars (`AQU_MODEL_*`) with `supports_thinking` flag.
  - `persistence/repo.py` handles `enhanced_*` tables plus `step_rewards`, and `CorrectedSevenStepPipeline` now uses it.
- Rewards telemetry hooked up: each step logs a `StepRewardsReport` to SQLite + `results/metrics_<ts>.json`.
- Final run artifact written to `corrected_7step_results_<ts>.json` (mirrors orchestrator behavior).
- Duplicate legacy pipeline scripts in `backend/` removed to avoid confusion.
- Retired the legacy `bedrock_utils.py` modules; Streamlit now defaults to demo mode until a new live Bedrock hook is wired in.
- Shared datatypes, validators, prompts, and tool schemas now live under `backend/aqumen_pipeline/`; the pipeline imports them instead of inline definitions.

## Outstanding / To-Do
1. **Legacy files under `backend/`**
   - Many helper scripts/tests still reference old implementations. Decide whether to remove or adapt them to the new pipeline.
2. **Frontend prompt loading**
   - The React UI used to pull prompts from JSON via the backend. After the refactor (prompts/tools now loaded from config + `_changes` overlays), verify the frontend still reads/updates correctly once the API server is running.
3. **Testing**
   - Run the end-to-end pipeline using the new `minimal/backend/run_pipeline.py` once AWS creds are available, and update any unit/integration tests.
4. **Documentation**
   - Update README / deployment notes to point to the new module structure (`minimal/backend/...`).

## Next Session Checklist
- Sweep `backend/` for remaining redundant files.
- Bring the frontend prompt UI online with the new JSON loaders and confirm edits flow through the API into `prompts_changes.json`.
- Run lint/tests after above changes, then final diff review against the aqumen_pipeline_v2 folder.
