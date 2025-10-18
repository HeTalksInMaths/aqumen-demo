from typing import Any


def difficulty_categories_tool() -> dict[str, Any]:
    return {
        "name": "difficulty_categories_tool",
        "description": "Returns difficulty categories with subtopics",
        "input_schema": {
            "type": "object",
            "properties": {
                "Beginner": {"type": "array", "items": {"type": "string"}},
                "Intermediate": {"type": "array", "items": {"type": "string"}},
                "Advanced": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["Beginner", "Intermediate", "Advanced"],
        },
    }

def error_catalog_tool(keep_likelihood: bool = True) -> dict[str, Any]:
    props = {
        "mistake": {"type": "string"},
        "why_wrong": {"type": "string"},
        "match_hint": {"type": "string"},   # renamed (domain-agnostic)
        "impact": {"type": "string", "enum": ["Minor", "Moderate", "Major"]},
        "domain_specific": {"type": "boolean"},
    }
    if keep_likelihood:
        props.update({
            "likelihood_strong_avoids": {"type": "number"},
            "likelihood_weak_makes": {"type": "number"},
        })
    return {
        "name": "error_catalog_tool",
        "description": "Structured catalog of conceptual mistakes (domain-agnostic)",
        "input_schema": {
            "type": "object",
            "properties": {
                "errors": {
                    "type": "array",
                    "items": {"type": "object", "properties": props, "required": list(props.keys())}
                }
            },
            "required": ["errors"],
        },
    }

def strategic_question_tool() -> dict[str, Any]:
    return {
        "name": "strategic_question_tool",
        "description": "Returns a strategic challenge yielding a concrete artifact",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "question_text": {"type": "string"},
                "context": {"type": "string"},
                "artifact_type": {"type": "string",
                    "enum": ["code","prose","math","email","table","diagram","plan","pseudo","query","other"]},
                "requirements": {"type": "array", "items": {"type": "string"}},
                "success_criteria": {"type": "string"},
                "target_error_patterns": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["title","question_text","context","artifact_type","requirements","success_criteria"],
        },
    }

def judge_decision_tool(include_evidence=True, include_confidence=True) -> dict[str, Any]:
    props = {
        "differentiation_achieved": {"type": "boolean"},
        "quality_score": {"type": "number"},
        "failures_weaker": {"type": "array", "items": {"type": "string"}},  # from catalog names
        "reasoning": {"type": "string"},
    }
    if include_evidence:
        props["evidence_spans"] = {"type": "array", "items": {"type": "string"}}
    if include_confidence:
        props["confidence"] = {"type": "number"}
    props["unmapped_findings"] = {"type": "array", "items": {"type": "string"}}
    return {
        "name": "judge_decision_tool",
        "description": "Returns differentiation decision and mapped weak-model failures",
        "input_schema": {"type": "object", "properties": props,
                         "required": ["differentiation_achieved","failures_weaker","reasoning"]},
    }

def student_assessment_tool() -> dict[str, Any]:
    return {
        "name": "student_assessment_tool",
        "description": "Returns assessment JSON for any modality",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "difficulty": {"type": "string", "enum": ["Beginner","Intermediate","Advanced"]},
                "content_type": {"type": "string",
                    "enum": ["code","prose","math","email","table","diagram","plan","pseudo","query","other"]},
                "content": {"type": "array", "items": {"type": "string"}},
                "errors": {
                    "type": "array",
                    "items": {"type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "description": {"type": "string"},
                        },
                        "required": ["id","description"]}
                },
            },
            "required": ["title","difficulty","content","errors"],
        },
    }
