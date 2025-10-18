# Backend Refactoring Plan

## Overview
This document outlines the refactoring strategy for the largest backend files, following the modular pattern established in `aqumen_pipeline_v2/`.

## Files Requiring Refactoring

### Priority 1: corrected_7step_pipeline.py (1,378 lines)

**Current Issues:**
- Single monolithic file with 1,378 lines
- Mixes concerns: pipeline orchestration, step execution, validation, logging, database operations
- 4 complex functions detected by ruff (C901)
- Difficult to test individual components

**Refactoring Strategy:**
Follow the `aqumen_pipeline_v2/aqumen_pipeline/` pattern:

```
minimal/backend/
├── pipeline/
│   ├── __init__.py
│   ├── orchestrator.py          # Main pipeline coordination (similar to aqumen_pipeline_v2)
│   ├── step_executor.py         # Individual step methods (step1-step7)
│   └── streaming.py             # Streaming pipeline execution
├── validators/
│   ├── __init__.py
│   ├── step_validators.py       # Validation logic for each step
│   └── assessment_validator.py  # Step 7 assessment validation (already exists in v2)
├── persistence/
│   ├── __init__.py
│   ├── logger.py                # File and database logging
│   └── repo.py                  # Database operations (already exists)
├── config/
│   ├── __init__.py
│   ├── pipeline_config.py       # Pipeline constants and configuration
│   └── prompts_loader.py        # Already exists
```

**Extraction Plan:**

1. **pipeline/orchestrator.py** (~200 lines)
   - `CorrectedSevenStepPipeline.__init__()` → `PipelineOrchestrator.__init__()`
   - `run_full_pipeline()` → `orchestrator.run_full_pipeline()`
   - `run_full_pipeline_streaming()` → Extract to `streaming.py`

2. **pipeline/step_executor.py** (~400 lines)
   - Extract all `step1_*`, `step2_*`, `step3_*`, `step4_*`, `step5_*`, `step6_*`, `step7_*` methods
   - Each step becomes a standalone function with clear inputs/outputs
   - Easier to unit test individual steps

3. **validators/step_validators.py** (~200 lines)
   - `_validate_assessment_payload()` → `validate_assessment()`
   - `_build_step7_prompt()` → Extract validation logic
   - Additional validators for steps 1-6

4. **persistence/logger.py** (~100 lines)
   - `log_step()` → `log_pipeline_step()`
   - `_log_step_reward()` → `log_step_reward()`
   - `_write_final_result()` → `write_final_result()`

5. **config/pipeline_config.py** (~50 lines)
   - Extract all constants: `allowed_difficulties`, `step7_max_attempts`, `min_code_lines`, etc.
   - Model IDs and configuration

### Priority 2: api_server.py (751 lines)

**Current Issues:**
- Single file with all endpoints, models, streaming logic, validation
- Mixes concerns: routing, business logic, validation, SSE implementation
- Difficult to unit test endpoint handlers separately

**Refactoring Strategy:**

```
minimal/backend/
├── api/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app initialization, CORS config
│   ├── endpoints.py             # Route handlers (health, models, generate, etc.)
│   ├── streaming.py             # SSE streaming implementation
│   └── models.py                # Pydantic request/response models
├── services/
│   ├── __init__.py
│   └── question_generator.py   # Business logic for question generation
```

**Extraction Plan:**

1. **api/models.py** (~100 lines)
   - `GenerateRequest`
   - `QuestionResponse`
   - `HealthResponse`
   - All Pydantic models

2. **api/endpoints.py** (~300 lines)
   - All `@app.get()` and `@app.post()` route handlers
   - Keep handlers thin - delegate to services

3. **api/streaming.py** (~150 lines)
   - `format_sse_message()`
   - `run_pipeline_streaming()`
   - SSE-specific utilities

4. **api/main.py** (~100 lines)
   - FastAPI app initialization
   - CORS middleware configuration
   - Pipeline singleton management
   - Startup events

5. **services/question_generator.py** (~100 lines)
   - `get_pipeline()` - pipeline management
   - Business logic extracted from endpoints

## Testing Strategy

### Integration Tests (Before Refactoring)
Create integration tests to capture current behavior:
- `tests/integration/test_api_endpoints.py` - Test all API endpoints
- `tests/integration/test_pipeline_flow.py` - Test full pipeline execution

### Unit Tests (After Refactoring)
Create unit tests for each module:
- `tests/unit/test_step_executor.py` - Test individual step functions
- `tests/unit/test_validators.py` - Test validation logic
- `tests/unit/test_streaming.py` - Test SSE streaming
- `tests/unit/test_endpoints.py` - Test endpoint handlers with mocks

## Implementation Order

1. ✅ **Setup**: Create venv with uv, install dependencies, configure ruff
2. **Write Integration Tests**: Capture current behavior (api_server + pipeline)
3. **Refactor api_server.py**:
   - Extract models → `api/models.py`
   - Extract streaming → `api/streaming.py`
   - Extract endpoints → `api/endpoints.py`
   - Create main app → `api/main.py`
   - Write unit tests for each module
   - Run integration tests to verify
4. **Refactor corrected_7step_pipeline.py**:
   - Extract step executors → `pipeline/step_executor.py`
   - Extract validators → `validators/step_validators.py`
   - Extract logger → `persistence/logger.py`
   - Extract config → `config/pipeline_config.py`
   - Create orchestrator → `pipeline/orchestrator.py`
   - Write unit tests for each module
   - Run integration tests to verify
5. **Linting**: Run ruff on all refactored code, fix issues
6. **Frontend Testing**: Run Playwright tests to ensure frontend still works
7. **Final Verification**: Run all integration + unit tests

## Success Criteria

- ✅ All existing integration tests pass
- ✅ All new unit tests pass
- ✅ Ruff reports 0 errors
- ✅ ESLint reports 0 errors on frontend
- ✅ Playwright tests pass
- ✅ No file exceeds 400 lines
- ✅ Each module has a single, clear responsibility
- ✅ Code coverage > 80% for new modules

## Benefits

1. **Maintainability**: Smaller, focused modules are easier to understand and modify
2. **Testability**: Unit tests can target specific functions without complex setup
3. **Reusability**: Extracted modules can be imported and used independently
4. **Following Best Practices**: Matches the pattern already established in aqumen_pipeline_v2
5. **Easier Debugging**: Clear separation of concerns makes it easier to trace issues
