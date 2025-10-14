# Refactor & Test Remediation Priorities

## Highest Priority Files to Refactor

1. **`minimal/backend/corrected_7step_pipeline.py`** – At ~1.3k lines it entangles Bedrock client setup, pipeline orchestration, scoring, and persistence. Breaking it into per-step strategy classes, a shared `PipelineContext`, and dedicated service adapters will reduce cognitive load and enable unit seams around each step.【F:docs/MODULARIZATION_GUIDANCE.md†L7-L13】
2. **`minimal/backend/api_server.py`** – At ~600 lines the FastAPI entry point mixes routing, SSE streaming, and mock-mode helpers. Splitting routers by concern and encapsulating the streaming generators will shrink the surface area and improve testability for both live and mock modes.【F:docs/MODULARIZATION_GUIDANCE.md†L7-L16】
3. **`minimal/frontend/src/App.jsx`** – Nearly 600 lines of global state management, streaming orchestration, and UI layout. Extracting feature hooks (e.g., `usePipelineStream`) and route-level containers lets `App.jsx` focus on composition, clarifying data flow and easing incremental UI rewrites.【F:docs/MODULARIZATION_GUIDANCE.md†L21-L27】
4. **`minimal/frontend/src/demoData.dev.js`** – ~1k lines of embedded demo transcripts hinder maintainability. Moving the payloads into JSON under `src/data/` and supplying typed transformers keeps mock assets modular and reduces bundle weight.【F:docs/MODULARIZATION_GUIDANCE.md†L21-L27】
5. **`minimal/backend/bedrock_utils.py` & `minimal/backend/persistence/repo.py`** – Both exceed 250 lines and conflate configuration with runtime logic. Extracting Bedrock client factories/retry policies and splitting repository CRUD code by entity will clarify responsibilities and simplify injection in tests.【F:docs/MODULARIZATION_GUIDANCE.md†L11-L13】

These targets offer the largest payoff because they concentrate multiple responsibilities in single files, directly blocking isolation of business rules and driving the most painful merge conflicts.

## Highest Priority Testing Gaps & Fixes

1. **Backend persistence test coverage is narrow.** The lone pytest verifies happy-path inserts through `Repo` but never asserts schema migrations, error handling, or concurrent writes. Add fixture-backed tests that simulate failure modes (duplicate steps, rollback on exceptions) and exercise migration scripts so DB regressions surface early.【F:code_testing/backend/tests/test_repo.py†L16-L89】【F:code_testing/TEST_REPORT.md†L1-L11】
2. **Frontend API client tests miss streaming and environment nuances.** The Node test suite covers blocking fetches and transformer validation but lacks coverage for the EventSource-based streaming paths or browser-specific global usage. Introduce integration-style tests that stub `EventSource` and assert reconnection logic, plus guard rails for non-browser environments (e.g., SSR) to prevent regressions.【F:code_testing/frontend/tests/api.test.mjs†L1-L117】【F:code_testing/TEST_REPORT.md†L12-L13】
3. **No tests enforce modularization promises.** The current suites validate behavior but don’t ensure refactors keep side effects isolated. Add contract tests around new service boundaries (e.g., Bedrock client factory protocols, pipeline step strategies) once the refactors land to keep responsibilities separated.【F:docs/MODULARIZATION_GUIDANCE.md†L15-L33】

Tackling these testing gaps alongside the modularization work will create fast feedback for the most critical flows (pipeline execution and frontend assessment rendering) and reduce the risk of regressions during the planned refactors.
