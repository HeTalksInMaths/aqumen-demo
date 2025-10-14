# Frontend Cleanup & Integration Plan

## Current Situation Analysis

### Port 3000 Frontend (`frontend/`)
**Purpose**: Testing if standalone file works same as modularized version
**Status**: ❌ **Can be removed** - served its purpose for comparison testing
**Files**:
- `original_demo.jsx` (675 lines) - Original standalone version
- `demo-modular.jsx` (124 lines) - Modularized version
- `src/demo.jsx` - Same as original_demo.jsx (identical code)
- `interactive-demo.html` - Toggle between two versions
- **All use fake API calls** - just `setTimeout()` simulations

**Timeline**:
- Sept 12: Created original standalone demo
- Sept 13: Created modular version to compare
- Port 3000 was for side-by-side toggle testing
- **No longer needed** ✅

---

## Target Architecture (What You Want)

```
┌─────────────────────────────────────────────────────┐
│  STREAMLIT DEV UI (port 8501)                        │
│  Purpose: Developer debugging & inspection           │
│  • Shows real-time SSE streaming of 7 steps          │
│  • Full prompts, responses, model logs               │
│  • Demo mode with hardcoded example                  │
│  Status: ✅ WORKING - Connected to pipeline         │
└─────────────────────────────────────────────────────┘
                      ↓ calls
┌─────────────────────────────────────────────────────┐
│  FASTAPI BACKEND (port 8000)                         │
│  Purpose: Runs actual 7-step adversarial pipeline   │
│  • /api/generate (blocking POST)                     │
│  • /api/generate-stream (SSE streaming GET)          │
│  • AWS Bedrock integration (Sonnet 4.5/4, Haiku 3)  │
│  Status: ✅ TESTED - 6 bugs fixed, working          │
└─────────────────────────────────────────────────────┘
                      ↓ returns Step 7 assessment
┌─────────────────────────────────────────────────────┐
│  REACT PRODUCTION UI (port 5173)                     │
│  Purpose: Student-facing assessment game            │
│  • Beautiful, polished UI (main branch version)      │
│  • Click-based error detection                       │
│  • Currently: hardcoded 10 questions                 │
│  • TODO: Fetch from FastAPI /api/generate           │
│  Status: ⏳ NEEDS INTEGRATION                        │
└─────────────────────────────────────────────────────┘
```

---

## Step 1: Finish Debugging (Your Current Questions)

Before cleaning up, you wanted to test:

### A. Math Topic Prompts
**Question**: "Can I pick simplifying exponents and get math problems, not code?"

**Answer**: Need to check prompts in `corrected_7step_pipeline.py` - they currently assume code generation.

**Action Items**:
1. Check Step 3 prompt (question generation)
2. Check Step 7 prompt (assessment creation)
3. Test with "Simplifying Exponents" topic
4. See if it generates math expressions or forces code

### B. Step 7 Retry Analysis
**Question**: "Why did Step 7 fail on attempt 1 and succeed on attempt 2?"

**Answer**: Step 7 has hard-coded validation checks (lines 649-743 in pipeline):
- Delimiter balance (must have matching `<<` and `>>`)
- Error ID uniqueness
- Code line count (24-60 lines)
- Error count (3-5 errors)
- Error span distance (20-120 characters)

**What happened**: Attempt 1 failed validation → Opus got feedback → Attempt 2 passed

### C. Streamlit Step-by-Step Tabs
**Question**: "Can we show all 7 steps in tabs, not just final result?"

**Current State**:
- Demo mode: Only shows final assessment
- Live mode: Shows step-by-step SSE stream in log format

**Desired State**:
- Tabs for each step (Step 1, Step 2, ..., Step 7, Final)
- Each tab shows that step's full output
- Works in both demo mode and live mode

---

## Step 2: Clean Up Port 3000 Frontend

**Files to Archive/Remove**:
```bash
frontend/
├── original_demo.jsx          ❌ Remove (test artifact)
├── demo-modular.jsx           ❌ Remove (test artifact)
├── src/demo.jsx               ❌ Remove (same as original_demo.jsx)
├── interactive-demo.html      ❌ Remove (toggle testing)
├── test.html                  ❌ Remove (old test file)
└── hardcoded_questions_example.jsx  ⚠️ Keep as reference?
```

