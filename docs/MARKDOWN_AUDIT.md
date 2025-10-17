# Markdown File Audit (2025-10-13)

## Methodology
- Enumerated non-dependency `.md` files across the repository and reviewed their contents.
- Collected the original commit dates via `git log --follow` to understand document freshness.
- Cross-checked each plan against the current code to decide whether the guidance is still actionable or has already been superseded.

## Summary Table
| Path | First Commit | Status | Notes |
| --- | --- | --- | --- |
| `README.md` | 2025-10-13 | ⚠️ Needs refresh | Still describes the older `adversarial demo/` layout even though only `minimal/` remains in the repo. |
| `minimal/README.md` | 2025-10-10 | ✅ Current | Accurate overview of the production-ready bundle and its deployment story. |
| `minimal/UPDATE.md` | 2025-10-13 | ❌ Superseded | Calls for restoring `demoData.js`, but the student demo content already lives in `demoData.student.js`. |
| `minimal/REFACTORING_PLAN.md` | 2025-10-13 | ⚠️ In progress | Outlines breaking the monolith into modules; only partially realized. |
| `minimal/SESSION_SUMMARY.md` | 2025-10-13 | 📎 Historical | Useful log of the October 11 session; no direct actions remaining. |
| `minimal/FRONTEND_DEBUG_SUMMARY.md` | 2025-10-13 | ⚠️ Partially resolved | Dev-mode prompt placeholders now exist, but the logging/debug suggestions still apply. |
| `minimal/frontend/CLEANUP_INSTRUCTIONS.md` | 2025-10-13 | ❌ Superseded | Mentions deleting inline GRPO data that has already been removed. |
| `minimal/frontend/summary.md` | 2025-10-13 | ✅ Current | Documents the new componentization and blueprint placeholder work. |
| `minimal/backend/STEP7_FIX_IMPLEMENTATION.md` | 2025-10-13 | ✅ Current | Matches the implemented auto-fix and validator changes in the pipeline. |
| `minimal/backend/PIPELINE_TEST_ANALYSIS_20251012.md` | 2025-10-13 | ✅ Current | Latest benchmark of the pipeline with pending follow-up work on evidence quotes. |
| `minimal/backend/PROMPT_EDITING_README.md` | 2025-10-13 | ❌ Superseded | States prompts are hard-coded, but the pipeline now loads them through `config.load_prompts()`. |
| `minimal/backend/aqumen_pipeline_v2/ARCHITECTURE.md` & `CHECKLIST.md` | 2025-10-13 | ⚠️ Planning | Forward-looking design for v2 modularization; implementation not yet wired in. |
| `docs/README.md` | 2025-10-10 | 📎 Historical | Documents the pre-minimal architecture split; helpful for context but not the active build. |
| `docs/BEDROCK_SETUP.md` & `docs/AWS_BEDROCK_SETUP.md` | 2025-10-10 | ✅ Current | Still the definitive Bedrock credentialing guide. |
| `docs/INSTRUCTIONS.md` | 2025-10-10 | ❌ Superseded | References `test.html` browser demos that are no longer present. |
| `docs/prompt_improvements.md` | 2025-10-10 | ⚠️ Review | Deep prompt upgrade ideas—worth revisiting if prompt quality becomes an issue. |
| `docs/explain.md` | 2025-10-10 | 📎 Historical | Explains the modular frontend for data scientists; aligned with legacy `constants.js` build. |

## Detail Notes

### Root README needs to be aligned with the minimal bundle
The root `README.md` still lists directories such as `frontend/`, `backend/`, and `examples/` under `adversarial demo/`, which no longer exist after the October 13 consolidation.【F:README.md†L5-L133】【6b06ae†L1-L2】 Consider rewriting it to point to the `minimal/` package instead (mirroring the accurate structure already captured in `minimal/README.md`).【F:minimal/README.md†L9-L139】

### Student demo data already restored
`minimal/UPDATE.md` prioritizes copying back `demoData.js`, but the student-mode assessments now live in `minimal/frontend/src/demoData.student.js` and cover the original 10-question set. Attempting to open the old path fails because the file was split, confirming this document is outdated.【F:minimal/UPDATE.md†L1-L64】【8cac21†L1-L2】【F:minimal/frontend/src/demoData.student.js†L1-L200】

### Frontend debug guidance vs. current state
The debug summary reports that prompts are inaccessible before a live run, suggesting placeholder blueprints or prompt loading as fixes.【F:minimal/FRONTEND_DEBUG_SUMMARY.md†L44-L105】 The follow-up session summary confirms that static placeholders were added and backed by Playwright coverage, so only the logging diagnostics remain to implement.【F:minimal/frontend/summary.md†L3-L17】

### Prompt editing doc needs an update
`PROMPT_EDITING_README.md` labels JSON loading as “pending,” yet the pipeline constructor now calls `load_prompts()` directly, meaning edits flow through without manual syncing.【F:minimal/backend/PROMPT_EDITING_README.md†L20-L175】【F:minimal/backend/corrected_7step_pipeline.py†L19-L138】 Refreshing that README to describe the new config loader (and documenting `prompts_changes.json`) would prevent confusion.

### Backend validation work is complete but has follow-ups
The Step 7 implementation summary describes the new JSON-schema tightening and auto-fix layer, and those changes are present in the codebase, so the doc remains authoritative.【F:minimal/backend/STEP7_FIX_IMPLEMENTATION.md†L1-L150】【F:minimal/backend/corrected_7step_pipeline.py†L98-L160】 Meanwhile, the October 12 pipeline analysis highlights lingering judge evidence gaps and performance timings that should stay on the radar for future prompt tuning.【F:minimal/backend/PIPELINE_TEST_ANALYSIS_20251012.md†L1-L188】

### Planning documents worth tracking
The refactoring plan and the v2 architecture/checklist were all committed on October 13 but have not yet been executed beyond creating the `aqumen_pipeline_v2` scaffold. Use them as the authoritative roadmap when modularization restarts.【F:minimal/REFACTORING_PLAN.md†L1-L105】【F:minimal/backend/aqumen_pipeline_v2/aqumen_pipeline/ARCHITECTURE.md†L1-L33】【F:minimal/backend/aqumen_pipeline_v2/CHECKLIST.md†L1-L21】

### Legacy docs for historical context
`docs/README.md`, `docs/explain.md`, and `docs/prompt_improvements.md` all date back to September/October 2025 and describe the original modular demo or aspirational prompt work. Keep them for institutional memory, but prioritize the `minimal/` documentation for day-to-day operations.【F:docs/README.md†L1-L55】【F:docs/explain.md†L1-L90】【48d37b†L1-L2】

### Deprecated browser instructions
`docs/INSTRUCTIONS.md` still references a `test.html` comparison harness that no longer exists in the repo, so the guide can be archived or revised to point to the Vite-based minimal frontend instead.【F:docs/INSTRUCTIONS.md†L1-L54】【8e27e5†L1-L2】
