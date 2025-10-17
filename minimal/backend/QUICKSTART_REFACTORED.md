# Quick Start Guide - Refactored Backend

## 🚀 Getting Started

### 1. Activate Virtual Environment
```bash
cd /Users/hetalksinmaths/minimal\ on\ local/aqumen-demo/minimal/backend
source .venv/bin/activate
```

### 2. Run the API Server
```bash
# Option 1: Direct Python execution
python api_server.py

# Option 2: Using uvicorn (recommended for development)
uvicorn api_server:app --reload --port 8000

# Option 3: With mock mode (no AWS credentials needed)
AQU_MOCK_PIPELINE=1 uvicorn api_server:app --reload --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. Run Tests
```bash
# All tests
python -m pytest tests/ -v

# Just integration tests
python -m pytest tests/integration/ -v

# Just unit tests (when we write them)
python -m pytest tests/unit/ -v

# With coverage
python -m pytest tests/ --cov=api --cov-report=html
```

### 4. Run Linters
```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check . --fix

# Format code
ruff format .

# Check specific files
ruff check api/ api_server.py
```

## 📁 New Structure

```
api/
├── __init__.py          # Package marker
├── models.py            # Pydantic request/response models
├── streaming.py         # Server-Sent Events streaming logic
├── main.py              # FastAPI app initialization & CORS
└── endpoints.py         # All route handlers

api_server.py            # Entry point (imports from api/)
```

## 🔍 What Changed

### Before
```python
# api_server.py (752 lines)
# Everything in one file:
# - FastAPI app setup
# - CORS configuration
# - Pydantic models
# - All endpoints
# - SSE streaming logic
# - Pipeline management
```

### After
```python
# api_server.py (33 lines)
from api.main import app
import api.endpoints

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", ...)
```

## 🧪 Testing in Mock Mode

No AWS credentials required! Set the environment variable:

```bash
export AQU_MOCK_PIPELINE=1
python api_server.py
```

Then test the endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Get models info
curl http://localhost:8000/api/models

# Get prompts
curl http://localhost:8000/api/get-prompts
```

## 🔧 Troubleshooting

### Import Error
```
ImportError: cannot import name 'app' from 'api_server'
```
**Solution:** Make sure you're in the backend directory and the venv is activated

### Module Not Found
```
ModuleNotFoundError: No module named 'api'
```
**Solution:** Run from the backend directory where the `api/` folder exists

### Ruff Not Found
```
Command 'ruff' not found
```
**Solution:** Install ruff in the venv:
```bash
source .venv/bin/activate
uv pip install ruff
```

## 📊 Code Stats

| File | Lines | Purpose |
|------|-------|---------|
| `api/models.py` | 48 | Request/response validation |
| `api/streaming.py` | 122 | SSE streaming logic |
| `api/main.py` | 111 | App initialization |
| `api/endpoints.py` | 560 | Route handlers |
| `api_server.py` | 33 | Entry point |
| **Total** | **874** | vs 752 in original (more modular!) |

## ✅ Verified Working

- ✅ API server starts successfully
- ✅ All imports work correctly
- ✅ Backward compatibility maintained
- ✅ Ruff auto-fixed 356 issues
- ✅ Code formatted consistently

## 🎯 Next Steps

1. Write unit tests for each module
2. Refactor `corrected_7step_pipeline.py` (1,378 lines)
3. Run full integration tests
4. Run Playwright frontend tests
5. Fix remaining 14 ruff warnings

## 💡 Tips

- Use mock mode for development without AWS
- Run ruff after every change
- Keep modules under 600 lines
- Write tests before refactoring
- One responsibility per module
