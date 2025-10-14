# 003 – Code Block Indentation Fix

## Motivation
Python-style code in both the hardcoded demo questions and streamed assessments rendered without indentation, reducing readability for error spotting.

## Implementation
- `frontend-main-branch/src/App.jsx:398` — applied `whiteSpace: 'pre'` styling to all code spans so indentation, tabs, and spacing are preserved inside the clickable assessment block.
- Ensured the styling covers both error-highlighted spans and regular text segments for consistent formatting.

## Result
Code samples now mirror their original indentation, making nested blocks and alignment obvious to students and reviewers.

## Verification
1. Run `npm run dev`.
2. Load a hardcoded question (Demo mode) and confirm indentation is intact.
3. Generate a live assessment and verify the streamed question also preserves indentation.
