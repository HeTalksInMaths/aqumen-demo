import os
import requests
from dotenv import load_dotenv
import json
import base64
from PIL import Image
from io import BytesIO
import io
from urllib.parse import urlparse
import time

try:
    from api_logger import log_api_call
    LOGGING_ENABLED = True
except ImportError:
    LOGGING_ENABLED = False

    def log_api_call(*args, **kwargs):
        return None

load_dotenv(override=True)

BLOCKED_DOMAINS = [
    "maliciousbook.com",
    "evilvideos.com",
    "darkwebforum.com",
    "shadytok.com",
    "suspiciouspins.com",
    "ilanbigio.com",
]


def pp(obj):
    print(json.dumps(obj, indent=4))


def show_image(base_64_image):
    image_data = base64.b64decode(base_64_image)
    image = Image.open(BytesIO(image_data))
    image.show()


def calculate_image_dimensions(base_64_image):
    image_data = base64.b64decode(base_64_image)
    image = Image.open(io.BytesIO(image_data))
    return image.size


def sanitize_message(msg: dict) -> dict:
    """Return a copy of the message with image_url omitted for computer_call_output messages."""
    if msg.get("type") == "computer_call_output":
        output = msg.get("output", {})
        if isinstance(output, dict):
            sanitized = msg.copy()
            sanitized["output"] = {**output, "image_url": "[omitted]"}
            return sanitized
    return msg


def create_response(**kwargs):
    url = "https://api.openai.com/v1/responses"
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }

    openai_org = os.getenv("OPENAI_ORG")
    if openai_org:
        headers["Openai-Organization"] = openai_org

    start_time = time.time()
    response = requests.post(url, headers=headers, json=kwargs)
    duration_ms = int((time.time() - start_time) * 1000)

    try:
        response_data = response.json()
    except ValueError:
        response_data = {"error": response.text}

    if LOGGING_ENABLED:
        try:
            model = kwargs.get("model", "unknown")
            log_api_call(model, kwargs, response_data, duration_ms=duration_ms)
        except Exception as logging_error:
            print(f"Logging failed: {logging_error}")

    if response.status_code != 200:
        print(f"Error: {response.status_code} {response.text}")

    return response_data


def check_blocklisted_url(url: str) -> None:
    """Raise ValueError if the given URL (including subdomains) is in the blocklist."""
    hostname = urlparse(url).hostname or ""
    if any(
        hostname == blocked or hostname.endswith(f".{blocked}")
        for blocked in BLOCKED_DOMAINS
    ):
        raise ValueError(f"Blocked URL: {url}")


# ============================================================================
# GPT-5 Nano Helper Functions
# ============================================================================

def create_chat_completion(
    messages,
    model="gpt-5-nano",
    max_tokens=500,
    temperature=0.7,
    reasoning_tokens=None,
):
    """
    Call OpenAI Chat Completions API (for GPT-5 Nano, GPT-4o, etc.)

    Args:
        messages: List of message dicts with role/content
        model: Model name (default: gpt-5-nano)
        max_tokens: Max tokens in response
        temperature: Sampling temperature

    Returns:
        Response JSON from API
    """
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

    use_azure = bool(azure_endpoint and azure_api_key)

    if use_azure:
        from openai import OpenAI

        base_url = azure_endpoint.rstrip("/")
        deployment = azure_deployment or model
        if "/openai" not in base_url:
            base_url = f"{base_url}/openai/v1/"

        client = OpenAI(
            base_url=base_url,
            api_key=azure_api_key,
        )

        start_time = time.time()
        response = client.chat.completions.create(
            model=deployment,
            messages=messages,
        )
        duration_ms = int((time.time() - start_time) * 1000)
        response_data = response.model_dump()

        if LOGGING_ENABLED:
            try:
                log_api_call(
                    model,
                    {"model": deployment, "messages": messages},
                    response_data,
                    duration_ms=duration_ms,
                )
            except Exception as logging_error:
                print(f"Logging failed: {logging_error}")

        return response_data
    else:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        }

        openai_org = os.getenv("OPENAI_ORG")
        if openai_org:
            headers["OpenAI-Organization"] = openai_org

        payload = {
            "model": model,
            "messages": messages,
        }

        if model.startswith("gpt-5"):
            payload["max_completion_tokens"] = max_tokens
        else:
            payload["max_tokens"] = max_tokens
            payload["temperature"] = temperature
            if reasoning_tokens is not None:
                payload["reasoning"] = {
                    "max_reasoning_tokens": max(0, reasoning_tokens)
                }

    start_time = time.time()
    response = requests.post(url, headers=headers, json=payload)
    duration_ms = int((time.time() - start_time) * 1000)

    try:
        response_data = response.json()
    except ValueError:
        response_data = {"error": response.text}

    if LOGGING_ENABLED:
        try:
            log_api_call(model, payload, response_data, duration_ms=duration_ms)
        except Exception as logging_error:
            print(f"Logging failed: {logging_error}")

    if response.status_code != 200:
        print(f"Error: {response.status_code} {response.text}")
        return {"error": response_data.get("error", "Unknown error")}

    return response_data


def parse_action_from_text(text: str) -> dict:
    """
    Parse natural language from GPT-5 Nano into structured action.

    Examples:
        "Click at (100, 200)" -> {type: "click", x: 100, y: 200}
        "Type 'hello world'" -> {type: "type", text: "hello world"}
        "Scroll down 100 pixels" -> {type: "scroll", scroll_y: -100}

    Returns:
        dict with 'type' and action-specific parameters, or None if no action found
    """
    import re

    text_lower = text.lower()

    # Click pattern: "click at (x, y)" or "click (x, y)" or "click coordinates x, y"
    click_pattern = r'click.*?[(\[]?\s*(\d+)\s*,\s*(\d+)\s*[)\]]?'
    click_match = re.search(click_pattern, text_lower)
    if click_match:
        return {
            "type": "click",
            "x": int(click_match.group(1)),
            "y": int(click_match.group(2))
        }

    # Type pattern: "type 'text'" or 'type "text"'
    type_pattern = r'type\s+[\'"](.+?)[\'"]'
    type_match = re.search(type_pattern, text_lower)
    if type_match:
        return {
            "type": "type",
            "text": type_match.group(1)
        }

    # Scroll pattern: "scroll down X" or "scroll up X"
    scroll_pattern = r'scroll\s+(down|up)\s+(\d+)'
    scroll_match = re.search(scroll_pattern, text_lower)
    if scroll_match:
        direction = scroll_match.group(1)
        amount = int(scroll_match.group(2))
        return {
            "type": "scroll",
            "x": 0,
            "y": 0,
            "scroll_x": 0,
            "scroll_y": -amount if direction == "down" else amount
        }

    # Wait pattern: "wait X seconds" or "wait X ms"
    wait_pattern = r'wait\s+(\d+)\s*(seconds?|ms|milliseconds?)?'
    wait_match = re.search(wait_pattern, text_lower)
    if wait_match:
        duration = int(wait_match.group(1))
        unit = wait_match.group(2) or "ms"
        ms = duration * 1000 if "second" in unit else duration
        return {
            "type": "wait",
            "ms": ms
        }

    # No action found
    return None
