# Frontend Bug Fix Update - 2025-10-12

## **Current Issue Identified**

The frontend has several bugs with the 2x2 mode functionality where student demo mode should show the original 10 hardcoded questions (Transformers, RAG, etc.) but currently shows database-generated assessments instead.

## **Root Cause Analysis**

### **Problem Location**: `minimal/frontend/src/demoData.js`
- Current file contains only 2 database-generated assessments:
  1. "Quadratic equations - Optimization problems"
  2. "Executive assistant meeting scheduling"
- The `studentModeQuestions` function (lines 190-225) tries to generate 10 questions but only has 2 database assessments to work with
- The original 10 hardcoded questions about Transformers and RAG are missing

### **Expected Behavior**:
- **Student + Demo Mode**: Should show 10 original hardcoded questions with Transformers/RAG content
- **Dev + Demo Mode**: Should show database assessments with 7-step pipeline visualization
- **Dev + Live Mode**: Should connect to backend for real generation
- **Student + Live Mode**: Should show empty state until content is generated

## **Solution Required**

### **Step 1: Restore Original Content**
- **File to update**: `/Users/hetalksinmaths/Downloads/demoData.js` (you have the correct content)
- **Destination**: `minimal/frontend/src/demoData.js`
- **Action**: Replace current file with your original content that has the proper 10 hardcoded questions

### **Step 2: Fix Mode Separation**
After restoring original demoData.js:
- `demoAssessments` → Database-generated assessments (for Dev mode)
- `studentModeQuestions` → Original 10 hardcoded questions (for Student mode)
- Update App.jsx to use proper separation

### **Step 3: Fix Remaining Issues**
- **Dev + Demo Mode**: Add 7-step pipeline display functionality
- **Autoloader**: Add "Finite Group Theory" run as third tab
- **Tab Navigation**: Fix switching between assessments with pipeline steps

## **Files to Modify**
1. `minimal/frontend/src/demoData.js` - **RESTORE from your file**
2. `minimal/frontend/src/App.jsx` - **Update mode logic**
3. `minimal/frontend/src/components/PipelinePanel.jsx` - **Add pipeline step display**
4. `minimal/frontend/src/api.js` - **Add pipeline history endpoint**
5. `minimal/frontend/tests/e2e/bug-fixes.spec.ts` - **Add E2E tests**

## **Next Steps**
1. Start new session and reference this UPDATE.md file
2. Replace `demoData.js` with content from `/Users/hetalksinmaths/Downloads/demoData.js`
3. Test that Student + Demo Mode shows original 10 questions
4. Continue with remaining bug fixes as outlined above

## **Current Server Status**
- Backend: ✅ Running on port 8000 with live generation
- Frontend: ✅ Running on port 5173
- Database: ✅ Contains 3 pipeline runs (Quadratic, Executive Assistant, Finite Group Theory)

## **Priority Order**
1. **HIGH**: Restore original demoData.js (fixes Student + Demo mode)
2. **MEDIUM**: Fix Dev + Demo pipeline display
3. **MEDIUM**: Add autoloader for new runs
4. **LOW**: Add E2E tests for verification

**Reference**: Original content available at `/Users/hetalksinmaths/Downloads/demoData.js`