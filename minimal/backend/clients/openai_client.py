import json
import logging
import os
import random
import time
from dataclasses import dataclass
from typing import Any

from openai import APIConnectionError, APIError, OpenAI, RateLimitError

logger = logging.getLogger(__name__)

@dataclass
class UsageMetrics:
    """Token usage and cost metrics from OpenAI response"""
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0
    total_cost_usd: float = 0.0
    model_id: str = ""
    response_time_ms: int = 0

class OpenAIRuntime:
    # Pricing per 1M tokens (approximate, update as OpenAI releases pricing)
    PRICING = {
        "gpt-5": {
            "input": 10.0, "output": 30.0, "cache_creation": 12.5, "cache_read": 2.5
        },
        "gpt-5-mini": {
            "input": 3.0, "output": 12.0, "cache_creation": 3.75, "cache_read": 0.75
        },
        "gpt-5-nano": {
            "input": 0.5, "output": 2.0, "cache_creation": 0.625, "cache_read": 0.125
        }
    }

    def __init__(self):
        self.usage_log: list[UsageMetrics] = []
        self._client: OpenAI | None = None
        self._is_azure = False
        self._import_error: Exception | None = None

        try:
            # Check for Azure OpenAI configuration
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")

            if azure_endpoint and azure_api_key:
                # Azure OpenAI configuration
                self._is_azure = True
                base_url = azure_endpoint.rstrip("/")
                if "/openai" not in base_url:
                    base_url = f"{base_url}/openai/v1/"

                self._client = OpenAI(
                    base_url=base_url,
                    api_key=azure_api_key,
                )
                logger.info("Initialized Azure OpenAI client")
            else:
                # Direct OpenAI API
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY or Azure credentials not found")

                self._client = OpenAI(api_key=api_key)
                logger.info("Initialized OpenAI client")

        except Exception as exc:
            self._import_error = exc
            self._client = None
            logger.error(f"Failed to initialize OpenAI client: {exc}")

    def _ensure_client(self) -> OpenAI:
        if self._client is None:
            raise RuntimeError(
                "OpenAI client unavailable. Set OPENAI_API_KEY or Azure credentials. "
                f"Root cause: {self._import_error}"
            )
        return self._client

    def _calculate_cost(self, model_id: str, usage: dict[str, int]) -> float:
        """Calculate cost based on token usage and model pricing"""
        # Normalize model name for pricing lookup
        model_key = model_id
        if "gpt-5-mini" in model_id:
            model_key = "gpt-5-mini"
        elif "gpt-5-nano" in model_id:
            model_key = "gpt-5-nano"
        elif "gpt-5" in model_id:
            model_key = "gpt-5"

        pricing = self.PRICING.get(model_key, {"input": 0.0, "output": 0.0, "cache_creation": 0.0, "cache_read": 0.0})

        input_cost = usage.get("input_tokens", 0) * pricing["input"] / 1_000_000
        output_cost = usage.get("output_tokens", 0) * pricing["output"] / 1_000_000
        cache_creation_cost = usage.get("cache_creation_input_tokens", 0) * pricing["cache_creation"] / 1_000_000
        cache_read_cost = usage.get("cache_read_input_tokens", 0) * pricing["cache_read"] / 1_000_000

        return input_cost + output_cost + cache_creation_cost + cache_read_cost

    def _log_usage_from_response(self, model_id: str, response: Any, start_time: float) -> UsageMetrics:
        """Extract usage information from OpenAI response and calculate cost"""
        usage = response.usage if hasattr(response, 'usage') else {}

        # OpenAI uses different field names
        usage_dict = {
            "input_tokens": getattr(usage, 'prompt_tokens', 0),
            "output_tokens": getattr(usage, 'completion_tokens', 0),
            "cache_creation_input_tokens": getattr(usage, 'prompt_tokens_details', {}).get('cached_tokens', 0) if hasattr(usage, 'prompt_tokens_details') else 0,
            "cache_read_input_tokens": 0  # OpenAI doesn't expose this separately yet
        }

        metrics = UsageMetrics(
            input_tokens=usage_dict["input_tokens"],
            output_tokens=usage_dict["output_tokens"],
            cache_creation_input_tokens=usage_dict["cache_creation_input_tokens"],
            cache_read_input_tokens=usage_dict["cache_read_input_tokens"],
            total_cost_usd=self._calculate_cost(model_id, usage_dict),
            model_id=model_id,
            response_time_ms=int((time.time() - start_time) * 1000)
        )

        self.usage_log.append(metrics)
        logger.info(f"Model {model_id}: {metrics.input_tokens} input, {metrics.output_tokens} output tokens, "
                   f"cost: ${metrics.total_cost_usd:.4f}, time: {metrics.response_time_ms}ms")

        return metrics

    def _invoke_with_retry(
        self,
        model_id: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 2048,
        temperature: float = 0.0,
        max_retries: int = 5,
        base_delay: float = 2.0
    ) -> tuple[Any, UsageMetrics]:
        """
        Invoke model with exponential backoff retry logic.

        OpenAI has higher rate limits than Bedrock, so we use shorter delays:
        - base_delay=2s: Retries at 2s, 4s, 8s, 16s, 32s
        - max_retries=5: Gives 6 total attempts
        """
        client = self._ensure_client()

        # Use Azure deployment name if configured
        if self._is_azure:
            azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", model_id)
            model_to_use = azure_deployment
        else:
            model_to_use = model_id

        for attempt in range(max_retries + 1):
            start_time = time.time()
            try:
                # Build request parameters
                request_params = {
                    "model": model_to_use,
                    "messages": messages,
                    "temperature": temperature,
                }

                # GPT-5 uses max_completion_tokens instead of max_tokens
                if "gpt-5" in model_id:
                    request_params["max_completion_tokens"] = max_tokens
                else:
                    request_params["max_tokens"] = max_tokens

                # Add tools if provided
                if tools:
                    request_params["tools"] = tools
                    request_params["tool_choice"] = "required"

                response = client.chat.completions.create(**request_params)

                # Log usage
                metrics = self._log_usage_from_response(model_id, response, start_time)

                return response, metrics

            except RateLimitError:
                if attempt == max_retries:
                    logger.error(f"Max retries ({max_retries}) exceeded for RateLimitError")
                    raise

                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Rate limit error on attempt {attempt + 1}/{max_retries + 1}. "
                             f"Retrying in {delay:.2f}s...")
                time.sleep(delay)

            except (APIError, APIConnectionError) as e:
                if attempt == max_retries:
                    logger.error(f"Max retries ({max_retries}) exceeded for {type(e).__name__}")
                    raise

                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"{type(e).__name__} on attempt {attempt + 1}/{max_retries + 1}. "
                             f"Retrying in {delay:.2f}s: {e}")
                time.sleep(delay)

        raise RuntimeError("Should not reach here")

    def get_total_cost(self) -> float:
        """Get total cost across all API calls"""
        return sum(m.total_cost_usd for m in self.usage_log)

    def get_usage_summary(self) -> dict[str, Any]:
        """Get summary of usage metrics"""
        if not self.usage_log:
            return {"total_calls": 0, "total_cost_usd": 0.0}

        total_cost = self.get_total_cost()
        total_input_tokens = sum(m.input_tokens for m in self.usage_log)
        total_output_tokens = sum(m.output_tokens for m in self.usage_log)

        model_breakdown = {}
        for metrics in self.usage_log:
            model = metrics.model_id
            if model not in model_breakdown:
                model_breakdown[model] = {
                    "calls": 0, "cost": 0.0, "input_tokens": 0, "output_tokens": 0
                }
            model_breakdown[model]["calls"] += 1
            model_breakdown[model]["cost"] += metrics.total_cost_usd
            model_breakdown[model]["input_tokens"] += metrics.input_tokens
            model_breakdown[model]["output_tokens"] += metrics.output_tokens

        return {
            "total_calls": len(self.usage_log),
            "total_cost_usd": total_cost,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "model_breakdown": model_breakdown
        }

    def invoke(
        self,
        model_id: str,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.0,
    ) -> str:
        """Invoke model with retry logic and cost tracking"""
        messages = [{"role": "user", "content": prompt}]

        response, _ = self._invoke_with_retry(
            model_id, messages, max_tokens=max_tokens, temperature=temperature
        )

        # Extract text from response
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content or "Error: No content generated."

        return "Error: No response choices."

    def invoke_with_tools(
        self,
        model_id: str,
        prompt: str,
        tools: list[dict[str, Any]],
        max_tokens: int = 2048,
        use_thinking: bool = False,
        thinking_budget: int = 2048,
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        """Invoke model with tools, retry logic and cost tracking"""
        # Note: GPT-5 thinking mode may differ from Claude's implementation
        # For now, we'll use standard function calling

        messages = [{"role": "user", "content": prompt}]

        response, _ = self._invoke_with_retry(
            model_id, messages, tools=tools, max_tokens=max_tokens, temperature=temperature
        )

        # Extract tool call from response
        if response.choices and len(response.choices) > 0:
            message = response.choices[0].message
            if message.tool_calls and len(message.tool_calls) > 0:
                tool_call = message.tool_calls[0]
                try:
                    return json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    return {"error": "Failed to parse tool call arguments"}

        return {"error": "No tool call found in response"}
