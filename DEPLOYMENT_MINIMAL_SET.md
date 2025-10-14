# Minimal Working Deployment Set

## 📋 Overview

This document defines the minimal set of files needed for a working deployment with:
- ✅ React frontend (Vercel)
- ✅ FastAPI backend (Render)
- ✅ 7-step pipeline with AWS Bedrock
- ✅ Database logging
- ✅ Interactive assessment UI

---

## 🎯 Deployment Strategy

### Repository Structure

```
main/
├── frontend/                  # React app (Vercel auto-detects)
│   ├── src/
│   │   ├── App.jsx           # Main app with pipeline + assessment
│   │   ├── api.js            # Backend API client
│   │   ├── main.jsx          # React entry point
│   │   └── index.css         # Minimal styles
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── vercel.json           # Vercel config
│
├── backend/                   # FastAPI server (Render auto-detects)
│   ├── api_server.py         # FastAPI endpoints (SSE + blocking)
│   ├── corrected_7step_pipeline.py  # 7-step logic
│   ├── aqumen_pipeline/      # Shared datatypes/prompts/tools/validators
│   ├── analytics/            # Reward calculations
│   ├── clients/bedrock.py    # AWS Bedrock runtime wrapper
│   ├── config/               # Prompt/tool loaders
│   ├── persistence/repo.py   # SQLite access
│   ├── services/invoke.py    # Model invocation helpers
│   ├── prompts.json          # Prompt templates
│   ├── tools.json            # Tool schemas
│   ├── requirements.txt      # Python deps
│   ├── render.yaml           # Render config
│   └── pipeline_results.db   # SQLite (gitignored, created at runtime)
│
├── docs/                      # Documentation
│   ├── AWS_BEDROCK_SETUP.md
│   └── README.md
│
├── .gitignore
├── README.md                  # Main README
└── LICENSE
```

---

## ✅ Frontend Files (7 files)

### Core App Files

1. **`frontend/src/App.jsx`** (from `frontend-main-branch/src/App.jsx`)
   - ✅ Interactive assessment UI (click errors)
   - ✅ Dev Mode with pipeline visualization
   - ✅ Student Mode for gameplay
   - ✅ Demo mode with GRPO example
   - ✅ Live generation with SSE streaming
   - Lines: ~1,500

2. **`frontend/src/api.js`** (from `frontend-main-branch/src/api.js`)
   - ✅ SSE client for streaming
   - ✅ Backend health check
   - Lines: ~150

3. **`frontend/src/main.jsx`** (from `frontend-main-branch/src/main.jsx`)
   - React 18 entry point
   - Lines: ~10

4. **`frontend/src/index.css`** (from `frontend-main-branch/src/index.css`)
   - Minimal Tailwind setup
   - Lines: ~5

### Build Config

5. **`frontend/index.html`** (from `frontend-main-branch/index.html`)
   - HTML shell
   - Tailwind CDN link
   - Lines: ~20

6. **`frontend/package.json`** (from `frontend-main-branch/package.json`)
   ```json
   {
     "name": "aqumen-ai-assessment",
     "version": "2.0.0",
     "type": "module",
     "scripts": {
       "dev": "vite",
       "build": "vite build",
       "preview": "vite preview"
     },
     "dependencies": {
       "react": "^18.2.0",
       "react-dom": "^18.2.0"
     },
     "devDependencies": {
       "@vitejs/plugin-react": "^4.0.3",
       "vite": "^4.4.5"
     }
   }
   ```

7. **`frontend/vite.config.js`** (from `frontend-main-branch/vite.config.js`)
   ```js
   import { defineConfig } from 'vite'
   import react from '@vitejs/plugin-react'

   export default defineConfig({
     plugins: [react()],
     server: {
       port: 5173
     }
   })
   ```

### Vercel Config

8. **`frontend/vercel.json`** (NEW - create this)
   ```json
   {
     "buildCommand": "npm run build",
     "outputDirectory": "dist",
     "framework": "vite",
     "env": {
       "VITE_API_URL": "https://your-backend.onrender.com"
     }
   }
   ```

---

## ✅ Backend Files (5 files)

### Core Backend Files

1. **`backend/api_server.py`** (from `backend/api_server.py`)
   - ✅ FastAPI server with CORS
   - ✅ `/api/generate-stream` (SSE streaming)
   - ✅ `/api/generate` (blocking)
   - ✅ `/health` endpoint
   - ✅ `/api/models` endpoint
   - Lines: ~410

2. **`backend/corrected_7step_pipeline.py`** (from `backend/corrected_7step_pipeline.py`)
   - ✅ Full 7-step pipeline logic
   - ✅ Database logging to `enhanced_step_responses`
   - ✅ Streaming generator for SSE
   - ✅ Model differentiation logic
   - Lines: ~1,300

3. **Support modules**  
   Include the supporting packages under `backend/` (now surfaced via `backend/aqumen_pipeline/`):
   - `clients/bedrock.py` for AWS Bedrock runtime access
   - `services/invoke.py` for safe invocation helpers
   - `analytics/`, `persistence/`, and `config/` for rewards, SQLite logging, and prompt/tool loaders
   - `prompts.json` and `tools.json` for the canonical templates and schemas

