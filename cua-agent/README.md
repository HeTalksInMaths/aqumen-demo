Minimal GPT-5 Nano Playwright Agent
===================================

This folder contains the validated minimal Computer Use agent scaffold that was copied from the `openai-cua-sample-app` project. It launches a Chromium browser via Playwright and drives it with `gpt-5-nano` (or any matching Azure deployment) to perform UI debugging and UX testing tasks.

Layout
------
- `cli_gpt5.py` — CLI entrypoint that wires the agent to the Playwright computer and manages the run loop.
- `agent/` — Holds `GPT5Agent`, which captures screenshots, calls the Chat Completions API, parses actions like `Click at (x, y)`, and executes them through the computer.
- `computers/` — Pared-down Computer protocol implementation for the local Playwright browser.
- `utils.py` — Shared helpers for API calls, screenshot utilities, and the natural-language action parser.
- `requirements.txt` — Exact dependencies for this scaffold.

Quickstart
----------
```bash
cd cua-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```

Configure credentials (choose one path):
```bash
# OpenAI direct
export OPENAI_API_KEY=sk-...

# or Azure OpenAI / Foundry
export AZURE_OPENAI_ENDPOINT=https://<resource>.cognitiveservices.azure.com/openai/v1/
export AZURE_OPENAI_API_KEY=...
export AZURE_OPENAI_DEPLOYMENT=gpt-5-nano
```

Run against a front-end under test:
```bash
python cli_gpt5.py --computer local-playwright --model gpt-5-nano --start-url http://localhost:5173 --show
```

Add `--input "Audit the landing page for UX issues"` for a single turn, or omit `--input` for the interactive loop.

Notes
-----
- Session logging via `api_logger.py` is optional; copy it here if you want per-call JSONL logs.
- When Azure variables are detected, the agent automatically switches to using the Azure deployment; otherwise it falls back to the OpenAI Chat Completions endpoint.
