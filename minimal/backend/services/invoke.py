from typing import Any

from clients.bedrock import BedrockRuntime


class Invoker:
    def __init__(self, runtime: BedrockRuntime):
        self.runtime = runtime

    def text(self, model_id: str, prompt: str, max_tokens: int = 2048) -> str:
        try:
            return self.runtime.invoke(model_id, prompt, max_tokens)
        except Exception as exc:  # pragma: no cover - runtime safeguard
            return f"Error: {exc}"

    def tools(
        self,
        model_id: str,
        prompt: str,
        tools: list[dict[str, Any]],
        max_tokens: int = 2048,
        use_thinking: bool = False,
        thinking_budget: int = 2048,
    ) -> dict[str, Any]:
        try:
            return self.runtime.invoke_with_tools(
                model_id,
                prompt,
                tools,
                max_tokens=max_tokens,
                use_thinking=use_thinking,
                thinking_budget=thinking_budget,
            )
        except Exception as exc:  # pragma: no cover - runtime safeguard
            return {"error": f"Error: {exc}"}
