import os
import json
import time
import random
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

from openai import OpenAI, AzureOpenAI
from openai import APIError, RateLimitError, APIConnectionError, BadRequestError

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, rely on system env vars

logger = logging.getLogger(__name__)

@dataclass
class UsageMetrics:
    """Token usage and cost metrics from OpenAI response"""
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0
    reasoning_tokens: int = 0  # GPT-5 internal thinking tokens
    total_cost_usd: float = 0.0
    model_id: str = ""
    response_time_ms: int = 0


def convert_anthropic_to_openai_tools(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert Anthropic tool definitions to OpenAI function calling format.
    Detects if tools are already in OpenAI format and skips conversion.

    Enables OpenAI's structured outputs (strict mode) for guaranteed schema compliance.

    Anthropic format:
    {
        "name": "tool_name",
        "description": "Tool description",
        "input_schema": {
            "type": "object",
            "properties": {...},
            "required": [...]
        }
    }

    OpenAI format (with strict mode):
    {
        "type": "function",
        "function": {
            "name": "tool_name",
            "description": "Tool description",
            "strict": true,
            "parameters": {
                "type": "object",
                "properties": {...},
                "required": [...],
                "additionalProperties": false
            }
        }
    }
    """
    openai_tools = []

    for tool in tools:
        if not isinstance(tool, dict):
            continue

        # Check if already in OpenAI format
        if tool.get("type") == "function" and "function" in tool:
            # Already in OpenAI format, use as-is
            openai_tools.append(tool)
            continue

        # Convert from Anthropic format
        input_schema = tool.get("input_schema", {})

        # Ensure additionalProperties: false at root level if it's an object schema
        # (nested objects should already have this from tools.json)
        if isinstance(input_schema, dict) and input_schema.get("type") == "object":
            if "additionalProperties" not in input_schema:
                input_schema = {**input_schema, "additionalProperties": False}

        openai_tool = {
            "type": "function",
            "function": {
                "name": tool.get("name", ""),
                "description": tool.get("description", ""),
                "strict": True,  # Enable structured outputs for 100% schema compliance
                "parameters": input_schema
            }
        }

        openai_tools.append(openai_tool)

    return openai_tools

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
        self.usage_log: List[UsageMetrics] = []
        self._client: Optional[Union[OpenAI, AzureOpenAI]] = None
        self._is_azure = False
        self._azure_default_deployment: Optional[str] = None
        self._azure_api_version: Optional[str] = None
        self._import_error: Optional[Exception] = None

        try:
            # Check for Azure OpenAI configuration
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")

            if azure_endpoint and azure_api_key:
                # Azure OpenAI configuration
                self._is_azure = True
                # Hardcode current required API version; environment can override if needed.
                api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
                endpoint = azure_endpoint.rstrip("/")

                self._client = AzureOpenAI(
                    api_key=azure_api_key,
                    azure_endpoint=endpoint,
                    api_version=api_version,
                )
                self._azure_api_version = api_version
                self._azure_default_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
                if not self._azure_default_deployment:
                    logger.warning(
                        "AZURE_OPENAI_DEPLOYMENT not set – using model IDs as deployment names. "
                        "Ensure Azure deployments match the requested model IDs."
                    )
                logger.info("Initialized Azure OpenAI client with api_version=%s", api_version)
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

    def _ensure_client(self) -> Union[OpenAI, AzureOpenAI]:
        if self._client is None:
            raise RuntimeError(
                "OpenAI client unavailable. Set OPENAI_API_KEY or Azure credentials. "
                f"Root cause: {self._import_error}"
            )
        return self._client

    def _calculate_cost(self, model_id: str, usage: Dict[str, int]) -> float:
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

        # Handle prompt_tokens_details as object (not dict)
        cached_tokens = 0
        if hasattr(usage, 'prompt_tokens_details') and usage.prompt_tokens_details:
            details = usage.prompt_tokens_details
            if hasattr(details, 'cached_tokens'):
                cached_tokens = details.cached_tokens or 0

        # Handle completion_tokens_details for reasoning tokens
        reasoning_tokens = 0
        if hasattr(usage, 'completion_tokens_details') and usage.completion_tokens_details:
            details = usage.completion_tokens_details
            if hasattr(details, 'reasoning_tokens'):
                reasoning_tokens = details.reasoning_tokens or 0

        # OpenAI uses different field names
        usage_dict = {
            "input_tokens": getattr(usage, 'prompt_tokens', 0),
            "output_tokens": getattr(usage, 'completion_tokens', 0),
            "cache_creation_input_tokens": cached_tokens,
            "cache_read_input_tokens": 0  # OpenAI doesn't expose this separately yet
        }

        metrics = UsageMetrics(
            input_tokens=usage_dict["input_tokens"],
            output_tokens=usage_dict["output_tokens"],
            cache_creation_input_tokens=usage_dict["cache_creation_input_tokens"],
            cache_read_input_tokens=usage_dict["cache_read_input_tokens"],
            reasoning_tokens=reasoning_tokens,
            total_cost_usd=self._calculate_cost(model_id, usage_dict),
            model_id=model_id,
            response_time_ms=int((time.time() - start_time) * 1000)
        )

        self.usage_log.append(metrics)
        log_msg = f"Model {model_id}: {metrics.input_tokens} input, {metrics.output_tokens} output tokens"
        if reasoning_tokens > 0:
            log_msg += f" ({reasoning_tokens} reasoning)"
        log_msg += f", cost: ${metrics.total_cost_usd:.4f}, time: {metrics.response_time_ms}ms"
        logger.info(log_msg)
        return metrics

    def _invoke_with_retry(
        self,
        model_id: str,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.0,
        reasoning_effort: str = "medium",
        max_retries: int = 5,
        base_delay: float = 2.0
    ) -> Tuple[Any, UsageMetrics]:
        """
        Invoke model with exponential backoff retry logic.

        OpenAI has higher rate limits than Bedrock, so we use shorter delays:
        - base_delay=2s: Retries at 2s, 4s, 8s, 16s, 32s
        - max_retries=5: Gives 6 total attempts
        """
        client = self._ensure_client()

        # Use Azure deployment name if configured, otherwise use model_id
        # This matches the CUA pattern: deployment = azure_deployment or model
        if self._is_azure:
            azure_deployment = self._azure_default_deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT")
            model_to_use = azure_deployment or model_id
        else:
            model_to_use = model_id

        for attempt in range(max_retries + 1):
            start_time = time.time()
            try:
                # Build request parameters
                request_params = {
                    "model": model_to_use,
                    "messages": messages,
                }

                # GPT-5 models: don't pass temperature (only default 1 is supported)
                # Set reasoning_effort directly (low or medium)
                if "gpt-5" in model_id:
                    request_params["reasoning_effort"] = reasoning_effort
                else:
                    request_params["temperature"] = temperature

                # Add tools if provided (convert Anthropic format to OpenAI format)
                if tools:
                    converted_tools = convert_anthropic_to_openai_tools(tools)
                    request_params["tools"] = converted_tools
                    # Disable parallel tool calls (required when using strict mode)
                    request_params["parallel_tool_calls"] = False

                    force_required = True
                    if self._is_azure:
                        version = self._azure_api_version
                        try:
                            version_parts = tuple(int(part) for part in (version or "").split("-")[:3])
                            min_required = (2024, 6, 1)
                            force_required = version_parts >= min_required
                        except Exception:
                            force_required = False
                    if force_required:
                        request_params["tool_choice"] = "required"

                response = client.chat.completions.create(**request_params)

                # Log usage
                metrics = self._log_usage_from_response(model_id, response, start_time)

                return response, metrics

            except RateLimitError as e:
                if attempt == max_retries:
                    logger.error(f"Max retries ({max_retries}) exceeded for RateLimitError")
                    raise

                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Rate limit error on attempt {attempt + 1}/{max_retries + 1}. "
                             f"Retrying in {delay:.2f}s...")
                time.sleep(delay)

            except BadRequestError as e:
                # Schema validation or parameter errors - usually not retriable
                logger.error(f"BadRequestError on model {model_id}: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    try:
                        error_details = e.response.json()
                        logger.error(f"Error details: {json.dumps(error_details, indent=2)}")
                    except Exception:
                        logger.error(f"Error details: {str(e)}")
                else:
                    logger.error(f"Error message: {str(e)}")
                raise  # Don't retry schema/parameter errors

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
        temperature: float = 0.0,
        reasoning_effort: str = "low",
    ) -> str:
        """Invoke model with retry logic and cost tracking"""
        messages = [{"role": "user", "content": prompt}]

        response, _ = self._invoke_with_retry(
            model_id, messages, temperature=temperature, reasoning_effort=reasoning_effort
        )

        # Extract text from response
        if response.choices and len(response.choices) > 0:
            choice = response.choices[0]
            finish_reason = choice.finish_reason
            content = choice.message.content

            if content is None:
                # Log detailed diagnostics when content is missing
                logger.warning(
                    f"Model {model_id} returned no content. "
                    f"finish_reason={finish_reason}, "
                    f"message={choice.message}"
                )
                refusal = getattr(choice.message, 'refusal', None)
                if refusal:
                    return f"Error: Content refused by model (reason: {refusal})"
                return f"Error: No content generated (finish_reason: {finish_reason})"

            return content

        return "Error: No response choices."

    def invoke_with_tools(
        self,
        model_id: str,
        prompt: str,
        tools: List[Dict[str, Any]],
        use_thinking: bool = False,
        reasoning_effort: str = "medium",
        temperature: float = 0.0,
    ) -> Dict[str, Any]:
        """Invoke model with tools, retry logic and cost tracking"""
        # Note: GPT-5 thinking mode may differ from Claude's implementation
        # For now, we'll use standard function calling

        # Adjust temperature for thinking mode (matching bedrock.py behavior)
        temp_value = temperature
        if use_thinking:
            temp_value = 1.0  # Thinking mode requires temperature = 1

        messages = [{"role": "user", "content": prompt}]

        response, _ = self._invoke_with_retry(
            model_id, messages, tools=tools, temperature=temp_value, reasoning_effort=reasoning_effort
        )

        # Extract tool call from response
        if response.choices and len(response.choices) > 0:
            choice = response.choices[0]
            message = choice.message
            finish_reason = choice.finish_reason

            if message.tool_calls and len(message.tool_calls) > 0:
                tool_call = message.tool_calls[0]
                try:
                    return json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    return {"error": "Failed to parse tool call arguments"}

            # Log detailed info when tool call missing
            logger.warning(
                f"Model {model_id} did not return tool call. "
                f"finish_reason={finish_reason}, "
                f"has_content={message.content is not None}, "
                f"refusal={getattr(message, 'refusal', None)}"
            )
            if message.content:
                logger.info(f"Model returned text instead: {message.content[:200]}...")

            refusal = getattr(message, 'refusal', None)
            if refusal:
                return {"error": f"Tool call refused by model: {refusal}"}

            return {"error": f"No tool call found (finish_reason: {finish_reason})"}

        return {"error": "No response choices"}
