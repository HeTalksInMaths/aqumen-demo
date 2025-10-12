# Step 7 Validation Fix - Implementation Summary

**Date:** October 11, 2025
**Status:** ✅ COMPLETED

---

## Changes Implemented

### Flow: Model Output → Auto-Fix → Validation → Retry (if needed)

```
┌─────────────────┐
│ Model generates │
│  Step 7 output  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   AUTO-FIX      │  ← NEW LAYER
│ Parse stringified│
│   arrays if     │
│   detected      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   VALIDATION    │
│ Check schema    │
│ compliance      │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
  PASS      FAIL
    │         │
    │         ▼
    │    ┌─────────────┐
    │    │   RETRY     │
    │    │ (max 3x)    │
    │    └─────────────┘
    │
    ▼
SUCCESS
```

---

## 1. Tool Schema Strengthening (`tools.json`)

### File: `minimal/backend/tools.json`

**Changes to `code` field (line 92-98):**

```json
"code": {
  "type": "array",
  "items": {"type": "string"},
  "minItems": 24,                    // ← NEW: JSON Schema constraint
  "maxItems": 60,                    // ← NEW: JSON Schema constraint
  "description": "Native JSON array where each element is ONE line of code as a string. Example: [\"import torch\", \"class MyClass:\", \"    def __init__(self):\", \"        pass\"]. CRITICAL: Return a JSON array, NOT a stringified/escaped array. Mark errors inline with <<error_substring>> delimiters."
  // ← NEW: Explicit example + negative instruction
}
```

**Changes to `errors` field (line 99-119):**

```json
"errors": {
  "type": "array",
  "minItems": 3,                     // ← NEW: JSON Schema constraint
  "maxItems": 5,                     // ← NEW: JSON Schema constraint
  "items": {
    "type": "object",
    "properties": {
      "id": {
        "type": "string",
        "description": "EXACT text between << >> delimiters (character-for-character match). Example: if code has <<result = model(x)>>, id must be exactly \"result = model(x)\"."
        // ← NEW: Concrete example
      },
      "description": {
        "type": "string",
        "maxLength": 150,              // ← NEW: JSON Schema constraint
        "description": "Concise explanation (1-2 sentences, under 150 chars) of WHY it's wrong and what the correct approach should be."
      }
    },
    "required": ["id", "description"]
  },
  "description": "Array of 3-5 conceptual/algorithmic errors (not typos) with matching IDs from the code. Each error 'id' must appear EXACTLY ONCE in the code array wrapped in << >> delimiters."
  // ← NEW: Emphasizes uniqueness requirement
}
```

**Impact:**
- More explicit guidance for the model
- JSON Schema constraints (`minItems`, `maxItems`, `maxLength`)
- Concrete examples showing correct format
- Negative examples warning against stringified arrays

---

## 2. Auto-Fix Fallback (`corrected_7step_pipeline.py`)

### File: `minimal/backend/corrected_7step_pipeline.py`

**Location:** Line 666-676 (in `_validate_assessment_payload` method)

```python
code_lines = payload.get("code")

# AUTO-FIX: If model returned stringified JSON array, parse it
if isinstance(code_lines, str):
    try:
        parsed = json.loads(code_lines)
        if isinstance(parsed, list) and all(isinstance(line, str) for line in parsed):
            code_lines = parsed
            logger.warning(f"Step 7 auto-fix: Converted stringified array to native JSON array ({len(parsed)} lines)")
    except (json.JSONDecodeError, TypeError):
        pass  # Fall through to validation error below

if not isinstance(code_lines, list) or not all(isinstance(line, str) for line in code_lines):
    errors.append("Code must be an array of strings.")
    code_lines = []
```

**How it works:**
1. **Check:** Is `code` field a string? (Should be an array)
2. **Attempt parse:** Try to parse as JSON
3. **Validate parsed:** Ensure it's a list of strings
4. **Auto-fix:** Replace string with parsed array
5. **Log:** Warn about the auto-fix (for monitoring)
6. **Fallback:** If parse fails, proceed to validation error + retry

**Example:**

**Before (would trigger retry):**
```json
{
  "code": "[\n  \"import torch\",\n  \"def foo():\"\n]"  // ❌ STRING
}
```

**After auto-fix (passes first attempt):**
```json
{
  "code": ["import torch", "def foo()"]  // ✅ ARRAY
}
```

---

## Expected Impact

