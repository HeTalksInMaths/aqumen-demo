# React Frontend Integration Guide
## Connecting Step 7 Pipeline Output to Port 5173 Interactive Demo

---

## 🎯 Goal

Replace the hardcoded `rawQuestions` array in `frontend-main-branch/src/App.jsx` with dynamically generated questions from the 7-step adversarial pipeline (Step 7 output).

---

## 📊 Current State

### Port 5173 React Frontend (`frontend-main-branch/`)
- **Status:** ✅ Running with 10 hardcoded questions
- **File:** `src/App.jsx` (lines 15-229)
- **Data Format:**
```javascript
const rawQuestions = [
  {
    title: "Transformer Attention Implementation",
    difficulty: "Intermediate",
    code: [
      "def attention(query, key, value, mask=None):",
      "    scores = torch.matmul(query, key.transpose(-2, -1)) / <<math.sqrt(d_k)>>",
      // ... more lines
    ],
    errors: [
      {
        id: "math.sqrt(d_k)",
        description: "Should check if d_k > 0 before taking sqrt..."
      },
      // ... more errors
    ]
  }
];
```

### Step 7 Pipeline Output Format
**Source:** `backend/corrected_7step_pipeline.py` Step 7 validation (lines 649-743)

**Example from database:**
```json
{
  "title": "Evaluation Framework for Distributed Warehouse Robot Coordination",
  "difficulty": "Advanced",
  "topic": "Agentic Evals for Multi-Agent Systems",
  "code": [
    "import time",
    "import random",
    "from typing import Dict, List",
    // ... 58 lines total
  ],
  "errors": [
    {
      "id": "Log message content, timestamps, and delivery status",
      "description": "Missing critical coordination metrics in message tracking...",
      "line_number": 19
    }
  ],
  "metadata": {
    "generated_at": "2025-10-09T11:34:29",
    "quality_score": "9/10",
    "weak_model_response": "I will not provide code implementation..."
  }
}
```

**Key Difference:** Step 7 includes `line_number` field, React parses errors from `<<delimiters>>`

---

## 🔄 Data Transformation Required

### Step 7 → React Format

The React frontend expects errors **embedded in code with `<<>>`** delimiters, but Step 7 outputs **structured errors separately**.

**Two Integration Approaches:**

### Option 1: Transform Step 7 JSON to React Format (Client-Side)
**Pros:** Backend stays unchanged
**Cons:** Requires delimiter insertion logic in React

```javascript
// Transform function to add delimiters to code
const transformStep7ToReact = (step7Output) => {
  // Step 7 provides:
  // - code: Array of clean code lines
  // - errors: Array with {id, description, line_number}

  // React needs:
  // - code: Array with <<error_text>> delimiters inline
  // - errors: Array with {id, description} (no line_number)

  const codeWithDelimiters = step7Output.code.map((line, idx) => {
    // Find errors on this line
    const lineErrors = step7Output.errors.filter(err => err.line_number === idx);

    if (lineErrors.length === 0) return line;

    // Insert delimiters around error IDs
    let modifiedLine = line;
    lineErrors.forEach(error => {
      // Need to find WHERE in the line the error is
      // Step 7 doesn't provide character position, only line number
      // This is a PROBLEM - see Option 2
    });

    return modifiedLine;
  });

  return {
    title: step7Output.title,
    difficulty: step7Output.difficulty,
    code: codeWithDelimiters,
    errors: step7Output.errors.map(({ id, description }) => ({ id, description }))
  };
};
```

**PROBLEM:** Step 7 only provides `line_number`, not character positions within the line. The React parser needs exact positions to create clickable spans.

---

### Option 2: Modify Step 7 to Output React-Compatible Format ✅ **RECOMMENDED**

Update Step 7 validation to ensure errors are **already embedded** in code with delimiters.

**Current Step 7 Behavior:**
- Opus generates code with `<<error>>` delimiters
- Validation extracts errors and checks format
- Final output has delimiters in code

**What's Needed:**
- Step 7 already outputs code with delimiters! ✅
- Just need to parse them correctly in React

**Example Step 7 Output (from database):**
```json
{
  "code": [
    "def message_log(self) -> Dict[str, List[str]]:",
    "    return {<<'messages': [str(m) for m in self.message_queue]>>}"
  ],
  "errors": [
    {
      "id": "'messages': [str(m) for m in self.message_queue]",
      "description": "Missing critical coordination metrics..."
    }
  ]
}
```

