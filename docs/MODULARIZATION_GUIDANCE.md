# Backend & Frontend Modularization Guidance

Line counts were collected with `wc -l` on April 14, 2025 to highlight oversized files. The recommendations below focus on splitting responsibilities and isolating pure logic for easier testing.

## Backend Hotspots

| File | ~Lines | Why It Is Large | Suggested Modularization |
| --- | --- | --- | --- |
| `minimal/backend/corrected_7step_pipeline.py` | 1342 | Orchestrates the full 7-step pipeline, manages Bedrock clients, scoring, persistence, and logging. | Extract per-step strategy objects (e.g., `steps/step1_strategy.py`), move Bedrock client bootstrap into `services/bedrock.py`, and isolate persistence/reporting adapters. Introduce a `PipelineContext` dataclass passed between steps. |
| `minimal/backend/api_server.py` | 587 | Contains FastAPI setup, request models, streaming SSE wiring, and mock-mode logic. | Split FastAPI routers into `/routers/generation.py`, `/routers/meta.py`, and `/routers/health.py`. Move mock-pipeline helpers into a dedicated module and encapsulate SSE streaming generator functions. |
| `minimal/backend/load_from_database.py` | 347 | Mixes data loading utilities, prompt hydration, and CLI helpers. | Separate pure data-access helpers into `persistence/queries.py` and keep CLI/formatting code inside a `cli/` command module. |
| `minimal/backend/bedrock_utils.py` | 345 | Combines credential management, retry logic, and response normalization. | Create a `bedrock/client_factory.py` for configuration, `bedrock/retry.py` for exponential backoff policies, and keep response-normalization utilities in `bedrock/parsers.py`. |
| `minimal/backend/persistence/repo.py` | 254 | Implements connection pooling, schema creation, and CRUD helpers for multiple tables. | Promote schema DDL into migrations (e.g., `persistence/migrations/0001_init.sql`) and split CRUD operations by entity (`runs_repository.py`, `step_repository.py`, `reward_repository.py`). |

**Quick Wins**
- Introduce interfaces (`Protocol`s) for Bedrock and persistence layers so the pipeline orchestrator can be unit tested with fakes.
- Promote analytics routines (`analytics/rewards`) into a service layer that returns typed DTOs, reducing cross-module coupling.

## Frontend Hotspots

| File | ~Lines | Why It Is Large | Suggested Modularization |
| --- | --- | --- | --- |
| `minimal/frontend/src/demoData.dev.js` | 1008 | Bundles extensive mock pipeline transcripts directly in JS. | Move static demo data into JSON files under `src/data/` and lazy-load them; provide typed transformers to map the JSON into runtime structures. |
| `minimal/frontend/src/App.jsx` | 597 | Handles application state, demo-vs-live toggles, streaming orchestration, and UI composition in one component. | Decompose into feature hooks (`usePipelineStream`, `useDemoAssessments`) and route-level containers (`StudentExperience`, `DeveloperWorkbench`). Keep `App.jsx` focused on routing and layout. |
| `minimal/frontend/src/components/PipelinePanel.jsx` | 325 | Renders tabs, step timelines, and developer/dev-mode toggles together. | Break into `PipelineTabs`, `StepTimeline`, and `DeveloperControls` components with prop drilling replaced by context hooks. |
| `minimal/frontend/src/components/QuestionPlayground.jsx` | 291 | Mixes question parsing, answer submission, and scoring logic. | Extract parsing helpers into `utils/questionFormatting.js` and use child components for code editor, answer list, and scoring summary. |
| `minimal/frontend/src/api.js` | 231 | Centralizes blocking/streaming requests, prompt fetching, and EventSource wiring. | Promote pure transformers (e.g., `transformStep7ToReact`) into `api/transformers.js`, isolate streaming lifecycle into `api/streaming.js`, and expose a small typed client interface consumed by hooks. |

**Additional Notes**
- Shared constants (difficulty levels, pipeline step metadata) should move into `src/constants/` to avoid duplicate literals across components.
- Custom hooks encapsulating fetch logic (`usePrompts`, `useHealthCheck`) will simplify `App.jsx` and make side effects explicit.

These refactors will shrink per-file scope, ease onboarding for new contributors, and give the new unit tests clearer seams to mock external dependencies.
