

def p_step1_difficulty(topic: str) -> str:
    return (
        f'For the topic "{topic}", return EXACTLY 3 difficulty levels with 3–5 subtopics each.\n'
        'Use the exact keys: "Beginner", "Intermediate", "Advanced".\n'
        "- Subtopics are specific tasks (≥ 2 words). Avoid 'overview', 'introduction', 'basics', 'general', 'misc'.\n"
        "Return ONLY via difficulty_categories_tool."
    )

def p_step2_error_catalog(topic: str, subtopic: str, difficulty: str, keep_likelihood: bool=True) -> str:
    extra = " Include likelihood_strong_avoids (0–1) and likelihood_weak_makes (0–1)."
    return (
        f'For "{topic}" at {difficulty}, subtopic "{subtopic}", return EXACTLY 6 subtle, independently testable mistakes.\n'
        "Fields EXACTLY: mistake, why_wrong, match_hint (short text/regex-like cue), impact (Minor|Moderate|Major), "
        "domain_specific=true." + (extra if keep_likelihood else "") + "\n"
        "Ensure mistakes are distinct. Return ONLY via error_catalog_tool."
    )

def p_step3_strategic(topic: str, subtopic: str, difficulty: str,
                      target_names: list[str], previous_failures: list[str]) -> str:
    prev = ("\nVALIDATION FEEDBACK (fix all):\n" + "\n".join(f"- {x}" for x in previous_failures)) if previous_failures else ""
    return (
        f"Create a strategic challenge for '{subtopic}' ({difficulty}) in {topic}.\n"
        "Choose artifact_type from: code, prose, math, email, table, diagram, plan, pseudo, query, other.\n"
        "Do NOT pre-embed mistakes; requirements should naturally invite subtle pitfalls.\n"
        "Include EXACTLY: title, question_text, context, artifact_type, 4–6 requirements, success_criteria, "
        "target_error_patterns (names only, subset of the provided catalog).\n"
        "Return ONLY via strategic_question_tool." + prev
    )

def p_step4_or_5_producer(question: dict) -> str:
    artifact = question.get("artifact_type", "artifact")
    reqs = "\n".join(f"- {r}" for r in question.get("requirements", []))
    return (
        f"You are an expert in {question.get('context','the domain')}. Produce the requested {artifact}.\n\n"
        f"TASK: {question.get('title','Challenge')}\n"
        f"DESCRIPTION: {question.get('question_text','')}\n"
        f"CONTEXT: {question.get('context','')}\n\n"
        f"REQUIREMENTS (address each explicitly):\n{reqs}\n\n"
        f"SUCCESS CRITERIA: {question.get('success_criteria','Meets requirements with sound reasoning and robustness')}\n\n"
        "Provide exactly three sections with markdown headers:\n\n"
        "### OUTPUT\n<the artifact itself>\n\n"
        "### RATIONALE\n2–4 sentences explaining key decisions.\n\n"
        "### CONSIDERATIONS\n2–4 bullets on risks, assumptions, or limitations.\n"
    )

def p_step6_judge(question: dict, catalog_names: list[str],
                  impl_mid_text: str, impl_weak_text: str) -> str:
    known = "\n".join(f"- {n}" for n in catalog_names)
    return (
        "Evaluate Implementation A (mid-tier) vs Implementation B (weak-tier) against the original task and the error catalog.\n\n"
        f"ORIGINAL TASK: {question.get('question_text','')}\nContext: {question.get('context','')}\n"
        f"Requirements: {', '.join(question.get('requirements', []))}\n\n"
        "KNOWN ERROR PATTERNS (names only):\n" + known + "\n\n"
        "IMPLEMENTATION A (mid-tier):\n" + impl_mid_text + "\n\n"
        "IMPLEMENTATION B (weak-tier):\n" + impl_weak_text + "\n\n"
        "Return ONLY via judge_decision_tool with: differentiation_achieved (bool), quality_score (1–10), "
        "failures_weaker (strings taken ONLY from the known error pattern names), reasoning (2–3 sentences). "
        "Optionally include evidence_spans (short quotes) and confidence (0–1). "
        "You may include unmapped_findings for telemetry; they will not affect Step 7."
    )

def p_step7_assessment(topic: str, subtopic: str, weak_text: str, mid_text: str,
                       failures_weaker: list[str], target_error_patterns: list[str]) -> str:
    fw = "\n".join(f"- {f}" for f in failures_weaker)
    targets = "\n".join(f"- {t}" for t in target_error_patterns) if target_error_patterns else "(none)"
    return (
        "Create a single interactive error-spotting assessment from the weak model's output.\n"
        "Select 2–5 mistakes FROM failures_weaker ONLY; choose a single-line span for each mistake.\n"
        "Modality may be code, prose/essay, math proof, email, financial model/table, diagram, plan, pseudo, query, or other.\n"
        "Provide a self-contained snippet (24–60 lines). Mark errors with <<error_substring>> (10–120 chars each).\n"
        "Return ONLY via student_assessment_tool with: title, difficulty, content_type, content (array of lines), errors[] (id, description).\n\n"
        f"Topic: {topic}\nSubtopic: {subtopic}\n\n"
        "WEAK MODEL OUTPUT (source):\n" + weak_text[:2000] + "\n\n"
        "MID-TIER REFERENCE (do not copy; guidance only):\n" + mid_text[:1000] + "\n\n"
        "failures_weaker:\n" + fw + "\n\n"
        "target_error_patterns:\n" + targets + "\n"
    )
