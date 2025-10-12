# Frontend Debug Summary

## Issues Reported

1. **Live generation stalled** - Generation seems to freeze/not complete
2. **Password modal missing** - Dev Mode button doesn't show password prompt
3. **Step prompts missing** - Pipeline panel doesn't show prompts before generation runs

---

## Investigation Results

### ✅ Issue 1: Password Modal IS Implemented

**Status:** Code is correct, likely not visible due to issue

**Evidence:**
```javascript
// App.jsx line 5
import PasswordModal from './components/PasswordModal';

// App.jsx line 1248
<PasswordModal
  isOpen={showPasswordPrompt}
  password={devPassword}
  setPassword={setDevPassword}
  onSubmit={checkDevPassword}
  onCancel={() => {
    setShowPasswordPrompt(false);
    setDevPassword('');
  }}
/>
```

**Root Cause:** The modal might not be showing because:
1. React Fragment wrapper might have rendering issues
2. `showPasswordPrompt` state not triggering correctly
3. CSS z-index issues

**Fix Needed:** Check browser console for errors

---

### ❌ Issue 2: Step Prompts Won't Show Before Generation

**Status:** DESIGN LIMITATION - Prompts don't exist until pipeline runs

**Why:**
- Steps are created dynamically as pipeline executes
- PipelinePanel expects `pipelineSteps` array from SSE stream
- Prompts are embedded in Python code, not pre-loaded

**Current Flow:**
```
1. User clicks "Generate" (Live mode)
2. SSE stream starts: /api/generate-stream
3. Backend runs step1 → step1 completes → yields PipelineStep object
4. Frontend receives step1 data → adds to pipelineSteps array
5. User can NOW click "Step 1" tab to see prompt
```

**Problem:** Steps only exist AFTER they run, so you can't view prompts in advance.

**Solution Options:**

**Option A: Pre-load Step Definitions (Quick)**
```javascript
// App.jsx - Add static step definitions
const STEP_DEFINITIONS = [
  { step_number: 1, step_name: "Generate difficulty categories", description: "..." },
  { step_number: 2, step_name: "Generate error catalog", description: "..." },
  // ... etc
];

// Show these BEFORE generation starts
{!isGenerating && pipelineSteps.length === 0 && (
  <PipelinePanel
    pipelineSteps={STEP_DEFINITIONS}  // Show placeholders
    ...
  />
)}
```

**Option B: Load from prompts.json (Better)**
```javascript
// Create /api/get-prompts endpoint
@app.get("/api/get-prompts")
async def get_prompts():
    with open('prompts.json', 'r') as f:
        return json.load(f)

// Frontend fetches on mount
useEffect(() => {
  fetch(`${API_BASE_URL}/api/get-prompts`)
    .then(r => r.json())
    .then(prompts => setAvailablePrompts(prompts));
}, []);
```

**Option C: Hybrid (Best)**
- Show step names/numbers before generation
- Show actual prompts from prompts.json
- Update with real data as pipeline runs

---

### ⚠️ Issue 3: Live Generation Stalling

**Possible Causes:**

1. **SSE Connection Issues**
   - EventSource not receiving events
   - CORS blocking SSE stream
   - Backend not sending events

2. **Backend Pipeline Hanging**
   - Bedrock API throttling
   - Network timeout
   - Step failure not handled

3. **Frontend Not Processing Events**
   - `onStepUpdate` callback not firing
   - State not updating
   - Component not re-rendering

**Debug Steps:**

```javascript
// Add debug logging to api.js
eventSource.addEventListener('step', (event) => {
  console.log('📨 Received step event:', event);
  const data = JSON.parse(event.data);
  console.log('📊 Step data:', data);

  if (data.type === 'step') {
    console.log(`✅ Processing step ${data.step_number}`);
    onStepUpdate?.(data);
  }
});
```

**Check browser console for:**
- `📨 Received step event` - Are events arriving?
- `📊 Step data` - What data is in them?
- `✅ Processing step X` - Are callbacks firing?

**Check backend logs:**
```bash
# Is pipeline actually running?
tail -f minimal/backend/logs/current/pipeline_run_*.txt

# Are steps being logged?
sqlite3 minimal/backend/pipeline_results.db \\
  "SELECT step_number, step_name, success FROM enhanced_step_responses ORDER BY id DESC LIMIT 10;"
```

---

## Recommended Fixes

### Fix 1: Add Debug Logging

**File:** `minimal/frontend/src/api.js`

```javascript
export const fetchQuestionStreaming = (topic, maxRetries, onStepUpdate, onComplete, onError) => {
  const url = `${API_BASE_URL}/api/generate-stream?topic=${encodeURIComponent(topic)}&max_retries=${maxRetries}`;

  console.log('🚀 Starting SSE connection:', url);
  const eventSource = new EventSource(url);
  let completed = false;

  eventSource.addEventListener('start', (event) => {
    const data = JSON.parse(event.data);
    console.log('✅ Pipeline started:', data.timestamp);
  });

  eventSource.addEventListener('step', (event) => {
    console.log('📨 RAW EVENT:', event);  // ADD THIS
    const data = JSON.parse(event.data);
    console.log('📊 PARSED DATA:', data);  // ADD THIS

    if (data.type === 'step') {
      console.log(`🔧 Step ${data.step_number}: ${data.description}`);  // ADD THIS
      onStepUpdate?.(data);
    } else if (data.type === 'final') {
      console.log('🏁 Final result received');  // ADD THIS
      completed = true;
      eventSource.close();

      if (data.success && data.assessment) {
        const question = transformStep7ToReact(data.assessment);
        onComplete?.(question, data);
      } else {
        onError?.(new Error(data.error || 'Pipeline completed but no assessment generated'));
      }
    }
  });

  eventSource.addEventListener('error', (event) => {
    console.error('❌ SSE ERROR:', event);  // ADD THIS
    if (!completed) {
      eventSource.close();
      onError?.(new Error('Connection to pipeline failed'));
    }
  });

  // ... rest of code
};
```

