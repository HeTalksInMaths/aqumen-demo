# 004 – Playwright E2E & Screenshot Harness

## Objective
Provide an automated way for Claude Code (and developers) to open the React app, capture Student/Dev mode screenshots, and run UI checks.

## Key additions
- `frontend-main-branch/package.json` — added `@playwright/test` (dev dependency) and `npm run test:e2e`.
- `frontend-main-branch/playwright.config.ts` — configures Playwright to start Vite automatically, target `http://localhost:5173`, and retain traces/screenshots on failure.
- `frontend-main-branch/tests/e2e/dev-student-screenshots.spec.ts` — two smoke tests that visit Student Mode and Dev Mode, asserting key UI elements and attaching full-page screenshots.

## Usage
1. Install dependencies: `npm install` (requires network access).  
2. Install browsers once: `npx playwright install` (or `npx playwright install --with-deps` if needed).  
3. Run tests: `npm run test:e2e`.
   - Playwright will launch Vite, navigate both views, and store artifacts under `playwright-report/`.

## Next steps
- Expand tests to interact with live pipeline runs (e.g., trigger generation, wait for SSE updates).
- Integrate the command in CI to auto-refresh screenshots for design reviews.
