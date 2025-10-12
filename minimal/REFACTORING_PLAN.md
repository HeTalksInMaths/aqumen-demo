# Modularization Refactoring Plan

## Goal
Break up large monolithic files into smaller, testable, editable modules.

## Current State

### Backend
- ❌ `corrected_7step_pipeline.py` - 1,217 lines (too large)
- ✅ `api_server.py` - 412 lines (manageable)
- ✅ `prompts.json` - Already extracted

### Frontend
- ❌ `App.jsx` - 1,660 lines (too large)
- ✅ `PipelinePanel.jsx` - 232 lines (good)
- ✅ `PasswordModal.jsx` - 67 lines (good)
- ✅ `api.js` - 160 lines (good)

---

## Phase 1: Extract Tool Schemas (Backend)

**Estimated Time:** 30 minutes

### 1.1 Create `tools.json`

Extract all tool schemas from the pipeline:

```json
{
  "step1_difficulty_categories": {
    "name": "difficulty_categories_tool",
    "description": "Returns difficulty categories with subtopics",
    "input_schema": { ... }
  },
  "step2_error_catalog": { ... },
  "step3_strategic_question": { ... },
  "step7_student_assessment": { ... }
}
```

### 1.2 Update Pipeline to Load Tools

```python
class CorrectedSevenStepPipeline:
    def __init__(self):
        # ... existing code ...
        self.tools = self._load_tools()

    def _load_tools(self):
        with open('config/tools.json', 'r') as f:
            return json.load(f)
```

### 1.3 Update Step Methods

```python
def step1_generate_difficulty_categories(self, topic: str):
    tools = [self.tools['step1_difficulty_categories']]
    # ... rest of method
```

### 1.4 Create `/api/update-tool` Endpoint

Similar to `/api/update-prompt`, allow editing tool schemas.

---

## Phase 2: Modularize Backend Pipeline

**Estimated Time:** 2 hours

### 2.1 Create Directory Structure

```
minimal/backend/
├── pipeline/
│   ├── __init__.py
│   ├── core.py
│   ├── steps/
│   │   ├── __init__.py
│   │   ├── step1_difficulty.py
│   │   ├── step2_errors.py
│   │   ├── step3_question.py
│   │   ├── step4_sonnet.py
│   │   ├── step5_haiku.py
│   │   ├── step6_judge.py
│   │   └── step7_assessment.py
│   ├── bedrock_client.py
│   └── database.py
└── config/
    ├── prompts.json
    ├── tools.json
    └── models.json
```

### 2.2 Extract Bedrock Client

```python
# pipeline/bedrock_client.py
class BedrockClient:
    def __init__(self, region="us-west-2"):
        self.client = boto3.client('bedrock-runtime', region_name=region)

    def invoke_model(self, model_id, prompt, max_tokens=2048):
        # ... existing logic ...

    def invoke_model_with_tools(self, model_id, prompt, tools, ...):
        # ... existing logic ...
```

### 2.3 Extract Database Operations

```python
# pipeline/database.py
class PipelineDatabase:
    def __init__(self, db_path="pipeline_results.db"):
        self.db_path = db_path
        self._init_database()

    def save_step(self, step: PipelineStep):
        # ... existing logic ...

    def get_recent_runs(self, limit=10):
        # ... new helper ...
```

### 2.4 Extract Each Step

**Example: `pipeline/steps/step1_difficulty.py`**

```python
from typing import Tuple, Dict, List
from ..bedrock_client import BedrockClient
from ..models import PipelineStep

def execute(
    bedrock: BedrockClient,
    topic: str,
    prompt_template: str,
    tool_schema: dict
) -> Tuple[bool, Dict[str, List[str]], PipelineStep]:
    """Step 1: Generate difficulty categories"""

    # Format prompt
    prompt = prompt_template.format(topic=topic)

    # Invoke model
    response = bedrock.invoke_model_with_tools(
        model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        prompt=prompt,
        tools=[tool_schema]
    )

    # Create step record
    step = PipelineStep(
        step_number=1,
        step_name="Generate difficulty categories",
        model_used="Sonnet 4.5",
        success=isinstance(response, dict) and 'error' not in response,
        response=str(response),
        timestamp=datetime.now().isoformat()
    )

    # Extract categories
    categories = response if step.success else {}

    return step.success, categories, step
```

