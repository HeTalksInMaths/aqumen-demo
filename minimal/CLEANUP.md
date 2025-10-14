# Cleanup Plan for `minimal/` Directory

This document lists files and directories within the `minimal/` folder that are likely candidates for cleanup, as they do not appear to be part of the core application flow.

## Backend Cleanup Candidates

### Old Pipeline Version
- **`minimal/backend/aqumen_pipeline_v2/`**: This entire directory seems to be an older version of the pipeline and can likely be removed.

### Old Backend Files
- **`minimal/backend/bedrock_utils.py`**: Appears to be replaced by the more modular `minimal/backend/clients/bedrock.py`.

### One-off & Test Scripts
- `minimal/backend/append_to_demo.py`
- `minimal/backend/load_from_database.py`
- `minimal/backend/sync_prompts.py`
- `minimal/backend/test_content_marketing.py`
- `minimal/backend/test_step7_direct.py`

### Temporary JSON Files
- `minimal/backend/prompts_changes.json`
- `minimal/backend/tools_changes.json`
- `minimal/backend/frontend_demo_data_exec.json`
- `minimal/backend/frontend_demo_data_quadratic.json`

### Documentation & Analysis Files
- `minimal/backend/PIPELINE_TEST_ANALYSIS_20251012.md`
- `minimal/backend/PROMPT_EDITING_README.md`
- `minimal/backend/STEP7_FIX_IMPLEMENTATION.md`
- `minimal/backend/GRAPH_NETWORK_FRAUD_ANALYSIS.md`
- `minimal/backend/WHY_ANTHROPIC_ANALYSIS.md`
- `minimal/backend/STEP7_VALIDATION_ANALYSIS.md`

## Frontend Cleanup Candidates

### One-off Scripts
- `minimal/frontend/src/fix_demo_data.py`

### Documentation & Notes
- `minimal/frontend/CLEANUP_INSTRUCTIONS.md`
- `minimal/frontend/summary.md`

## Root `minimal/` Folder Documentation
- `minimal/UPDATE.md`
- `minimal/FRONTEND_DEBUG_SUMMARY.md`
- `minimal/REFACTORING_PLAN.md`
- `minimal/SESSION_SUMMARY.md`
- `minimal/README.md` (Consider merging with the main `README.md` if it contains relevant info)