**React Compatible!** The code already has delimiters, and `error.id` matches the delimited text.

---

## ✅ Integration Steps

### Step 1: Add API Fetch Function to React

Create a new file: `frontend-main-branch/src/api.js`

```javascript
const API_BASE_URL = 'http://localhost:8000';

// Fetch a single question from the pipeline (blocking)
export const fetchQuestionBlocking = async (topic, maxRetries = 3) => {
  const response = await fetch(`${API_BASE_URL}/api/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, max_retries: maxRetries })
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  const data = await response.json();
  return transformStep7ToReact(data.assessment);
};

// Fetch question using SSE streaming (real-time updates)
export const fetchQuestionStreaming = async (topic, maxRetries, onStepUpdate, onComplete) => {
  const url = `${API_BASE_URL}/api/generate-stream?topic=${encodeURIComponent(topic)}&max_retries=${maxRetries}`;

  const eventSource = new EventSource(url);

  eventSource.addEventListener('step', (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'step') {
      onStepUpdate(data); // Update UI with current step
    }
  });

  eventSource.addEventListener('complete', (event) => {
    const data = JSON.parse(event.data);
    eventSource.close();
    onComplete(transformStep7ToReact(data.assessment));
  });

  eventSource.addEventListener('error', (event) => {
    eventSource.close();
    throw new Error('SSE connection failed');
  });
};

// Transform Step 7 output to React format
const transformStep7ToReact = (step7Data) => {
  // Step 7 already has delimiters in code! No transformation needed
  return {
    title: step7Data.title,
    difficulty: step7Data.difficulty,
    code: step7Data.code, // Already has <<delimiters>>
    errors: step7Data.errors.map(err => ({
      id: err.id,
      description: err.description
      // Note: line_number not needed - React parseQuestion() finds it from delimiters
    }))
  };
};
```

---

### Step 2: Update App.jsx to Use API

**Modify `frontend-main-branch/src/App.jsx`:**

```javascript
import React, { useState, useRef, useEffect } from 'react';
import { CheckCircle, XCircle, RotateCcw, Trophy, Eye, EyeOff, Target, Award, Loader } from 'lucide-react';
import { fetchQuestionBlocking, fetchQuestionStreaming } from './api';

const App = () => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [clicks, setClicks] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const [gameComplete, setGameComplete] = useState(false);
  const [totalScore, setTotalScore] = useState(0);
  const [showSolution, setShowSolution] = useState(false);
  const [currentResult, setCurrentResult] = useState(null);
  const [parsedQuestions, setParsedQuestions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [generationMode, setGenerationMode] = useState('demo'); // 'demo' or 'live'
  const [currentStepInfo, setCurrentStepInfo] = useState(null);
  const codeRef = useRef(null);

  // Hardcoded demo questions (keep for demo mode)
  const demoQuestions = [
    // ... keep existing rawQuestions array
  ];

  // Load initial questions based on mode
  useEffect(() => {
    if (generationMode === 'demo') {
      const parsed = demoQuestions.map(question => parseQuestion(question));
      setParsedQuestions(parsed);
    }
  }, [generationMode]);

  // Generate new question from pipeline
  const generateNewQuestion = async () => {
    const topic = prompt("Enter AI/ML topic (e.g., 'RLHF with Bradley-Terry Loss'):");
    if (!topic) return;

    setIsLoading(true);
    setCurrentStepInfo('Generating question...');

    try {
      // Option 1: Blocking (wait for full result)
      const newQuestion = await fetchQuestionBlocking(topic);

      // Option 2: Streaming (real-time updates)
      // await fetchQuestionStreaming(
      //   topic,
      //   3,
      //   (stepData) => {
      //     setCurrentStepInfo(`Step ${stepData.step_number}/7: ${stepData.description}`);
      //   },
      //   (finalQuestion) => {
      //     const parsed = parseQuestion(finalQuestion);
      //     setParsedQuestions([...parsedQuestions, parsed]);
      //     setIsLoading(false);
      //     setCurrentStepInfo(null);
      //   }
      // );

      const parsed = parseQuestion(newQuestion);
      setParsedQuestions([...parsedQuestions, parsed]);
    } catch (error) {
      alert(`Failed to generate question: ${error.message}`);
    } finally {
      setIsLoading(false);
      setCurrentStepInfo(null);
    }
  };

  // Rest of the component stays the same...
  const parseQuestion = (question) => {
    // ... existing parseQuestion logic
  };

  // ... rest of component code
};
```

---

### Step 3: Add UI Controls for Generation

Add buttons to switch modes and generate questions:

```javascript
// Add to header section in App.jsx
<div className="flex gap-3 mb-4">
  <button
    onClick={() => setGenerationMode('demo')}
    className={`px-4 py-2 rounded ${generationMode === 'demo' ? 'bg-indigo-600 text-white' : 'bg-gray-200'}`}
  >
    Demo Mode (Hardcoded)
  </button>
  <button
    onClick={() => setGenerationMode('live')}
    className={`px-4 py-2 rounded ${generationMode === 'live' ? 'bg-indigo-600 text-white' : 'bg-gray-200'}`}
  >
    Live Generation
  </button>
  {generationMode === 'live' && (
    <button
      onClick={generateNewQuestion}
      disabled={isLoading}
      className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400"
    >
      {isLoading ? '⏳ Generating...' : '➕ Generate New Question'}
    </button>
  )}