### 2.5 New Core Pipeline

```python
# pipeline/core.py
from .bedrock_client import BedrockClient
from .database import PipelineDatabase
from .steps import (
    step1_difficulty,
    step2_errors,
    step3_question,
    step4_sonnet,
    step5_haiku,
    step6_judge,
    step7_assessment
)

class CorrectedSevenStepPipeline:
    def __init__(self):
        self.bedrock = BedrockClient()
        self.database = PipelineDatabase()
        self.prompts = self._load_config('prompts.json')
        self.tools = self._load_config('tools.json')
        self.models = self._load_config('models.json')

    def run_full_pipeline(self, topic: str, max_attempts: int = 3):
        # Step 1
        success, categories, step1 = step1_difficulty.execute(
            bedrock=self.bedrock,
            topic=topic,
            prompt_template=self.prompts['step1_difficulty_categories']['template'],
            tool_schema=self.tools['step1_difficulty_categories']
        )
        self.database.save_step(step1)

        # ... continue for other steps ...
```

**Benefits:**
- Each step file ~50-100 lines (vs 1,217 line monolith)
- Easy to test individual steps
- Clear separation of concerns

---

## Phase 3: Modularize Frontend

**Estimated Time:** 1.5 hours

### 3.1 Extract Student Mode Components

**`components/student/QuestionDisplay.jsx`**
```javascript
// Display code with error delimiters
export const QuestionDisplay = ({ code, onLineClick }) => {
  // ... ~50 lines
}
```

**`components/student/ErrorSelection.jsx`**
```javascript
// Error selection UI
export const ErrorSelection = ({ errors, selectedErrors, onToggle }) => {
  // ... ~40 lines
}
```

**`components/student/ResultsDisplay.jsx`**
```javascript
// Results after submission
export const ResultsDisplay = ({ correctErrors, missedErrors, score }) => {
  // ... ~60 lines
}
```

### 3.2 Extract Shared Components

**`components/shared/Header.jsx`**
```javascript
export const Header = ({ title, difficulty, viewMode, onModeChange }) => {
  // ... ~30 lines
}
```

**`components/shared/ModeToggle.jsx`**
```javascript
export const ModeToggle = ({ mode, onModeChange, onDevClick }) => {
  // ... ~40 lines
}
```

### 3.3 Simplified App.jsx

```javascript
// App.jsx - Now ~300 lines instead of 1,660
import { QuestionDisplay, ErrorSelection, ResultsDisplay } from './components/student';
import { PipelinePanel, PasswordModal } from './components/dev';
import { Header, ModeToggle } from './components/shared';

function App() {
  // State management
  const [viewMode, setViewMode] = useState('student');
  const [question, setQuestion] = useState(null);
  const [selectedErrors, setSelectedErrors] = useState([]);

  // Render
  return (
    <>
      <PasswordModal {...passwordProps} />
      <div className="app-container">
        <Header {...headerProps} />
        <ModeToggle {...modeProps} />

        {viewMode === 'student' ? (
          <>
            <QuestionDisplay {...questionProps} />
            <ErrorSelection {...errorProps} />
            <ResultsDisplay {...resultsProps} />
          </>
        ) : (
          <PipelinePanel {...pipelineProps} />
        )}
      </div>
    </>
  );
}
```

---

## Phase 4: Testing Strategy

### 4.1 Backend Unit Tests