**What to Keep**:
- `package.json`, `vite.config.js` - If you want to keep Vite setup
- `components/` - Only if they're useful for future React work
- Or just delete the entire `frontend/` directory!

---

## Step 3: Integrate Port 5173 with Real Pipeline

**Goal**: Replace hardcoded questions in main branch with FastAPI calls

### Current Main Branch (Port 5173)
- Location: `frontend-main-branch/src/App.jsx`
- Lines 15-229: Hardcoded `rawQuestions` array
- Clean, production-ready UI
- No API integration

### Integration Steps

1. **Add API Fetch Function**
```javascript
const fetchQuestionFromPipeline = async (topic) => {
  const response = await fetch('http://localhost:8000/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, max_retries: 3 })
  });

  const data = await response.json();
  return transformPipelineToQuestion(data.assessment);
};
```

2. **Transform Step 7 Output to React Format**
```javascript
const transformPipelineToQuestion = (assessment) => {
  // Convert Step 7 JSON to rawQuestions format
  return {
    title: assessment.title,
    difficulty: assessment.difficulty,
    code: assessment.code,  // Array of lines
    errors: assessment.errors.map(e => ({
      id: e.id,
      description: e.description
    }))
  };
};
```

3. **Add Generation UI**
- Button: "Generate New Question"
- Input: Topic selector
- Loading state during 60s+ pipeline execution
- Or use SSE streaming for progress updates!

4. **Optional: SSE Streaming**
Instead of POST (blocking), use GET streaming:
```javascript
const eventSource = new EventSource(`http://localhost:8000/api/generate-stream?topic=${topic}&max_retries=3`);

eventSource.addEventListener('step', (event) => {
  const data = JSON.parse(event.data);
  console.log(`Step ${data.step_number}: ${data.description}`);
  // Show progress bar
});

eventSource.addEventListener('complete', (event) => {
  const data = JSON.parse(event.data);
  // Display final assessment
});
```

---

## Step 4: Final Architecture

After cleanup and integration:

```
PROJECT ROOT
├── backend/
│   ├── corrected_7step_pipeline.py   (7-step pipeline)
│   ├── api_server.py                 (FastAPI with SSE)
│   ├── requirements.txt
│   └── pipeline_results.db           (logs database)
│
├── frontend-dev/                      (Streamlit - Developer UI)
│   ├── streamlit_app.py
│   ├── demo_assessment.json
│   └── requirements.txt
│
├── frontend-main-branch/              (React - Production UI)
│   ├── src/App.jsx                    (integrated with FastAPI)
│   ├── package.json
│   └── vite.config.js
│
└── docs/                              (Documentation)
    ├── AWS_BEDROCK_SETUP.md
    ├── FRONTEND_COMPARISON.md
    ├── DEBUGGING_RESULTS.md
    └── DEPLOYMENT_GUIDE.md
```

**Removed**:
- ❌ `frontend/` directory entirely
- ❌ Port 3000 testing artifacts

---

## Summary: Your Questions & Next Steps

### Immediate Tasks (Before Cleanup)

1. ✅ **Check prompts for math support** - Test "Simplifying Exponents"
2. ✅ **Analyze Step 7 retry** - Read validation logs
3. ✅ **Add tabs to Streamlit** - Show all steps separately

### After Debugging

4. **Remove port 3000 frontend** - No longer needed
5. **Integrate port 5173 with FastAPI** - Real pipeline questions
6. **Deploy full stack** - Render (backend) + Vercel (frontend) + Streamlit Cloud (dev)

---

## Want Me To...

A. **Check prompts now** - See if math topics work or need modification?
B. **Add tabs to Streamlit** - Show all 7 steps in separate tabs?
C. **Analyze Step 7 retry** - Show you the validation logs from the database?
D. **All of the above** - Full debugging session?

Let me know which debugging task to tackle first!
