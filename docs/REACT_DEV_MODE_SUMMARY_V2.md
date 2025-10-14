# React Dev/Student Streaming – V2 Overview

## Key behavior
- **Single streaming path**  
  Every live run (Student or Dev view) hits `/api/generate-stream`, so both views always receive the same step log and final assessment.  
  Code: `frontend-main-branch/src/App.jsx:268-343`

- **Auto-synced Dev panel**  
  - New `_id` markers and `activePipelineTab` state auto-select the most recent step and switch to “Final Assessment” when the stream ends.  
  - Tab buttons replace collapsible panels, making each step or the final output one click away.  
  Code: `App.jsx:26`, `App.jsx:296-312`, `App.jsx:900-989`

- **Student view awareness**  
  Student Mode shows a purple banner when a fresh pipeline run exists; toggling to Dev Mode reveals the detailed trace immediately.  
  Code: `App.jsx:744-752`

## UX flow
1. Launch the Vite app (`npm run dev`) with FastAPI running.
2. In Student Mode, pick Live Generation, enter a topic, and click “Generate”.  
   - A reminder banner appears; the final question pops into the student carousel.
3. Switch to Dev Mode to inspect the same run:  
   - Step tabs show each LLM response (timestamp + model).  
   - “Final Assessment” summarises attempts, differentiation, and weak-model failures.

## Next options
- Keep the Streamlit debugger for deep-dive comparisons or retire it if the React panel covers your workflow.  
- Persist streamed runs to let Dev Mode compare multiple generations without leaving the page.  
