# GPT-5 Nano Computer-Use Agent (Minimal Extract)

This repository contains only the files required to run the GPT-5 Nano computer-use agent from the original Aqumen demo. It exposes a simple CLI that drives a Playwright-powered "computer" and calls GPT models for reasoning and action selection.

## What's included

* `cua-agent/cli_gpt5.py` – command-line entrypoint for launching the agent
* `cua-agent/agent/gpt5_agent.py` – main agent loop and action parsing
* `cua-agent/computers/` – abstract computer interface and the default local Playwright implementation
* `cua-agent/utils.py` – shared helpers for API calls, screenshots, and action parsing
* `cua-agent/requirements.txt` – Python dependencies to install

Everything else from the original repository (React frontend, Tailwind config, optional docs) has been removed so this stays as small as possible.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r cua-agent/requirements.txt
playwright install chromium
```

## Running the agent

```bash
python -m cua-agent.cli_gpt5 --start-url https://example.com --model gpt-5-nano
```

### Selecting a model

Pass `--model` to switch between the supported GPT variants:

* `gpt-5-nano` – fast and inexpensive default
* `gpt-5-mini` – larger reasoning budget
* Any other Chat Completions-capable GPT model (for example `gpt-4o`) if you have access

The loop and tooling are identical regardless of which GPT model you choose.

### Environment variables

The agent auto-detects whether to call the public OpenAI endpoint or an Azure-hosted deployment based on the environment variables you set.

**OpenAI (public):**

```bash
export OPENAI_API_KEY="sk-..."
# Optional organization header if you use it
export OPENAI_ORG="org_..."
```

**Azure OpenAI:**

```bash
export AZURE_OPENAI_ENDPOINT="https://your-resource-name.openai.azure.com"
export AZURE_OPENAI_API_KEY="azure-key"
# Either the deployment name of your GPT model or leave unset to reuse --model
export AZURE_OPENAI_DEPLOYMENT="gpt-5-nano"
# Optional, defaults to 2024-08-01-preview
export AZURE_OPENAI_API_VERSION="2024-08-01-preview"
```

When the Azure variables are present the agent switches to the Azure SDK client and routes calls through your deployment. Otherwise it falls back to `https://api.openai.com/v1/chat/completions` with the standard REST call.

## Replacing Anthropic Sonnet/Haiku flows

If you previously relied on Anthropic's Sonnet or Haiku models (often hosted through AWS Bedrock), you can migrate the workflow to GPT-5 Nano or GPT-5 Mini without touching the control loop:

* Keep this repository exactly as is; the CLI and agent already produce the multi-modal prompts required for GPT-5 Nano/Mini.
* Point your environment variables at a GPT deployment (public OpenAI or Azure). No Anthropic SDK calls are used.
* Remove any Anthropic-specific keys (`AWS_ACCESS_KEY_ID`, `ANTHROPIC_API_KEY`, etc.) from your runtime environment unless you still need them elsewhere. The agent never reads them.

> **Do the API calls need to change between AWS Anthropic and Azure GPT?**
>
> Yes. Anthropic's Sonnet/Haiku models (whether called directly or through AWS Bedrock) use the Anthropic Messages API and require the corresponding keys and headers. This minimal agent does **not** include that integration. Instead it always talks to GPT models via OpenAI's Chat Completions API. To migrate, provision GPT-5 Nano/Mini in Azure OpenAI (or use the public OpenAI endpoint) and set the environment variables listed above. No AWS credentials are needed once you switch to GPT models.

## Optional logging

If you drop an `api_logger.py` module next to `cli_gpt5.py`, the helper functions will call `log_api_call(...)` and `write_session_summary(...)` so you can persist request metadata. The agent runs fine without it.
