# Aqumen.ai - Minimal Deployment Package

**Interactive adversarial assessment for AI/ML developers**

This is the minimal deployment package containing only the essential files for production deployment.

---

## 🎯 What's Included

### Frontend (React + Vite)
- **Full interactive assessment UI** - Click-to-find-errors gameplay
- **Dev Mode** - Real-time 7-step pipeline visualization with SSE streaming
- **Student Mode** - Clean gameplay experience
- **Demo Mode** - GRPO gold-standard example with full pipeline trace
- **Live Generation** - Generate custom questions from any AI/ML topic

### Backend (FastAPI + AWS Bedrock)
- **7-step adversarial pipeline** - Generates expert-level assessment questions
- **SSE streaming** - Real-time step-by-step updates
- **Database logging** - SQLite with `enhanced_step_responses` table
- **Model differentiation** - Tests Sonnet 4, Opus 4.1, and Haiku 3

---

## 📁 Structure (17 files)

```
minimal/
├── frontend/               # React app (8 files)
│   ├── src/
│   │   ├── App.jsx        # Main UI (~1,500 lines)
│   │   ├── api.js         # Backend client with SSE
│   │   ├── main.jsx       # React entry
│   │   └── index.css      # Minimal styles
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── vercel.json        # Vercel deployment config
│
├── backend/               # FastAPI server (5 files)
│   ├── api_server.py      # FastAPI endpoints (~410 lines)
│   ├── corrected_7step_pipeline.py  # Pipeline logic (~1,300 lines)
│   ├── bedrock_utils.py   # AWS Bedrock wrapper (~200 lines)
│   ├── requirements.txt   # Python dependencies
│   └── render.yaml        # Render deployment config
│
├── .gitignore
└── README.md (this file)
```

**Total: ~3,600 lines of code**

---

## 🚀 Quick Start

### Local Development

#### 1. Start Backend (Terminal 1)
```bash
cd backend
pip install -r requirements.txt

# Set AWS credentials
export AWS_ACCESS_KEY_ID=your_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_here
export AWS_DEFAULT_REGION=us-west-2

# Start server
python api_server.py
# Server running at http://localhost:8000
```

#### 2. Start Frontend (Terminal 2)
```bash
cd frontend
npm install
npm run dev
# Frontend running at http://localhost:5173
```

#### 3. Test
- Open http://localhost:5173
- **Student + Demo**: Should show 10 hardcoded questions
- **Dev + Demo**: Should show GRPO example with pipeline panel
- **Dev + Live**: Click "Generate New Question" → Enter topic → See real-time streaming

---

## 🌐 Production Deployment

### Backend → Render

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add minimal deployment package"
   git push origin minimal
   ```

2. **Create Render Service**:
   - Go to https://render.com
   - New → Web Service
   - Connect GitHub repo
   - Render auto-detects `backend/render.yaml`
   - Add environment variables in dashboard:
     - `AWS_ACCESS_KEY_ID`
     - `AWS_SECRET_ACCESS_KEY`

3. **Verify**: https://your-backend.onrender.com/health

### Frontend → Vercel

1. **Update API URL**:
   ```bash
   # Edit frontend/vercel.json
   {
     "env": {
       "VITE_API_URL": "https://your-backend.onrender.com"
     }
   }
   ```

2. **Deploy via CLI**:
   ```bash
   cd frontend
   npx vercel --prod
   ```

   **OR** Deploy via Dashboard:
   - Import GitHub repo
   - Root Directory: `frontend`
   - Framework: Vite
   - Env Variable: `VITE_API_URL=https://your-backend.onrender.com`

3. **Verify**: https://your-app.vercel.app

---

## 🧪 Testing Checklist

After deployment:

- [ ] Backend health check: `curl https://api.aqumen.ai/health`
- [ ] Backend models endpoint: `curl https://api.aqumen.ai/api/models`
- [ ] Frontend loads: https://demo.aqumen.ai
- [ ] **Student + Demo**: Shows 10 questions
- [ ] **Dev + Demo**: Shows GRPO with pipeline
- [ ] **Switch to Live**: Shows empty state
- [ ] **Live Generation**: Enter "Transformer Attention" → Streams question
- [ ] Database logs to `pipeline_results.db` (check backend logs)

---

## 📊 Database

### Location
- **Backend**: `backend/pipeline_results.db` (auto-created)
- **Git**: Excluded (.gitignore)