4. **`backend/requirements.txt`** (from `backend/requirements.txt`)
   ```
   fastapi==0.109.0
   uvicorn[standard]==0.27.0
   pydantic==2.5.3
   python-multipart==0.0.6
   asyncio
   streamlit>=1.32.0
   boto3>=1.34.0
   botocore>=1.34.0
   pandas>=2.0.0
   ```

### Render Config

5. **`backend/render.yaml`** (NEW - create this)
   ```yaml
   services:
     - type: web
       name: aqumen-backend
       env: python
       region: oregon
       plan: starter
       buildCommand: pip install -r requirements.txt
       startCommand: uvicorn api_server:app --host 0.0.0.0 --port $PORT
       envVars:
         - key: AWS_ACCESS_KEY_ID
           sync: false
         - key: AWS_SECRET_ACCESS_KEY
           sync: false
         - key: AWS_DEFAULT_REGION
           value: us-west-2
         - key: PYTHON_VERSION
           value: 3.11.0
       healthCheckPath: /health
   ```

---

## ✅ Docs (2 files)

1. **`docs/AWS_BEDROCK_SETUP.md`** (already exists)
2. **`docs/README.md`** (create architecture overview)

---

## ✅ Root Files (3 files)

1. **`.gitignore`**
   ```
   # Dependencies
   node_modules/
   __pycache__/
   *.pyc
   .env
   .venv/
   venv/

   # Build outputs
   dist/
   build/
   *.egg-info/

   # Database (runtime generated)
   *.db
   *.sqlite
   *.sqlite3

   # Logs
   *.log
   *.jsonl

   # IDE
   .vscode/
   .idea/
   *.swp

   # OS
   .DS_Store
   Thumbs.db

   # Testing
   test-results/
   playwright-report/

   # Temp
   *.tmp
   *.bak
   ```

2. **`README.md`** (root level)
   ```markdown
   # Aqumen.ai - AI Code Review Mastery

   Interactive adversarial assessment for AI/ML developers.

   ## 🚀 Live Demo
   - Frontend: https://demo.aqumen.ai
   - API Docs: https://api.aqumen.ai/docs

   ## 🏗️ Architecture
   - **Frontend**: React + Vite (deployed on Vercel)
   - **Backend**: FastAPI + AWS Bedrock (deployed on Render)
   - **Pipeline**: 7-step adversarial question generation

   ## 📦 Deployment

   ### Frontend (Vercel)
   ```bash
   cd frontend
   vercel deploy --prod
   ```

   ### Backend (Render)
   - Push to GitHub
   - Render auto-deploys from `backend/render.yaml`
   - Set environment variables in Render dashboard

   ## 🛠️ Local Development

   ### Frontend
   ```bash
   cd frontend
   npm install
   npm run dev  # http://localhost:5173
   ```

   ### Backend
   ```bash
   cd backend
   pip install -r requirements.txt
   export AWS_ACCESS_KEY_ID=xxx
   export AWS_SECRET_ACCESS_KEY=xxx
   python api_server.py  # http://localhost:8000
   ```

   ## 📖 Documentation
   - [AWS Bedrock Setup](docs/AWS_BEDROCK_SETUP.md)
   - [Architecture](docs/README.md)
   ```

3. **`LICENSE`** (MIT or your choice)

---

## 🤔 Vercel Detection Strategy

### How Vercel Knows What's Frontend

**Option 1: Root-level Frontend (Recommended for simplicity)**
```
main/
├── src/              # React source (Vercel auto-detects)
├── index.html        # Vite entry
├── package.json      # Frontend deps
├── vite.config.js
├── vercel.json       # Optional config
└── backend/          # Ignored by Vercel (no package.json in root)
```

**Option 2: Subdirectory Frontend (Current structure)**
```
main/
├── frontend/         # Vercel project root = "frontend"
│   └── package.json
└── backend/          # Separate deployment
```

**Vercel Configuration**:
- Project Settings → Root Directory: `frontend`
- Build Command: `npm run build`
- Output Directory: `dist`
- Install Command: `npm install`

### How Render Knows What's Backend

**Render Configuration**:
- Detects `render.yaml` in repo root
- Uses `buildCommand` and `startCommand` from YAML
- Alternatively: Manual setup in Render dashboard
  - Build Command: `pip install -r backend/requirements.txt`
  - Start Command: `cd backend && uvicorn api_server:app --host 0.0.0.0 --port $PORT`

---

## 📁 Total File Count: 17 Files

### Frontend: 8 files
- 4 source files (.jsx, .js, .css)
- 4 config files (package.json, vite.config, index.html, vercel.json)

### Backend: 5 files
- 3 Python files (.py)
- 2 config files (requirements.txt, render.yaml)

### Docs: 2 files

### Root: 3 files
- README.md
- .gitignore
- LICENSE

---

## 🚀 Deployment Steps

### Step 1: Prepare Repository