```python
# tests/test_step1.py
from pipeline.steps import step1_difficulty

def test_step1_success():
    result = step1_difficulty.execute(
        bedrock=mock_bedrock,
        topic="LLM Training",
        prompt_template="...",
        tool_schema={...}
    )
    assert result[0] == True  # success
    assert 'Beginner' in result[1]  # categories
```

### 4.2 Frontend Component Tests

```javascript
// tests/QuestionDisplay.test.jsx
import { render } from '@testing-library/react';
import { QuestionDisplay } from '../components/student';

test('renders code with delimiters', () => {
  const { getByText } = render(
    <QuestionDisplay code={["line 1", "line 2"]} />
  );
  expect(getByText('line 1')).toBeInTheDocument();
});
```

### 4.3 Integration Tests

```bash
# Test full pipeline with modular structure
python -m pytest tests/integration/test_full_pipeline.py
```

---

## Migration Path (Safe)

### Option A: Gradual Migration
1. Create new modular structure alongside old file
2. Test modular version thoroughly
3. Switch API server to use new structure
4. Keep old file as backup for 1 week
5. Delete old file

### Option B: Feature Flag
```python
USE_MODULAR_PIPELINE = os.getenv("USE_MODULAR_PIPELINE", "false") == "true"

if USE_MODULAR_PIPELINE:
    from pipeline.core import CorrectedSevenStepPipeline
else:
    from corrected_7step_pipeline import CorrectedSevenStepPipeline  # old
```

Test in production with flag, flip when confident.

---

## Rollout Timeline

### Week 1: Backend Tools Extraction
- ✅ Day 1-2: Create `tools.json`
- ✅ Day 3: Update pipeline to load tools
- ✅ Day 4: Create `/api/update-tool` endpoint
- ✅ Day 5: Test tool editing in Dev Mode

### Week 2: Backend Modularization
- ✅ Day 1-2: Create directory structure
- ✅ Day 3-4: Extract each step to separate file
- ✅ Day 5: Create core.py orchestrator
- ✅ Day 6-7: Test modular pipeline

### Week 3: Frontend Modularization
- ✅ Day 1-2: Extract student components
- ✅ Day 3: Extract shared components
- ✅ Day 4: Refactor App.jsx
- ✅ Day 5: Test all components
- ✅ Day 6-7: Integration testing

### Week 4: Polish & Deploy
- ✅ Day 1-3: Fix bugs, optimize
- ✅ Day 4: Update documentation
- ✅ Day 5: Deploy to staging
- ✅ Day 6-7: Production deployment

---

## Success Metrics

### Before
- Pipeline file: 1,217 lines
- App.jsx: 1,660 lines
- Tool editing: Requires code changes
- Testing: Hard to isolate steps
- Onboarding time: 2-3 days

### After
- Largest file: ~300 lines
- Tool editing: Via Dev Mode UI
- Testing: Unit tests per step
- Onboarding time: 4-6 hours
- Development velocity: 2-3x faster

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Breaking existing functionality | Keep old file, use feature flag |
| Import path issues | Thorough testing, use absolute imports |
| Performance degradation | Benchmark before/after |
| Database schema changes | Use migrations, maintain compatibility |
| Frontend state management | Use React Context or Zustand |

---

## Next Steps

**Immediate (This Session):**
1. Extract tool schemas to `tools.json`
2. Create `/api/update-tool` endpoint
3. Test tool editing in Dev Mode

**Short-term (Next Session):**
1. Create modular directory structure
2. Extract Step 1 as proof-of-concept
3. Test Step 1 in isolation

**Long-term (Over Multiple Sessions):**
1. Complete backend modularization
2. Complete frontend modularization
3. Full integration testing
4. Deploy to production

---

## Questions to Resolve

1. Should we use TypeScript for new frontend components?
2. Do we want shared state management (Redux/Zustand)?
3. Should tools.json support versioning?
4. Do we need a migration guide for contributors?

Let me know which phase you'd like to start with!