### Schema
```sql
-- Main logging table
CREATE TABLE enhanced_step_responses (
    id INTEGER PRIMARY KEY,
    run_timestamp TEXT,
    topic TEXT,
    step_number INTEGER,
    step_name TEXT,
    model_used TEXT,
    success BOOLEAN,
    response_length INTEGER,
    full_response TEXT,
    timestamp TEXT
);
```

### Query Recent Runs
```bash
cd backend
sqlite3 pipeline_results.db "
  SELECT DISTINCT topic, run_timestamp, COUNT(*) as steps
  FROM enhanced_step_responses
  GROUP BY topic, run_timestamp
  ORDER BY run_timestamp DESC
  LIMIT 10;
"
```

---

## 🔧 Environment Variables

### Backend (Required)
```
AWS_ACCESS_KEY_ID=AKIA...           # AWS access key
AWS_SECRET_ACCESS_KEY=xxx           # AWS secret
AWS_DEFAULT_REGION=us-west-2        # Bedrock region
```

### Frontend (Required)
```
VITE_API_URL=http://localhost:8000  # Local: localhost
VITE_API_URL=https://api.aqumen.ai  # Prod: your backend URL
```

---

## 📖 Architecture

### Pipeline Flow (7 Steps)

1. **Generate Difficulty Categories** (Sonnet 4.5)
   - Creates Beginner/Intermediate/Advanced/Expert subtopics

2. **Generate Error Catalog** (Sonnet 4.5)
   - Identifies 5-7 domain-specific error patterns

3. **Generate Strategic Question** (Sonnet 4.5)
   - Creates implementation challenge

4. **Test Sonnet Implementation** (Sonnet 4)
   - Strong model attempts question

5. **Test Haiku Implementation** (Haiku 3)
   - Weak model attempts question (should fail)

6. **Judge Differentiation** (Sonnet 4.5)
   - Compares implementations, checks if weak model failed

7. **Create Student Assessment** (Sonnet 4.5)
   - Generates final question with embedded errors
   - **Retries** if validation fails

### Frontend Modes

| Mode | Questions | Pipeline Panel | Use Case |
|------|-----------|----------------|----------|
| **Student + Demo** | 10 hardcoded | Hidden | Quick gameplay |
| **Student + Live** | Empty → Generated | Hidden | Generate without inspection |
| **Dev + Demo** | GRPO example | **Visible** | Inspect gold-standard example |
| **Dev + Live** | Empty → Generated | **Visible** | Generate + inspect pipeline |

---

## 🛠️ Tech Stack

- **Frontend**: React 18 + Vite + Tailwind CSS (CDN)
- **Backend**: FastAPI + Uvicorn
- **AI**: AWS Bedrock (Claude Sonnet 4.5, Sonnet 4, Haiku 3)
- **Database**: SQLite
- **Deployment**: Vercel (frontend) + Render (backend)

---

## 📚 Documentation

For setup details:
- See `backend/render.yaml` for backend config
- See `frontend/vercel.json` for frontend config
- AWS Bedrock setup: Contact maintainer for full guide

---

## ✅ What's Working

**October 2025 Pipeline Runs**:
- ✅ Regime Change Time Series Forecasting
- ✅ GRPO (Group Relative Policy Optimization)
- ✅ Agentic Evals for Multi-Agent Systems
- ✅ All logged to `enhanced_step_responses` table

**Frontend Integration**:
- ✅ SSE streaming from FastAPI
- ✅ Pipeline visualization in Dev Mode
- ✅ Interactive assessment gameplay
- ✅ Mock pipeline data for Demo mode

---

## 🎯 Pull & Test Instructions

```bash
# Clone repo
git clone https://github.com/your-username/adversarial-demo.git
cd adversarial-demo
git checkout minimal

# Navigate to minimal package
cd minimal

# Terminal 1: Start backend
cd backend
pip install -r requirements.txt
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx
python api_server.py

# Terminal 2: Start frontend
cd frontend
npm install
npm run dev

# Browser: http://localhost:5173
```

---

## 📞 Support

- **Issues**: GitHub Issues
- **Docs**: See inline code comments
- **Architecture**: 7-step pipeline in `corrected_7step_pipeline.py`

---

**Status**: ✅ Ready for deployment
**Last Updated**: October 2025
**Maintainer**: Aqumen.ai Team
