# Frontend Cleanup Instructions

**Date:** October 11, 2025
**Status:** Demo data extracted, cleanup pending

---

## What Was Done ✅

1. **Created `/Users/hetalksinmaths/adversarial demo/minimal/frontend/src/demoData.js`**
   - Extracted GRPO demo data (lines 34-279 from App.jsx)
   - Added Graph Network Fraud Detection demo data (from database)
   - Created modular exports for both demos
   - Added pipeline steps for full dev mode experience

2. **Updated App.jsx imports** (line 6)
   ```javascript
   import { grpoDemo, grpoPipelineSteps, graphNetworkFraudDemo, graphNetworkFraudPipelineSteps } from './demoData';
   ```

---

## What Needs To Be Done 🔧

### Remove Hardcoded Data from App.jsx

**Lines to DELETE:** 33-279 (247 lines total)

```javascript
// DELETE THESE LINES (33-68):
  // GRPO Example for Dev Mode Demo with full 7-step pipeline trace
  const grpoExample = {
    title: "Group-Relative Policy Optimization (GRPO) Implementation",
    difficulty: "Expert",
    code: [
      ... // 15 lines of code
    ],
    errors: [
      ... // 3 error objects
    ]
  };

// DELETE THESE LINES (71-265):
  const grpoPipelineSteps = [
    ... // 7 pipeline step objects, ~195 lines
  ];

// DELETE THESE LINES (267-279):
  const grpoPipelineFinal = {
    ... // Final pipeline metadata
  };
```

### Update References

After deleting, update these references:

**Line ~502 (in useEffect):**
```javascript
// BEFORE:
const parsed = parseQuestion(grpoExample);
setPipelineSteps(grpoPipelineSteps);
setPipelineFinal(grpoPipelineFinal);

// AFTER:
const parsed = parseQuestion(grpoDemo);
setPipelineSteps(grpoPipelineSteps);
setPipelineFinal({
  title: grpoDemo.title,
  difficulty: grpoDemo.difficulty,
  success: true,
  differentiation_achieved: true,
  total_attempts: 3,
  stopped_at_step: 7,
  metadata: {
    topic: "Group-Relative Policy Optimization (GRPO)",
    topic_requested: "GRPO",
    weak_model_failures: 0
  }
});
```

---

## Step-by-Step Cleanup

### Option 1: Manual Deletion

1. Open `minimal/frontend/src/App.jsx`
2. Delete lines 33-279
3. Update the reference at line ~502 (now line ~255 after deletion)
4. Test the app: `npm run dev`
5. Verify demo mode still works

### Option 2: Using Edit Tool (Safer)

```javascript
// Delete the hardcoded data in chunks:

// Chunk 1: Delete grpoExample (lines 33-68)
Edit: old_string = "  // GRPO Example for Dev Mode...\n  const grpoExample = {...}"
      new_string = ""

// Chunk 2: Delete grpoPipelineSteps (lines 71-265)
Edit: old_string = "  const grpoPipelineSteps = [...]"
      new_string = ""

// Chunk 3: Delete grpoPipelineFinal (lines 267-279)
Edit: old_string = "  const grpoPipelineFinal = {...}"
      new_string = ""

// Chunk 4: Update reference
Edit: old_string = "const parsed = parseQuestion(grpoExample);"
      new_string = "const parsed = parseQuestion(grpoDemo);"

Edit: old_string = "setPipelineFinal(grpoPipelineFinal);"
      new_string = "setPipelineFinal({ title: grpoDemo.title, difficulty: grpoDemo.difficulty, success: true, differentiation_achieved: true, total_attempts: 3, stopped_at_step: 7, metadata: { topic: 'Group-Relative Policy Optimization (GRPO)', topic_requested: 'GRPO', weak_model_failures: 0 } });"
```

---

## Benefits of Cleanup

1. **Reduced file size:** App.jsx goes from 1,669 lines → ~1,422 lines (15% reduction)
2. **Better maintainability:** Demo data in one place (`demoData.js`)
3. **Easier to add new demos:** Just add to `demoData.js` and import
4. **Separation of concerns:** UI logic vs demo content

---

## Future Enhancements

### Add Demo Selector

Update `demoData.js` to include a selector:

```javascript
export const availableDemos = [
  {
    id: 'grpo',
    name: 'Group-Relative Policy Optimization',
    difficulty: 'Expert',
    topic: 'RLHF',
    assessment: grpoDemo,
    pipelineSteps: grpoPipelineSteps
  },
  {
    id: 'graph-network-fraud',
    name: 'Graph Network Fraud Detection',
    difficulty: 'Advanced',
    topic: 'GNN',
    assessment: graphNetworkFraudDemo,
    pipelineSteps: graphNetworkFraudPipelineSteps
  }
];
```

Then in App.jsx, add a dropdown to switch between demos:

```javascript
const [selectedDemo, setSelectedDemo] = useState('grpo');

// In useEffect:
const demo = availableDemos.find(d => d.id === selectedDemo);
const parsed = parseQuestion(demo.assessment);
setPipelineSteps(demo.pipelineSteps);
```

---

## Testing Checklist

After cleanup, verify:

- [ ] App loads without errors
- [ ] Demo mode shows GRPO question
- [ ] Dev mode shows pipeline steps
- [ ] Switching to Student mode works
- [ ] Live generation mode works
- [ ] No console errors
- [ ] Vite build succeeds: `npm run build`

---

## Files Modified

1. ✅ **Created:** `minimal/frontend/src/demoData.js` (260 lines)
2. ✅ **Modified:** `minimal/frontend/src/App.jsx` (added import, line 6)
3. ⏳ **Pending:** `minimal/frontend/src/App.jsx` (remove hardcoded data, update refs)

---

## Summary

**Current State:**
- Demo data extracted to `demoData.js`
- Import added to `App.jsx`
- App still uses old hardcoded data (lines 33-279)

**Next Step:**
- Remove hardcoded data from App.jsx
- Update references to use imported demos
- Test to ensure functionality is preserved

**Time Estimate:** 10-15 minutes