### Baseline (Before Fixes):
- **Step 7 retry rate:** ~50% (1 failure observed, 1 success = 50%)
- **Root cause:** Model returns stringified array instead of native JSON array
- **Cost per retry:** ~$0.05 (Opus 4 output tokens)

### After Tool Schema Improvements:
- **Expected retry rate:** 10-20%
- **Improvement:** Model gets clearer guidance with examples and constraints
- **Rationale:** Explicit examples + negative instructions reduce ambiguity

### After Auto-Fix Layer:
- **Expected retry rate:** <5%
- **Improvement:** Catches ~80% of stringified array cases automatically
- **Rationale:** Even if model makes the mistake, we fix it before validation

### Combined Impact:
- **Baseline:** 50% retry rate
- **Target:** <5% retry rate
- **Improvement:** 90% reduction in retries
- **Cost savings:** ~$0.045 per pipeline run (from $0.05 to $0.005)

---

## Testing Plan

### Test Case 1: Verify Auto-Fix Works
**Input:** Manually create a stringified array response
**Expected:** Auto-fix converts it, validation passes, no retry
**Command:**
```python
# In corrected_7step_pipeline.py test
payload = {
    "code": "[\n  \"import torch\",\n  \"def foo():\"\n]",  # Stringified
    "errors": [...]
}
result = pipeline._validate_assessment_payload(payload)
# Should pass validation after auto-fix
```

### Test Case 2: Full Pipeline Run
**Topic:** Any new topic (e.g., "Transformer Attention Mechanisms")
**Expected:** Step 7 succeeds on first attempt (with auto-fix logging if needed)
**Metrics to track:**
- Step 7 attempts count
- Auto-fix trigger count (check logs for "auto-fix" warnings)
- Final success rate

### Test Case 3: Failure Fallback
**Input:** Completely invalid `code` field (not a string or array)
**Expected:** Auto-fix skips, validation catches error, retry logic triggers
**Purpose:** Ensure auto-fix doesn't break existing validation

---

## Monitoring

### Logs to Watch:

**Auto-fix triggered:**
```
WARNING:corrected_7step_pipeline:Step 7 auto-fix: Converted stringified array to native JSON array (40 lines)
```

**First-attempt success (no auto-fix needed):**
```
INFO:corrected_7step_pipeline:✅ Differentiation achieved on attempt 1
```

**Retry after validation failure:**
```
INFO:corrected_7step_pipeline:Step 7 attempt 1 failed validation, retrying...
```

### Metrics to Track:

```sql
-- Step 7 first-attempt success rate (after fixes)
SELECT
  COUNT(CASE WHEN step_name LIKE '%attempt 1%' AND success = 1 THEN 1 END) * 100.0 /
  COUNT(DISTINCT run_timestamp) as first_attempt_success_rate
FROM enhanced_step_responses
WHERE step_number = 7
  AND timestamp > '2025-10-11';  -- After fix deployment
```

---

## Files Modified

1. ✅ `minimal/backend/tools.json`
   - Lines 92-98: Enhanced `code` field description with examples and constraints
   - Lines 99-119: Enhanced `errors` field with minItems/maxItems and examples

2. ✅ `minimal/backend/corrected_7step_pipeline.py`
   - Lines 666-676: Added auto-fix logic for stringified arrays

---

## Rollback Plan

If the fixes cause issues:

### Rollback Tool Schema:
```bash
cd /Users/hetalksinmaths/adversarial\ demo/minimal/backend
git diff tools.json  # Review changes
git checkout tools.json  # Revert if needed
```

### Rollback Auto-Fix:
Remove lines 668-676 in `corrected_7step_pipeline.py`:
```python
# Delete this block:
# AUTO-FIX: If model returned stringified JSON array, parse it
if isinstance(code_lines, str):
    try:
        parsed = json.loads(code_lines)
        ...
```

---

## Next Steps

1. ✅ Tool schema strengthened
2. ✅ Auto-fix fallback added
3. ⏳ **Test with new topic** (e.g., "Transformer Attention Mechanisms")
4. ⏳ **Monitor metrics** for 5-10 runs
5. ⏳ **Document results** in follow-up analysis

---

## Summary

**Problem:** Step 7 failed ~50% of the time because models returned stringified JSON arrays instead of native arrays.

**Solution:** Two-layer defense:
1. **Prevention:** Stronger tool schemas with explicit examples and JSON Schema constraints
2. **Recovery:** Auto-fix layer that parses stringified arrays before validation

**Expected Outcome:** Retry rate drops from 50% → <5%, saving time and costs while maintaining quality.

**Status:** Ready for testing ✅
