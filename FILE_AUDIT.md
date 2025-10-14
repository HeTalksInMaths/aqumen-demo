# Repository File Audit — 2025-10-09

Snapshot of key files in `/Users/hetalksinmaths/adversarial demo` with local last-modified timestamps. Use this as a triage guide before pruning anything.

## Definitely Keep
| Path | Last Updated (local) | Why it matters |
| --- | --- | --- |
| `README.md` | 2025-09-13 10:09 | Current top-level overview reflecting the modular React + Bedrock architecture. |
| `backend/api_server.py` | 2025-10-09 11:31 | FastAPI service with SSE streaming; backs both Streamlit dev mode and React frontend. |
| `backend/corrected_7step_pipeline.py` | 2025-10-09 00:32 | Production pipeline implementation with Step 7 fixes, logging, and DB persistence. |
| `backend/aqumen_pipeline/` | 2025-10-09 12:00 | Modular pipeline package (prompts, tools, validators, orchestrator scaffolding) now used by the main pipeline. |
| `backend/bedrock_utils.py` | — (removed) | Remove legacy Streamlit helper; superseded by `backend/clients/bedrock.py`. |
| `backend/requirements.txt` / `backend/requirements-api.txt` | 2025-09-12 15:04 / 2025-10-09 00:32 | Keep both sets of dependencies (Streamlit vs FastAPI) in sync with current runtime. |
| `backend/debug_streaming.py` / `backend/test_step_by_step.py` / `backend/quick_test_sse.py` / `backend/quick_test_blocking.py` / `backend/test_api.py` | 2025-10-09 11:01–11:29 | Freshly updated diagnostic scripts that verify SSE streaming and blocking endpoints end-to-end. |
| `backend/pipeline_results.db` | 2025-10-09 11:34 | Active SQLite store written by the corrected pipeline for run history and Step 7 payloads. |
| `frontend/src/main.jsx` / `frontend/components/` / `frontend/hooks.js` / `frontend/utils.js` / `frontend/constants.js` / `frontend/package.json` / `frontend/vite.config.js` | 2025-09-12 13:01 – 2025-09-13 16:29 | Core React demo (original + modular views) and build configuration still in use. |
| `frontend-dev/streamlit_app.py` / `frontend-dev/requirements.txt` | 2025-10-09 11:50 / 2025-10-09 00:46 | Streamlit “Dev Mode” UI that consumes the SSE API for debugging and stakeholder demos. |
| `docs/FRONTEND_INTEGRATION.md` | 2025-10-08 20:47 | Latest integration checklist between React, FastAPI, and Streamlit. |
| `docs/AWS_BEDROCK_SETUP.md` | 2025-09-13 22:11 | Canonical Bedrock access guide; newer than the duplicated setup docs. |
| `docs/TOOLS_DOCUMENTATION.md` / `docs/current_pipeline_prompts.md` / `docs/project_rebuild_roadmap.md` | 2025-09-15 05:39 – 2025-10-02 14:52 | Living references for prompt design, toolchain, and rebuild milestones. |
| `DEPLOYMENT_GUIDE.md` / `SSE_IMPLEMENTATION_SUMMARY.md` / `DEBUGGING_RESULTS.md` | 2025-10-09 00:51 – 2025-10-09 11:38 | Document the current three-surface deployment strategy plus the October 9 SSE fixes. |
| `examples/gold_standard_examples.md` / `examples/hardcoded_demo_data.js` / `examples/corrected_pipeline_gold_standard.md` / `examples/corrected_pipeline_scoring.md` / `examples/updated_adversarial_rubric.md` | 2025-09-13 09:46 – 2025-09-14 00:02 | Reference datasets and scoring rubrics that seed both frontend demos and backend validation. |

