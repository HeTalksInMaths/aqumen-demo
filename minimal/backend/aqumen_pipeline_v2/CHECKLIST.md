# Verification Checklist

## Structural
- [ ] Env vars resolve for model IDs (AQU_MODEL_*); `roles.py` loads.
- [ ] SQLite tables created; `step_rewards` present.
- [ ] Log dirs exist; `logs/current/pipeline_run_<ts>.txt` appended.

## Step Integration
- [ ] Step 1: exact keys; rewards show `keys_exact=True`.
- [ ] Step 2: EXACTLY 6 mistakes; `match_hint` present (alias from `code_pattern` OK).
- [ ] Step 3: includes `artifact_type`, 4–6 `requirements`, guidance from catalog names.
- [ ] Step 4/5: outputs have all three sections; 24–120 non-empty lines.
- [ ] Step 6: prompt shows names only; returns `failures_weaker` ⊆ catalog.
- [ ] Step 7: uses failures_weaker only; validator OK or retries up to STEP7_MAX_ATTEMPTS.

## Rewards Telemetry
- [ ] After each step, `step_rewards` row written (pass_rate + details).
- [ ] `results/metrics_<ts>.json` contains per-step pass-rates and results.

## Back-compat & Naming
- [ ] Old `code_pattern` mapped to `match_hint`.
- [ ] Role names: judge / mid-tier / weak-tier (no vendor names).

## Prompt Conformance
- [ ] Step 6 “KNOWN ERROR PATTERNS” lists full catalog names (no truncation).
- [ ] Step 7: single-line spans; 24–60 lines; 1–5 errors.

## Future Tests
- [ ] CI non-regression: compare pass_rate to baseline JSON (fail on drop > ε).
- [ ] Optional modality plug-ins for richness rewards (code/math/table...).
- [ ] Calibration metrics logged when Step-6 returns failures_weaker.
