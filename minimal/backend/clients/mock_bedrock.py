import json
from typing import Dict, List, Any

class MockBedrockRuntime:
    """A mock Bedrock client that returns dummy data for testing."""
    def __init__(self, region: str = "us-west-2"):
        pass

    def invoke_text(self, model_id: str, prompt: str, max_tokens: int = 2048) -> str:
        if "sonnet" in model_id:
            return "This is a mock response from the mid-tier model."
        if "haiku" in model_id:
            return "This is a mock response from the weak-tier model."
        return "This is a mock text response."

    def invoke_with_tools(
        self,
        model_id: str,
        prompt: str,
        tools: List[Dict[str, Any]],
        max_tokens: int = 2048,
        use_thinking: bool = False,
        thinking_budget: int = 2048,
    ) -> Dict[str, Any]:
        tool_name = tools[0].get("name")

        if tool_name == "difficulty_categories_tool":
            return {
                "Beginner": ["Subtopic 1", "Subtopic 2", "Subtopic 3"],
                "Intermediate": ["Subtopic 4", "Subtopic 5", "Subtopic 6"],
                "Advanced": ["Subtopic 7", "Subtopic 8", "Subtopic 9"],
            }
        if tool_name == "error_catalog_tool":
            return {
                "errors": [
                    {"mistake": f"Mistake {i}", "why_wrong": f"Reason {i}", "code_pattern": f"Pattern {i}"}
                    for i in range(1, 7)
                ]
            }
        if tool_name == "strategic_question_tool":
            return {
                "title": "Mock Question Title",
                "question_text": "This is a mock question.",
                "context": "Mock Context",
                "success_criteria": "Mock success criteria.",
                "requirements": ["req1", "req2", "req3", "req4"],
                "artifact_type": "code"
            }
        if tool_name == "judge_decision_tool":
            return {
                "differentiation_achieved": True,
                "failures_weaker": ["Mistake 1", "Mistake 2"],
                "reasoning": "Mock reasoning: The weak model made mistakes."
            }
        if tool_name == "student_assessment_tool":
            return {
                "title": "Mock Assessment",
                "difficulty": "Intermediate",
                "content_type": "code",
                "content": [
                    "line 1 <<error_id_1_placeholder_text_to_pass_validation>>",
                    "line 2",
                    "line 3 <<error_id_2_placeholder_text_to_pass_validation>>"
                ] + [f"line {i}" for i in range(4, 25)],
                "errors": [
                    {"id": "error_id_1_placeholder_text_to_pass_validation", "description": "This is a mock error 1."},
                    {"id": "error_id_2_placeholder_text_to_pass_validation", "description": "This is a mock error 2."}
                ]
            }

        return {"error": f"Mock for tool '{tool_name}' not implemented."}