### Fix 2: Pre-load Step Information

**File:** `minimal/frontend/src/App.jsx`

Add this near the top of the component:

```javascript
const STEP_DEFINITIONS = [
  {
    _id: 'step1-placeholder',
    step_number: 1,
    step_name: "Generate difficulty categories",
    description: "Generate difficulty categories",
    model: "Sonnet 4.5",
    success: null,
    timestamp: null,
    response_full: null,
    prompt: "Prompts will be loaded from prompts.json..."
  },
  {
    _id: 'step2-placeholder',
    step_number: 2,
    step_name: "Generate error catalog",
    description: "Generate conceptual error catalog",
    model: "Sonnet 4.5",
    success: null,
    timestamp: null,
    response_full: null,
    prompt: "Prompts will be loaded from prompts.json..."
  },
  // ... add all 7 steps
];

// Show placeholders when no real steps exist
const displaySteps = pipelineSteps.length > 0 ? pipelineSteps : STEP_DEFINITIONS;
```

Then pass `displaySteps` instead of `pipelineSteps` to PipelinePanel.

### Fix 3: Add GET /api/get-prompts Endpoint

**File:** `minimal/backend/api_server.py`

```python
@app.get("/api/get-prompts")
async def get_prompts():
    """
    Get all prompts from prompts.json for pre-loading in frontend.
    """
    import os
    import json as json_module

    try:
        prompts_file = os.path.join(os.path.dirname(__file__), "prompts.json")

        if not os.path.exists(prompts_file):
            raise HTTPException(404, "prompts.json not found")

        with open(prompts_file, 'r') as f:
            prompts = json_module.load(f)

        return {"prompts": prompts}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error loading prompts")
        raise HTTPException(500, f"Failed to load prompts: {str(e)}")
```

### Fix 4: Load Prompts on Frontend Mount

**File:** `minimal/frontend/src/App.jsx`

```javascript
const [availablePrompts, setAvailablePrompts] = useState({});

useEffect(() => {
  // Load prompts on mount
  const loadPrompts = async () => {
    try {
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/api/get-prompts`);
      if (response.ok) {
        const data = await response.json();
        setAvailablePrompts(data.prompts);
        console.log('✅ Loaded prompts:', Object.keys(data.prompts));
      }
    } catch (error) {
      console.error('Failed to load prompts:', error);
    }
  };

  loadPrompts();
}, []);
```

---

## Testing Checklist

### Backend Test
```bash
cd minimal/backend
python3 -c "from corrected_7step_pipeline import CorrectedSevenStepPipeline; pipeline = CorrectedSevenStepPipeline(); result = pipeline.run_full_pipeline('Graph Network Fraud Detection'); print(f'Success: {result.final_success}')"
```

### Frontend Test (Local)
1. Start backend: `cd minimal/backend && uvicorn api_server:app --reload --port 8000`
2. Start frontend: `cd minimal/frontend && npm run dev`
3. Open http://localhost:5173
4. Open browser DevTools Console (F12)
5. Click "Dev Mode" button
   - Expected: Password modal appears
   - Check console for errors
6. Enter password: `menaqu`
   - Expected: Dev Mode activates
7. Enter topic: "Graph Network Fraud Detection"
8. Click "Generate" (Live mode)
   - Expected: Console shows:
     ```
     🚀 Starting SSE connection: http://localhost:8000/api/generate-stream?topic=...
     ✅ Pipeline started: 2025-10-11T...
     📨 RAW EVENT: [MessageEvent object]
     📊 PARSED DATA: {type: 'step', step_number: 1, ...}
     🔧 Step 1: Generate difficulty categories
     ...
     ```
9. Click "Step 1" tab in Pipeline Panel
   - Expected: Prompt shows (after step completes)
10. Click "View/Edit Prompt" dropdown
    - Expected: Prompt text appears
    - Expected: Edit/Save buttons appear

### SSE Stream Test (Direct)
```bash
# Test SSE endpoint directly
curl -N "http://localhost:8000/api/generate-stream?topic=Graph%20Network%20Fraud%20Detection&max_retries=1"

# Should see:
# event: start
# data: {"event":"start","topic":"Graph Network Fraud Detection",...}
#
# event: step
# data: {"type":"step","step_number":1,...}
# ...
```

---

## Summary

| Issue | Status | Fix |
|-------|--------|-----|
| Password modal missing | ✅ Code exists | Add console debugging |
| Step prompts missing before generation | ❌ By design | Add `/api/get-prompts` + pre-load |
| Live generation stalling | ⚠️ Unknown | Add SSE debugging logs |

**Next Steps:**
1. Add all debug logging
2. Test locally with console open
3. Share console output if issues persist
4. Implement `/api/get-prompts` endpoint
5. Pre-load step definitions with prompts
