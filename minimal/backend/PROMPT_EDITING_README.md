# Prompt Editing System

## Overview

The prompt editing system allows developers to view and edit the prompts used in each step of the 7-step adversarial pipeline through the Dev Mode UI.

## Files

- **`prompts.json`** - Central repository of all pipeline prompts with metadata
- **`api_server.py`** - Contains `/api/update-prompt` endpoint for saving edits
- **`corrected_7step_pipeline.py`** - Pipeline implementation (prompts are currently embedded inline)

## Current State

✅ **Completed:**
- Created `prompts.json` with all 7 step prompts extracted
- Created `POST /api/update-prompt` API endpoint
- Frontend components (PasswordModal, PipelinePanel) support prompt viewing and editing

⏳ **Pending:**
- Modifying pipeline to load prompts from `prompts.json` (requires careful testing)
- Full bidirectional sync between JSON and Python code

## How It Works (Current Implementation)

### 1. View Prompts (Frontend)

In Dev Mode, click any pipeline step to see its full prompt in the `PipelinePanel` component.

### 2. Edit Prompts (Frontend)

Click the "Edit" button next to a prompt, modify the text, then click "Update in Pipeline".

This sends a POST request to `/api/update-prompt`:

```javascript
fetch('http://localhost:8000/api/update-prompt', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    step: 'step1_difficulty_categories',  // or step2, step3, etc.
    new_prompt: 'Your modified prompt text here...'
  })
})
```

### 3. Save to prompts.json (Backend)

The `/api/update-prompt` endpoint:
1. Validates the step name
2. Loads `prompts.json`
3. Updates the `template` field for that step
4. Adds `last_updated` and `updated_by` metadata
5. Saves back to `prompts.json`

**Note:** This updates the JSON file, but the pipeline currently uses hard-coded prompts from `corrected_7step_pipeline.py`.

## Prompts.json Structure

```json
{
  "step1_difficulty_categories": {
    "description": "Generate difficulty categories for a topic",
    "template": "For the topic \"{topic}\", create exactly 3 difficulty levels...",
    "last_updated": "2025-10-11T14:30:00",
    "updated_by": "api"
  },
  "step2_error_catalog": {
    "description": "Generate conceptual error catalog",
    "template": "For the topic \"{topic}\" at {difficulty} level..."
  },
  ...
}
```

### Template Variables

Prompts use Python f-string style placeholders:

- `{topic}` - User-provided topic
- `{subtopic}` - Selected subtopic from Step 1
- `{difficulty}` - Difficulty level
- `{error_patterns}` - Formatted error catalog from Step 2
- `{failure_feedback}` - Feedback from previous retry attempts
- `{haiku_failures}` - Weak model failures from Step 6
- `{context}`, `{title}`, `{question_text}`, `{requirements}`, `{success_criteria}` - Question data

## Next Steps (To Make Edits Actually Work)

### Option A: Modify Pipeline to Use JSON (Recommended for Production)

1. Add prompt loader to `CorrectedSevenStepPipeline.__init__()`:
   ```python
   def _load_prompts(self):
       with open('prompts.json', 'r') as f:
           return json.load(f)
   ```

2. Update each step method to use loaded prompts:
   ```python
   def step1_generate_difficulty_categories(self, topic: str):
       template = self.prompts['step1_difficulty_categories']['template']
       prompt = template.format(topic=topic)
       # ... rest of method
   ```

3. Test thoroughly with existing test topics

### Option B: Manual Sync (Current Workaround)

1. Edit prompts via Dev Mode UI
2. Check `prompts.json` for updates
3. Manually copy changes to `corrected_7step_pipeline.py`
4. Restart the API server

### Option C: Create sync_prompts.py Script

```python
# sync_prompts.py - Bidirectional sync tool
# Usage:
#   python sync_prompts.py --extract   # Python → JSON
#   python sync_prompts.py --apply     # JSON → Python
```

## Testing

After modifying the pipeline to use `prompts.json`:

```bash
cd minimal/backend

# Test single topic
python -c "
from corrected_7step_pipeline import CorrectedSevenStepPipeline
pipeline = CorrectedSevenStepPipeline()
result = pipeline.run_full_pipeline('LLM Post-Training with DPO', max_attempts=1)
print(f'Success: {result.final_success}')
"

# Run full test suite
python corrected_7step_pipeline.py
```

## Security Note

The `/api/update-prompt` endpoint is protected by the same Dev Mode password (`VITE_DEV_PASSWORD=menaqu`). Only users who can access Dev Mode can edit prompts.

## FAQ

**Q: Why aren't my prompt edits affecting the pipeline?**
A: The pipeline currently uses hard-coded prompts from the Python file. You need to implement Option A above to make edits take effect.

**Q: Will editing prompts break the pipeline?**
A: Changes to prompt templates can affect model outputs. Always test with a known topic after editing.

**Q: Can I add new template variables?**
A: Yes, but you must also update the corresponding step method to pass that variable to `.format()`.

**Q: How do I revert to default prompts?**
A: Delete `prompts.json` and restart the server - it will regenerate from the Python code defaults.

## Example: Editing Step 1 Prompt

1. Open Dev Mode (password: `menaqu`)
2. Run a generation to see pipeline steps
3. Click "Step 1" tab
4. Click "Edit" button
5. Modify the prompt text:
   ```
   For the topic "{topic}", create exactly 5 difficulty levels (instead of 3)...
   ```
6. Click "Update in Pipeline"
7. Check `minimal/backend/prompts.json` - you'll see your edit with timestamp
8. **Current limitation:** Pipeline still uses old prompt until you implement Option A

## Support

For issues or questions, check:
- Frontend component: `minimal/frontend/src/components/PipelinePanel.jsx`
- Backend endpoint: `minimal/backend/api_server.py` (line 306)
- Prompt storage: `minimal/backend/prompts.json`
