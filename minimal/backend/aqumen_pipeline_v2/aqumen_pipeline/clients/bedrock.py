import json
import time
from typing import Dict, Any, List

class BedrockRuntime:
    def __init__(self, region: str = "us-west-2"):
        self.region = region
        self.client = None
        self._import_err = None
        try:
            import boto3  # lazy protection for dev envs without boto3
            self.client = boto3.client("bedrock-runtime", region_name=region)
        except Exception as e:
            self._import_err = e
            self.client = None

    def _ensure(self):
        if self.client is None:
            raise RuntimeError(f"Bedrock client unavailable. Install boto3/configure AWS. Root error: {self._import_err}")

    def invoke(self, model_id: str, prompt: str, max_tokens: int = 2048) -> str:
        self._ensure()
        time.sleep(1)
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        }
        resp = self.client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )
        data = json.loads(resp["body"].read())
        return (data.get("content",[{}])[0].get("text")) or "Error: No content generated."

    def invoke_with_tools(self, model_id: str, prompt: str, tools: List[Dict[str, Any]],
                          max_tokens: int = 2048, use_thinking: bool=False, thinking_budget: int=2048) -> Dict[str, Any]:
        self._ensure()
        time.sleep(1)
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools,
            "temperature": 0.7,
        }
        if use_thinking:
            body["thinking"] = {"type":"enabled","budget_tokens":thinking_budget}
        resp = self.client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )
        data = json.loads(resp["body"].read())
        for c in data.get("content", []):
            if c.get("type") == "tool_use":
                return c.get("input", {})
        return {"error": "No tool use found in response"}
