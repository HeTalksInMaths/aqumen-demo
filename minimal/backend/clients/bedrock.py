import json
import time
import random
import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)

@dataclass
class UsageMetrics:
    """Token usage and cost metrics from AWS Bedrock response"""
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0
    total_cost_usd: float = 0.0
    model_id: str = ""
    response_time_ms: int = 0

class BedrockRuntime:
    # Pricing per 1M tokens (approximate, should be updated periodically)
    PRICING = {
        "us.anthropic.claude-opus-4-1-20250805-v1:0": {
            "input": 15.0, "output": 75.0, "cache_creation": 18.75, "cache_read": 3.75
        },
        "us.anthropic.claude-sonnet-4-5-20250929-v1:0": {
            "input": 3.0, "output": 15.0, "cache_creation": 3.75, "cache_read": 0.75
        },
        "us.anthropic.claude-haiku-4-5-20251001-v1:0": {
            "input": 0.8, "output": 4.0, "cache_creation": 1.0, "cache_read": 0.2
        }
    }

    def __init__(self, region: str = "us-west-2"):
        self.region = region
        self._client: Optional[Any] = None
        self._import_error: Optional[Exception] = None
        self.usage_log: List[UsageMetrics] = []
        try:
            retry_config = Config(
                retries={
                    "max_attempts": 10,
                    "mode": "adaptive",
                }
            )
            self._client = boto3.client(
                "bedrock-runtime", region_name=region, config=retry_config
            )
        except Exception as exc:  # pragma: no cover -- runtime dependency
            self._import_error = exc
            self._client = None

    def _ensure_client(self) -> Any:
        if self._client is None:
            raise RuntimeError(
                "Bedrock client unavailable. Set AWS credentials and install boto3. "
                f"Root cause: {self._import_error}"
            )
        return self._client

    def _calculate_cost(self, model_id: str, usage: Dict[str, int]) -> float:
        """Calculate cost based on token usage and model pricing"""
        pricing = self.PRICING.get(model_id, {"input": 0.0, "output": 0.0, "cache_creation": 0.0, "cache_read": 0.0})

        input_cost = usage.get("input_tokens", 0) * pricing["input"] / 1_000_000
        output_cost = usage.get("output_tokens", 0) * pricing["output"] / 1_000_000
        cache_creation_cost = usage.get("cache_creation_input_tokens", 0) * pricing["cache_creation"] / 1_000_000
        cache_read_cost = usage.get("cache_read_input_tokens", 0) * pricing["cache_read"] / 1_000_000

        return input_cost + output_cost + cache_creation_cost + cache_read_cost

    def _log_usage_from_data(self, model_id: str, response_data: Dict[str, Any], start_time: float) -> UsageMetrics:
        """Extract usage information from parsed response data and calculate cost"""
        usage_data = response_data.get('usage', {})

        metrics = UsageMetrics(
            input_tokens=usage_data.get('input_tokens', 0),
            output_tokens=usage_data.get('output_tokens', 0),
            cache_creation_input_tokens=usage_data.get('cache_creation_input_tokens', 0),
            cache_read_input_tokens=usage_data.get('cache_read_input_tokens', 0),
            total_cost_usd=self._calculate_cost(model_id, usage_data),
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
        body: Dict[str, Any],
        max_retries: int = 5,
        base_delay: float = 40.0
    ) -> Tuple[Dict[str, Any], UsageMetrics]:
        """
        Invoke model with exponential backoff retry logic.

        Configured for 2 calls/minute rate limit:
        - base_delay=40s: Retries at 40s, 80s, 160s, 320s, 640s
        - max_retries=5: Gives 6 total attempts
        - Post-success delay: 2s to help prevent rate limit hits
        """
        client = self._ensure_client()

        for attempt in range(max_retries + 1):
            start_time = time.time()
            try:
                response = client.invoke_model(
                    modelId=model_id,
                    body=json.dumps(body),
                    contentType="application/json",
                    accept="application/json",
                )

                # Read and parse response body once
                response_data = json.loads(response["body"].read())

                # Log usage from parsed data
                metrics = self._log_usage_from_data(model_id, response_data, start_time)

                # Small delay after successful call to help prevent rate limits
                time.sleep(2)

                return response_data, metrics

            except ClientError as e:
                error_code = e.response['Error']['Code']

                # Don't retry on certain errors
                non_retryable_errors = {
                    'AccessDeniedException',
                    'ValidationException',
                    'ResourceNotFoundException',
                    'UnsupportedMediaTypeException'
                }

                if error_code in non_retryable_errors:
                    logger.error(f"Non-retryable error {error_code}: {e}")
                    raise

                # Retry on throttling and service errors
                if attempt == max_retries:
                    logger.error(f"Max retries ({max_retries}) exceeded for {error_code}")
                    raise

                # Calculate exponential backoff with jitter
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Retryable error {error_code} on attempt {attempt + 1}/{max_retries + 1}. "
                             f"Retrying in {delay:.2f}s...")
                time.sleep(delay)

            except BotoCoreError as e:
                if attempt == max_retries:
                    logger.error(f"Max retries ({max_retries}) exceeded for BotoCoreError: {e}")
                    raise

                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"BotoCoreError on attempt {attempt + 1}/{max_retries + 1}. "
                             f"Retrying in {delay:.2f}s: {e}")
                time.sleep(delay)

        raise RuntimeError("Should not reach here")

    def get_total_cost(self) -> float:
        """Get total cost across all API calls"""
        return sum(m.total_cost_usd for m in self.usage_log)

    def get_usage_summary(self) -> Dict[str, Any]:
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
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }

        data, _ = self._invoke_with_retry(model_id, body)
        return data.get("content", [{}])[0].get("text", "Error: No content generated.")

    def invoke_with_tools(
        self,
        model_id: str,
        prompt: str,
        tools: List[Dict[str, Any]],
        max_tokens: int = 2048,
        use_thinking: bool = False,
        thinking_budget: int = 2048,
        temperature: float = 0.0,
    ) -> Dict[str, Any]:
        """Invoke model with tools, retry logic and cost tracking"""
        temp_value = temperature
        if use_thinking:
            temp_value = 1.0  # Claude Extended Thinking requires temperature = 1
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools,
            "temperature": temp_value,
        }
        if use_thinking:
            # Claude requires budget_tokens < max_tokens; we cap at 1024 for stability.
            effective_budget = min(1024, max_tokens - 1)
            if effective_budget <= 0:
                raise ValueError("max_tokens must be greater than 1 when extended thinking is enabled.")
            body["thinking"] = {
                "type": "enabled",
                "budget_tokens": effective_budget,
            }

        data, _ = self._invoke_with_retry(model_id, body)
        for content in data.get("content", []):
            if content.get("type") == "tool_use":
                return content.get("input", {})
        return {"error": "No tool use found in response"}