## Needs Review (Maybe Deprecate or Archive)
| Path | Last Updated (local) | Why review |
| --- | --- | --- |
| `backend/demo_light_app.py` / `backend/demo_light_app_fixed.py` | 2025-09-14 11:12 / 11:41 | Older Streamlit frontends superseded by `frontend-dev/streamlit_app.py`; keep only if you still demo the non-SSE variant. |
| `backend/full_7step_pipeline.py` | 2025-09-13 22:39 | Pre-“corrected” pipeline; audit differences and archive if no longer referenced. |
| `backend/agentic_optimizer.py` / `backend/agentic_detailed.txt` / `backend/quick_baseline_test.py` / `backend/mass_experiment_plan.py` | 2025-09-13 22:29 – 2025-09-14 11:01 | Batch experimentation scaffold; decide whether these high-cost test harnesses are still part of the roadmap. |
| `backend/bedrock_model_availability_test.py` / `backend/final_models_test.py` / `backend/test_sonnet_3_7.py` | 2025-09-13 20:21 – 2025-09-15 11:44 | One-off model access checks tied to older model IDs; refresh or remove. |
| `backend/live_e2e_test.py` | 2025-09-13 22:16 | Legacy Bedrock end-to-end script writing to `backend/pipeline_log.txt`; verify overlap with the corrected pipeline. |
| `backend/step7_new_format.json` / `backend/corrected_7step_results_20250913_233740.json` | 2025-09-13 23:37 – 2025-10-07 22:44 | Sample outputs retained for reference; archive to `/docs/samples/` or drop if no longer needed. |
| `backend/bedrock_quota_check_20251007_131634.json` / `backend/check_bedrock_quotas.py` | 2025-10-07 10:31 – 13:16 | Quota diagnostics; keep only if you plan recurring quota checks. |
| `backend/backend/pipeline_results.db` / `backend/backend/logs` | 2025-09-14 09:05 – 09:07 | Nested duplicate of the new logging structure; confirm nothing still writes here before deleting. |
| `docs/BEDROCK_SETUP.md` / `docs/README.md` / `docs/INSTRUCTIONS.md` / `docs/explain.md` / `docs/streamlit_demo_light_plan.md` | 2025-09-12 13:12 – 2025-09-14 08:39 | Earlier documentation superseded by newer guides; merge any unique notes, then retire. |
| `AI_BACKEND_SESSION_FOCUS.md` / `CLEANUP_ROADMAP.md` / `CLAUDE.md` | 2025-09-13 10:05 – 19:28 | Planning and policy docs—still useful for process context but consider consolidating now that this audit exists. |
| `frontend/original_demo.jsx` / `frontend/demo-modular.jsx` / `frontend/test.html` / `frontend/test.js` / `frontend/interactive-demo.html` | 2025-09-12 12:58 – 14:02 | Temporary comparison and test harnesses; keep only if side-by-side demo remains valuable. |
| `frontend/hardcoded_questions_example.jsx` | 2025-10-07 16:22 | Scratchpad for new question formats; either finish integration or move to `/examples/`. |
| `clean_request.json` / `request.json` / `response.json` / `simple_request.json` | 2025-09-13 17:09 – 17:16 | Sample Bedrock payloads; archive to docs or remove if they’re no longer referenced. |

## Safe to Delete (No Current Consumers)
| Path | Last Updated (local) | Why remove |
| --- | --- | --- |
| `bedrock_utils.py` (repo root) | — (removed) | Duplicate wrapper deleted; demo now uses sample data only. |
| `constants.js` (repo root) | 2025-09-13 10:55 | Legacy data for `src/demo.jsx`; superseded by `frontend/constants.js`. |
| `src/demo.jsx` | 2025-09-13 10:55 | Old React monolith kept outside `frontend/`; current builds use `frontend/src/`. |
| `5bec5674-660d-4777-bc44-98e925edf4f6.jsonl`, `62bfeb2e-71c7-46e8-99ff-7ccb128f242b.jsonl`, `6d9853f8-172b-4106-bbee-571da23b0475.jsonl`, `90c44e2a-3a8f-4eba-a572-7c18babbb1c2.jsonl` | 2025-09-13 11:44 | Autogen conversation logs (Codex/Claude transcripts); not required for the codebase. |
| `todo search results`, `todo_search_results.txt`, `react_mentions_last_100.txt`, `jules_mentions.txt`, `gemini_cli.md ` | 2025-09-13 12:05 – 22:16 | Scratch outputs from AI tooling; safe to drop. |
| `AWSCLIV2.pkg` | 2025-09-13 16:58 | Installer payload; large and not meant for source control. |
| `node_modules/`, `streamlit-env/`, `__pycache__/` | 2025-09-12 13:45 – 2025-09-13 06:03 | Regenerable build artefacts that should stay out of git. |
