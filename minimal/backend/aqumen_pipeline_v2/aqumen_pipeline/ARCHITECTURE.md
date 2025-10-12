# Aqumen Pipeline — Architecture (v2)

## Goals
- Domain-agnostic 7-step pipeline with interchangeable models (judge / mid-tier / weak-tier).
- Prompts tuned to reduce retriability; tools enforce structure.
- Verifiable rewards are **soft metrics** to track prompt quality regressions (not gates).
- Only functional gate: Step-7 validator + retry.

## Modules
- `config.py` — constants, paths, limits.
- `roles.py` — model role registry (env-driven IDs).
- `datatypes.py` — `PipelineStep`, `SevenStepResult`.
- `tools/schemas.py` — factory functions for tool schemas (`match_hint` replaces `code_pattern`).
- `prompts/builders.py` — final prompts (v2): explicit inputs, keys/counts, domain-agnostic.
- `validators/assessment.py` — Step-7 validator with auto-fix & diagnostics (functional gate).
- `analytics/rewards.py` — soft, per-step verifiable rewards; pass-rate roll-up.
- `clients/bedrock.py` — thin Bedrock runtime wrapper (lazy boto3 import).
- `services/invoke.py` — Invoker orchestrating simple calls with/without tools.
- `persistence/repo.py` — SQLite repo & JSON artifacts; includes `step_rewards` table.
- `pipeline/orchestrator.py` — coordinator: runs steps, logs, runs rewards (soft), uses Step-7 validator.
- `run_pipeline.py` — entry point scaffold.

## Data Flow
1. **Step 1** → difficulty buckets (exact keys).  
2. **Step 2** → error catalog with `match_hint`, likelihoods, impact.  
3. **Step 3** → strategic question referencing a subset of catalog names (`target_error_patterns`).  
4. **Step 4/5** → two implementations (mid / weak).  
5. **Step 6** → judge returns `failures_weaker` **subset of catalog names** (plus optional evidence).  
6. **Step 7** → assessment selecting 2–5 mistakes **from `failures_weaker`** only; validator cleans & may retry.

## Persistence
- `enhanced_pipeline_runs` — run metadata.
- `enhanced_step_responses` — full step payloads.
- `step_rewards` — per-step soft metrics (`pass_rate`, `num_tests`, `detail_json`).
- Files:
  - `logs/current/pipeline_run_<ts>.txt` (append-only)
  - `results/metrics_<ts>.json` (soft rewards snapshot)
  - `backend/corrected_7step_results_<ts>.json` (batch results)
