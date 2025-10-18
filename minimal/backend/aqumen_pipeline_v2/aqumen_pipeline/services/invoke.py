from typing import Any

from ..clients.bedrock import BedrockRuntime


class Invoker:
    def __init__(self, runtime: BedrockRuntime):
        self.rt = runtime

    def text(self, model_id: str, prompt: str, max_tokens: int = 2048) -> str:
        try:
            return self.rt.invoke(model_id, prompt, max_tokens)
        except Exception as e:
            return f"Error: {e}"

    def tools(self, model_id: str, prompt: str, tools: list[dict[str, Any]],
              max_tokens: int = 2048, use_thinking: bool=False, thinking_budget: int=2048) -> dict[str, Any]:
        try:
            return self.rt.invoke_with_tools(model_id, prompt, tools, max_tokens, use_thinking, thinking_budget)
        except Exception as e:
            return {"error": f"Error: {e}"}
