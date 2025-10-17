# Quick Reference Card

## 🚀 Essential Commands

### Environment
```bash
# Activate venv
cd minimal/backend
source .venv/bin/activate

# Check Python version
python --version  # Should show 3.11.13
```

### Run API Server
```bash
# Mock mode (no AWS credentials needed)
AQU_MOCK_PIPELINE=1 python api_server.py

# With uvicorn (recommended)
AQU_MOCK_PIPELINE=1 uvicorn api_server:app --reload --port 8000

# Production mode (requires AWS)
python api_server.py
```

### Run Tests
```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/ -m "unit" -v

# Integration tests only
pytest tests/ -m "integration" -v

# Specific file
pytest tests/unit/test_step7_direct.py -v

# With coverage
pytest tests/ --cov=api --cov-report=html
```

### Linting & Formatting
```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check . --fix

# Format code
ruff format .

# Both
ruff check . --fix && ruff format .
```

### Frontend
```bash
cd minimal/frontend

# Install dependencies
npm install

# Run linter
npm run lint

# Run dev server
npm run dev

# Run Playwright tests
npm run test:e2e
```

## 📊 Project Stats

- **Python Version**: 3.11+
- **Total Tests**: 45 (10 unit + 33 integration + 2 integration subtest)
- **Test Pass Rate**: 83% (43/45)
- **Code Reduced**: api_server.py 752 → 33 lines (95.6%)
- **Ruff Issues Fixed**: 356
- **Test Framework**: pytest
- **Linter**: ruff (Python) + ESLint (JavaScript)

## 📁 Key Files

| File | Lines | Purpose |
|------|-------|---------|
| `api/models.py` | 48 | Pydantic request/response models |
| `api/streaming.py` | 122 | SSE streaming logic |
| `api/main.py` | 111 | FastAPI app initialization |
| `api/endpoints.py` | 560 | All route handlers |
| `api_server.py` | 33 | Entry point (imports from api/) |

## 🧪 Test Files

| File | Tests | Type |
|------|-------|------|
| `test_api_endpoints.py` | 20 | Integration |
| `test_pipeline_flow.py` | 10 | Integration |
| `test_content_marketing_pipeline.py` | 3 | Integration |
| `test_step7_direct.py` | 12 | Unit |

## ⚡ Quick Checks

```bash
# Verify API server imports work
python -c "from api_server import app; print('✅ API server OK')"

# Verify test discovery
pytest tests/ --co -q

# Run fast unit tests only
pytest tests/ -m "unit" -v --tb=short

# Check code quality
ruff check api/ api_server.py
```

## 🔗 API Endpoints

- Health: `http://localhost:8000/health`
- Docs: `http://localhost:8000/docs`
- Models: `http://localhost:8000/api/models`
- Prompts: `http://localhost:8000/api/get-prompts`

## 📝 Test Markers

```python
@pytest.mark.unit          # Unit tests
@pytest.mark.integration   # Integration tests
@pytest.mark.slow          # Slow tests
@pytest.mark.skip          # Skip tests
```

## 🎯 Next Steps

1. Fix 2 failing unit tests
2. Refactor `corrected_7step_pipeline.py` (1,378 lines)
3. Add unit tests for API modules
4. Run Playwright tests
5. Fix remaining 14 ruff warnings

## 📚 Documentation

- `REFACTORING_PLAN.md` - Strategy
- `TEST_SUMMARY.md` - All tests
- `QUICKSTART_REFACTORED.md` - Getting started
- `COMPLETE_REFACTORING_SUMMARY.md` - Full summary
- `QUICK_REFERENCE.md` - This file
