from typing import List, Dict, Any, Optional

def build_step1_prompt(topic: str, template: str) -> str:
    """Builds the prompt for Step 1: Generate difficulty categories."""
    return template.format(topic=topic)

def build_step2_prompt(topic: str, subtopic: str, difficulty: str, template: str) -> str:
    """Builds the prompt for Step 2: Generate conceptual error catalog."""
    return template.format(topic=topic, difficulty=difficulty, subtopic=subtopic)

def build_step3_prompt(
    topic: str,
    subtopic: str,
    difficulty: str,
    error_catalog: List[Dict],
    template: str,
    previous_failures: List[str] = None
) -> str:
    """Builds the prompt for Step 3: Generate strategic implementation challenge."""
    failure_feedback = ""
    if previous_failures:
        failure_feedback = (
            "\nVALIDATION FEEDBACK (resolve before returning a new challenge):\n"
            + "\n".join(f"- {failure}" for failure in previous_failures)
        )

    catalog_names: List[str] = [
        f"- {error.get('mistake', '').strip()}"
        for error in error_catalog or []
        if isinstance(error.get('mistake'), str) and error.get('mistake').strip()
    ]

    return template.format(
        topic=topic,
        subtopic=subtopic,
        difficulty=difficulty,
        catalog_names="\n".join(catalog_names) if catalog_names else "- (no catalog names available)",
        failure_feedback=failure_feedback
    )

def build_step45_prompt(question: Dict, template: str) -> str:
    """Builds the prompt for Steps 4 & 5: Implementation responses."""
    requirements = question.get('requirements', []) or []
    return template.format(
        context=question.get('context', 'the domain'),
        artifact=question.get('artifact_type', 'artifact'),
        title=question.get('title', 'Implementation Challenge'),
        question_text=question.get('question_text', ''),
        requirements="\n".join(f"- {req}" for req in requirements) if requirements else "- (no requirements provided)",
        success_criteria=question.get('success_criteria', 'Meets requirements with sound reasoning and robustness')
    )

def build_step6_prompt(
    question: Dict,
    sonnet_response: str,
    haiku_response: str,
    error_catalog: List[Dict],
    template: str
) -> str:
    """Builds the prompt for Step 6: Judge implementation differentiation."""
    error_patterns_text = ""
    for i, error in enumerate(error_catalog or [], 1):
        error_patterns_text += (
            f"\n{i}. {error.get('mistake', 'Unknown error')}\n"
            f"   Why problematic: {error.get('why_wrong', 'Issues not specified')}\n"
            f"   Code pattern: {error.get('code_pattern', error.get('match_hint', 'Not specified'))}"
        )

    return template.format(
        question_text=question.get('question_text', ''),
        context=question.get('context', ''),
        requirements=", ".join(question.get('requirements', [])),
        error_patterns_text=error_patterns_text,
        sonnet_response=sonnet_response,
        haiku_response=haiku_response
    )

def build_step7_prompt(
    topic: str,
    subtopic: str,
    haiku_failures: List[str],
    haiku_response: str,
    sonnet_response: str,
    template: str,
    config: Dict[str, Any],
    validation_feedback: Optional[List[str]] = None
) -> str:
    """Builds the prompt for Step 7: Create student assessment."""
    validation_block = ""
    if validation_feedback:
        feedback_lines = "\n".join(f"- {issue}" for issue in validation_feedback)
        validation_block = (
            "\n\nVALIDATION FEEDBACK FROM THE LAST ATTEMPT:\n"
            "Fix every issue below before returning the next result:\n"
            f"{feedback_lines}\n"
        )

    return template.format(
        haiku_failures="\n".join(f"- {failure}" for failure in haiku_failures),
        haiku_response_preview=haiku_response[:2000],
        sonnet_response_preview=sonnet_response[:1000],
        min_code_lines=config.get('min_code_lines', 24),
        max_code_lines=config.get('max_code_lines', 60),
        min_error_span=config.get('min_error_span', 20),
        max_error_span=config.get('max_error_span', 120),
        min_errors=config.get('min_errors', 1),
        max_errors=config.get('max_errors', 5),
        allowed_difficulties=", ".join(sorted(config.get('allowed_difficulties', []))),
        topic=topic,
        subtopic=subtopic,
        validation_feedback=validation_block
    )