</div>

{/* Loading indicator */}
{isLoading && currentStepInfo && (
  <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg mb-4">
    <div className="flex items-center gap-3">
      <Loader className="w-5 h-5 animate-spin text-blue-600" />
      <span className="text-blue-800">{currentStepInfo}</span>
    </div>
  </div>
)}
```

---

## 🔧 Backend CORS Setup (Required!)

The FastAPI backend needs CORS enabled for localhost:5173 to make requests.

**File:** `backend/api_server.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # React dev server
        "http://localhost:3000",  # Alternative port
        "https://yourdomain.vercel.app"  # Production (when deployed)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... rest of your FastAPI routes
```

---

## 📝 Step 7 Output Validation Checklist

Ensure Step 7 outputs are compatible with React:

- [ ] **Code has delimiters:** `<<error_text>>` embedded in code lines
- [ ] **Error IDs match:** `error.id` exactly matches text inside `<<>>`
- [ ] **Array format:** `code` is array of strings, `errors` is array of objects
- [ ] **Required fields:**
  - `title` (string)
  - `difficulty` (string: "Beginner" | "Intermediate" | "Advanced" | "Expert")
  - `code` (string[])
  - `errors` ({ id: string, description: string }[])

---

## 🧪 Testing the Integration

### Test 1: Hardcoded Demo Mode
1. Start React frontend: `cd frontend-main-branch && npm run dev`
2. Open http://localhost:5173
3. Verify 10 hardcoded questions load correctly
4. Click through and play the game

### Test 2: Live Generation Mode (Blocking)
1. Start FastAPI backend: `cd backend && uvicorn api_server:app --reload`
2. Switch to "Live Generation" mode in React
3. Click "Generate New Question"
4. Enter topic: "RLHF with Bradley-Terry Loss"
5. Wait ~60 seconds for pipeline to complete
6. Verify new question appears and is playable

### Test 3: Live Generation Mode (Streaming with Progress)
1. Same as Test 2, but uncomment streaming code in `generateNewQuestion`
2. Verify step-by-step progress shows in UI
3. Verify final question loads after all 7 steps

---

## 🚀 Production Deployment Strategy

### Option A: Separate Deployments
- **Frontend:** Deploy React to Vercel (static hosting)
- **Backend:** Deploy FastAPI to Render/Railway (Python hosting)
- **Env Variables:** Set `REACT_APP_API_URL=https://your-backend.render.com`

