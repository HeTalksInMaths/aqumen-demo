# Frontend Test Harness

- **Framework:** [Node.js Test Runner](https://nodejs.org/api/test.html).
- **Scope:** Ensures the React API adapter correctly serializes request payloads, interprets backend responses, and guards against malformed data.
- **Test Files:**
  - `tests/api.test.mjs`
- **Running Tests:** After installing Node.js 18+ (which ships with the test runner), execute from the repository root:
  ```bash
  node --test code_testing/frontend/tests/api.test.mjs
  ```
