from typing import Any, Dict, List

from clients.bedrock import BedrockRuntime


class Invoker:
    def __init__(self, runtime: BedrockRuntime):
        self.runtime = runtime

    def text(self, model_id: str, prompt: str, reasoning_effort: str = "low") -> str:
        try:
            return self.runtime.invoke(model_id, prompt, reasoning_effort=reasoning_effort)
        except Exception as exc:  # pragma: no cover - runtime safeguard
            return f"Error: {exc}"

    def tools(
        self,
        model_id: str,
        prompt: str,
        tools: List[Dict[str, Any]],
        use_thinking: bool = False,
        reasoning_effort: str = "medium",
    ) -> Dict[str, Any]:
        try:
            return self.runtime.invoke_with_tools(
                model_id,
                prompt,
                tools,
                use_thinking=use_thinking,
                reasoning_effort=reasoning_effort,
            )
        except Exception as exc:  # pragma: no cover - runtime safeguard
            return {"error": f"Error: {exc}"}