```bash
# Current branch: demo-light
# We need to merge clean frontend into main

# Option A: Copy frontend-main-branch files to main
git checkout main
mkdir -p frontend/src
cp frontend-main-branch/src/* frontend/src/
cp frontend-main-branch/{index.html,package.json,vite.config.js} frontend/
cp backend/{api_server.py,corrected_7step_pipeline.py} backend/
cp -R backend/{analytics,clients,config,persistence,services} backend/
cp backend/{prompts.json,prompts_changes.json,tools.json,tools_changes.json} backend/

# Option B: Create fresh structure (cleaner)
# See detailed steps below
```

### Step 2: Deploy Backend (Render)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add minimal deployment set"
   git push origin main
   ```

2. **Create Render Service**:
   - Go to https://render.com
   - New → Web Service
   - Connect GitHub repo
   - Render auto-detects `render.yaml`
   - Add environment variables:
     - `AWS_ACCESS_KEY_ID`
     - `AWS_SECRET_ACCESS_KEY`

3. **Verify**:
   - Wait for deploy (~5 mins)
   - Check https://your-backend.onrender.com/health

### Step 3: Deploy Frontend (Vercel)

1. **Update API URL**:
   ```bash
   # frontend/vercel.json
   {
     "env": {
       "VITE_API_URL": "https://your-backend.onrender.com"
     }
   }
   ```

2. **Deploy**:
   ```bash
   cd frontend
   vercel --prod
   ```

3. **Or use Vercel Dashboard**:
   - Import GitHub repo
   - Root Directory: `frontend`
   - Framework Preset: Vite
   - Environment Variable: `VITE_API_URL=https://your-backend.onrender.com`

4. **Verify**:
   - Open https://your-app.vercel.app
   - Test Student Mode (should see 10 questions)
   - Test Dev Mode (should see GRPO example + pipeline)
   - Test Live Generation (should stream from backend)

---

## ⚠️ Missing/Extra Files to Ignore

### Don't Include:
- ❌ `*.jsonl` (session logs)
- ❌ `*.db` (database - regenerated)
- ❌ `test_*.py` (local testing scripts)
- ❌ `demo_light_app.py` (old Streamlit - deprecated)
- ❌ `frontend-dev/`, `frontend-main/` (duplicate directories)
- ❌ `*.md` files (except README and docs/)
- ❌ `playwright/` tests (optional, for CI later)

### Database Note:
- `pipeline_results.db` is **NOT** in Git
- Created automatically on first backend run
- Tables auto-initialize from `corrected_7step_pipeline.py`

---

## 🔧 Environment Variables

### Backend (Render)
```
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=xxx
AWS_DEFAULT_REGION=us-west-2
PYTHON_VERSION=3.11.0
```

### Frontend (Vercel)
```
VITE_API_URL=https://aqumen-backend.onrender.com
```

---

## ✅ Verification Checklist

### After Deployment:

- [ ] Backend health endpoint returns 200: `curl https://api.aqumen.ai/health`
- [ ] Backend models endpoint works: `curl https://api.aqumen.ai/api/models`
- [ ] Frontend loads at https://demo.aqumen.ai
- [ ] Student + Demo mode shows 10 hardcoded questions
- [ ] Dev + Demo mode shows GRPO example with pipeline panel
- [ ] Switching to Live Generation shows empty state
- [ ] Live Generation API health check passes (green indicator)
- [ ] Entering topic + Generate streams question via SSE
- [ ] Database logs new runs to `enhanced_step_responses`

---

## 📊 What Gets Excluded from Main Branch

### Large/Temporary Files:
- Session logs (`.jsonl`)
- Test databases
- Build artifacts (`dist/`, `node_modules/`)
- Python cache (`__pycache__/`)

### Deprecated Code:
- Old Streamlit apps
- Duplicate frontend directories
- Testing scripts not needed in production

### Local Development Only:
- `.env` files
- Local database snapshots
- Playwright test results

---

## 🎯 Final Structure Preview

```
main/ (17 files + docs)
├── frontend/
│   ├── src/
│   │   ├── App.jsx         (1,500 lines - full assessment + pipeline)
│   │   ├── api.js          (150 lines - SSE client)
│   │   ├── main.jsx        (10 lines)
│   │   └── index.css       (5 lines)
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── vercel.json
├── backend/
│   ├── api_server.py                    (410 lines)
│   ├── corrected_7step_pipeline.py      (1,300 lines)
│   ├── analytics/                       (reward telemetry)
│   ├── clients/bedrock.py               (AWS runtime wrapper)
│   ├── config/                          (prompt/tool loaders)
│   ├── persistence/repo.py              (SQLite logging)
│   ├── services/invoke.py               (invocation helpers)
│   ├── prompts.json / tools.json        (prompt + tool schemas)
│   ├── requirements.txt
│   └── render.yaml
├── docs/
│   ├── AWS_BEDROCK_SETUP.md
│   └── README.md
├── .gitignore
├── README.md
└── LICENSE
```

**Total: ~3,600 lines of code, 17 config/source files**

---

Ready to create this structure and push to main?
