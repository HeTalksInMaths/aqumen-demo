"""
Multi-provider model configuration and selection.

Supports switching between Anthropic (via AWS Bedrock) and OpenAI models
for the 3-tier pipeline architecture.
"""
from typing import Any

from .bedrock import BedrockRuntime
from .openai_client import OpenAIRuntime

# Model tier mappings
ANTHROPIC_MODELS = {
    "strong": "us.anthropic.claude-opus-4-1-20250805-v1:0",
    "mid": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    "weak": "us.anthropic.claude-haiku-4-5-20251001-v1:0"
}

OPENAI_MODELS = {
    "strong": "gpt-5",
    "mid": "gpt-5-mini",
    "weak": "gpt-5-nano"
}

def get_model_provider(provider: str = "anthropic") -> tuple[Any, dict[str, str]]:
    """
    Get the appropriate client and model IDs for the specified provider.

    Args:
        provider: Either "anthropic" or "openai" (default: "anthropic")

    Returns:
        Tuple of (client_instance, model_dict) where model_dict has keys:
        - "strong": Judge/strategic model
        - "mid": Mid-tier implementation model
        - "weak": Weak-tier error-prone model

    Raises:
        ValueError: If provider is not supported

    Example:
        >>> client, models = get_model_provider("openai")
        >>> client.invoke(models["strong"], "Hello")
    """
    provider = provider.lower()

    if provider == "anthropic":
        client = BedrockRuntime(region="us-west-2")
        models = ANTHROPIC_MODELS
    elif provider == "openai":
        client = OpenAIRuntime()
        models = OPENAI_MODELS
    else:
        raise ValueError(
            f"Unsupported provider: {provider}. Must be 'anthropic' or 'openai'"
        )

    return client, models

def get_provider_info(provider: str = "anthropic") -> dict[str, Any]:
    """
    Get information about a provider's models without initializing the client.

    Args:
        provider: Either "anthropic" or "openai"

    Returns:
        Dictionary with provider name and model configuration

    Example:
        >>> info = get_provider_info("openai")
        >>> print(info["models"]["strong"])
        'gpt-5'
    """
    provider = provider.lower()

    if provider == "anthropic":
        return {
            "provider": "anthropic",
            "backend": "AWS Bedrock",
            "models": ANTHROPIC_MODELS,
            "rate_limits": "Conservative (2 calls/min with retries)",
            "features": ["Extended thinking", "Tool use", "Cost tracking"]
        }
    elif provider == "openai":
        return {
            "provider": "openai",
            "backend": "Azure OpenAI / OpenAI Direct",
            "models": OPENAI_MODELS,
            "rate_limits": "Higher limits for parallel testing",
            "features": ["Function calling", "Cost tracking", "Fast responses"]
        }
    else:
        raise ValueError(
            f"Unsupported provider: {provider}. Must be 'anthropic' or 'openai'"
        )
