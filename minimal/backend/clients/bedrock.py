import json
import time
from typing import Any, Dict, List, Optional

import boto3
from botocore.config import Config


class BedrockRuntime:
    def __init__(self, region: str = "us-west-2"):
        self.region = region
        self._client: Optional[Any] = None
        self._import_error: Optional[Exception] = None
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

    def invoke(self, model_id: str, prompt: str, max_tokens: int = 2048) -> str:
        client = self._ensure_client()
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        }
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )
        data = json.loads(response["body"].read())
        return data.get("content", [{}])[0].get("text", "Error: No content generated.")

    def invoke_with_tools(
        self,
        model_id: str,
        prompt: str,
        tools: List[Dict[str, Any]],
        max_tokens: int = 2048,
        use_thinking: bool = False,
        thinking_budget: int = 2048,
    ) -> Dict[str, Any]:
        client = self._ensure_client()
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools,
            "temperature": 0.7,
        }
        if use_thinking:
            body["thinking"] = {"type": "enabled", "budget_tokens": thinking_budget}

        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )
        data = json.loads(response["body"].read())
        for content in data.get("content", []):
            if content.get("type") == "tool_use":
                return content.get("input", {})
        return {"error": "No tool use found in response"}