### Option B: Monolithic Deployment
- **Backend:** Serve React build as static files from FastAPI
- **File:** `backend/api_server.py`
```python
from fastapi.staticfiles import StaticFiles

# After all API routes:
app.mount("/", StaticFiles(directory="../frontend-main-branch/dist", html=True), name="static")
```
- **Build:** `cd frontend-main-branch && npm run build`
- **Deploy:** Single Render deployment with FastAPI serving everything

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────┐
│  REACT FRONTEND (Port 5173)                          │
│  ┌─────────────────────────────────────────────┐   │
│  │ App.jsx                                      │   │
│  │ - Demo Mode: uses hardcoded rawQuestions    │   │
│  │ - Live Mode: calls API                      │   │
│  └────────────┬────────────────────────────────┘   │
│               │ fetch/EventSource                   │
└───────────────┼─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  FASTAPI BACKEND (Port 8000)                         │
│  ┌─────────────────────────────────────────────┐   │
│  │ /api/generate (POST) - Blocking             │   │
│  │ /api/generate-stream (GET) - SSE Streaming  │   │
│  └────────────┬────────────────────────────────┘   │
│               │ calls                               │
└───────────────┼─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  7-STEP PIPELINE                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ Step 1: Generate difficulty categories      │   │
│  │ Step 2: Generate error catalog              │   │
│  │ Step 3: Generate strategic question         │   │
│  │ Step 4: Test Sonnet (mid-tier)              │   │
│  │ Step 5: Test Haiku (weak-tier)              │   │
│  │ Step 6: Judge differentiation               │   │
│  │ Step 7: Create assessment ← OUTPUT          │   │
│  └────────────┬────────────────────────────────┘   │
│               │ returns JSON                        │
└───────────────┼─────────────────────────────────────┘
                │
                ▼
        ┌───────────────┐
        │ Step 7 JSON   │
        │ {             │
        │   code: [...],│  ← Has <<delimiters>>
        │   errors: [...│  ← {id, description}
        │ }             │
        └───────────────┘
                │
                │ transformStep7ToReact()
                ▼
        ┌───────────────┐
        │ React Format  │
        │ {             │
        │   code: [...],│  ← parseQuestion() extracts
        │   errors: [...│  ← errorPositions
        │ }             │
        └───────────────┘
                │
                ▼
        ┌───────────────┐
        │ Clickable UI  │
        │ - Errors      │
        │   highlighted │
        │ - Click to    │
        │   identify    │
        └───────────────┘
```

---

## 🐛 Common Issues & Solutions

### Issue 1: CORS Error in Browser Console
**Symptom:** `Access-Control-Allow-Origin` error
**Solution:** Add CORS middleware to FastAPI (see Backend CORS Setup section)

### Issue 2: Delimiters Not Parsing Correctly
**Symptom:** No clickable error spans in React
**Solution:**
- Check Step 7 output has `<<>>` delimiters: `console.log(question.code)`
- Verify `error.id` matches text inside delimiters exactly
- Check `parseQuestion()` regex: `/<<([^>]+)>>/g`

### Issue 3: Pipeline Takes Too Long (60+ seconds)
**Symptom:** User waits forever, no feedback
**Solution:** Use SSE streaming instead of blocking:
- Shows step-by-step progress
- User knows it's working
- Can debug which step is slow

### Issue 4: Step 7 `line_number` Field Missing
**Symptom:** React can't find errors
**Solution:** Not needed! React parses line numbers from delimiter positions in code array

---

## 📚 Summary

### What You Need to Do:

1. ✅ **Step 7 already outputs React-compatible format** (code has `<<>>` delimiters)
2. **Create `frontend-main-branch/src/api.js`** with fetch functions
3. **Update `App.jsx`** to add Live Generation mode
4. **Add CORS to FastAPI backend** for localhost:5173
5. **Test** with both demo and live modes
6. **Deploy** (Frontend to Vercel, Backend to Render)

### What You DON'T Need to Do:

- ❌ Modify Step 7 pipeline output format (already compatible!)
- ❌ Complex character position calculations (delimiters handle it)
- ❌ Database queries from React (FastAPI abstracts this)

---

## 🎯 Next Steps

**Priority 1:** Test integration locally
- Start backend: `uvicorn api_server:app --reload`
- Start frontend: `cd frontend-main-branch && npm run dev`
- Try generating one question from pipeline

**Priority 2:** Add UI polish
- Loading spinner during generation
- Step-by-step progress bar (if using SSE)
- Error handling (show user-friendly messages)

**Priority 3:** Production deployment
- Deploy backend to Render
- Deploy frontend to Vercel
- Update CORS origins
- Test end-to-end in production

---

**Questions? Check:**
- Backend API: http://localhost:8000/docs (FastAPI Swagger UI)
- Streamlit Dev UI: http://localhost:8501 (see live pipeline execution)
- React Frontend: http://localhost:5173 (current demo)
