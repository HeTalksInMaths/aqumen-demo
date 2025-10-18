import re
from dataclasses import dataclass
from typing import Any


@dataclass
class RewardResult:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class StepRewardsReport:
    step: int
    results: list[RewardResult]

    @property
    def pass_rate(self) -> float:
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.passed) / len(self.results)


def rewards_step1(categories: dict[str, list[str]]) -> StepRewardsReport:
    categories = categories or {}
    required_keys = {"Beginner", "Intermediate", "Advanced"}
    results: list[RewardResult] = []

    key_set = set(categories.keys())
    results.append(RewardResult("keys_exact", key_set == required_keys, f"found={sorted(key_set)}"))

    count_checks = []
    for key in required_keys:
        items = categories.get(key, [])
        count_checks.append(3 <= len(items) <= 5)
    results.append(RewardResult("count_range", all(count_checks), f"counts={[len(categories.get(k, [])) for k in sorted(required_keys)]}"))

    lowered = {k: {s.strip().lower() for s in categories.get(k, []) if isinstance(s, str)} for k in categories}
    union = set().union(*lowered.values()) if lowered else set()
    total_items = sum(len(v) for v in lowered.values())
    results.append(RewardResult("no_overlaps", len(union) == total_items, f"unique={len(union)} total={total_items}"))

    banned_terms = {"overview", "introduction", "basics", "general", "misc"}
    concrete = True
    for items in lowered.values():
        for item in items:
            if len(item.split()) < 2 or any(term in item for term in banned_terms):
                concrete = False
                break
        if not concrete:
            break
    results.append(RewardResult("subtopics_concrete", concrete))

    return StepRewardsReport(step=1, results=results)


def rewards_step2(error_catalog: list[dict[str, Any]]) -> StepRewardsReport:
    errors = error_catalog or []
    results: list[RewardResult] = []

    results.append(RewardResult("count_exact_6", len(errors) == 6, f"found={len(errors)}"))

    required_fields = {"mistake", "why_wrong", "match_hint", "impact", "domain_specific", "likelihood_strong_avoids", "likelihood_weak_makes"}
    field_check = all(required_fields <= set(entry.keys()) for entry in errors if isinstance(entry, dict))
    results.append(RewardResult("schema_fields", field_check))

    likelihood_ok = all(
        0 <= (entry.get("likelihood_strong_avoids") or 0) <= 1 and
        0 <= (entry.get("likelihood_weak_makes") or 0) <= 1
        for entry in errors if isinstance(entry, dict)
    )
    results.append(RewardResult("likelihood_ranges", likelihood_ok))

    impacts_ok = all(entry.get("impact") in {"Minor", "Moderate", "Major"} for entry in errors if isinstance(entry, dict))
    results.append(RewardResult("impact_normalized", impacts_ok))

    mistake_names = [str(entry.get("mistake", "")).strip().lower() for entry in errors if isinstance(entry, dict)]
    results.append(RewardResult("distinct_mistakes", len(set(mistake_names)) == len(mistake_names)))

    generic = {"bad", "wrong", "error", "issue"}
    hint_quality = all(
        isinstance(entry.get("match_hint"), str) and len(entry["match_hint"].strip()) >= 6 and
        entry["match_hint"].strip().lower() not in generic
        for entry in errors if isinstance(entry, dict)
    )
    results.append(RewardResult("match_hint_present", hint_quality))

    return StepRewardsReport(step=2, results=results)


def rewards_step3(question: dict[str, Any]) -> StepRewardsReport:
    question = question or {}
    results: list[RewardResult] = []
    required_fields = {"title", "question_text", "context", "artifact_type", "requirements", "success_criteria"}
    results.append(RewardResult("fields_present", required_fields <= set(question.keys())))

    requirements = question.get("requirements") or []
    if not isinstance(requirements, list):
        requirements = []
    results.append(RewardResult("requirements_count_4_6", 4 <= len(requirements) <= 6, f"found={len(requirements)}"))

    valid_artifacts = {"code", "prose", "math", "email", "table", "diagram", "plan", "pseudo", "query", "other"}
    artifact_ok = question.get("artifact_type") in valid_artifacts
    results.append(RewardResult("artifact_type_valid", artifact_ok, f"found={question.get('artifact_type')}"))

    combined_text = f"{question.get('title', '')} {question.get('question_text', '')}".lower()
    preembedded = any(term in combined_text for term in ("<<", "fix the", "bug"))
    results.append(RewardResult("no_preembedded_mistakes", not preembedded))

    success_criteria_ok = bool(str(question.get("success_criteria", "")).strip())
    results.append(RewardResult("success_criteria_present", success_criteria_ok))

    return StepRewardsReport(step=3, results=results)


def rewards_step45(output_text: str, requirements: list[str]) -> StepRewardsReport:
    output_text = output_text or ""
    requirements = requirements or []

    results: list[RewardResult] = []
    sections_present = all(section in output_text for section in ("### OUTPUT", "### RATIONALE", "### CONSIDERATIONS"))
    results.append(RewardResult("sections_present", sections_present))

    lines = [line for line in output_text.splitlines() if line.strip()]
    results.append(RewardResult("length_24_120", 24 <= len(lines) <= 120, f"lines={len(lines)}"))

    hits = 0
    for req in requirements:
        tokens = str(req).split()
        if any(tok.lower() in output_text.lower() for tok in tokens):
            hits += 1
    coverage_ratio = hits / max(1, len(requirements))
    results.append(RewardResult("coverage_soft>=0.5", coverage_ratio >= 0.5, f"coverage={coverage_ratio:.2f}"))

    return StepRewardsReport(step=45, results=results)


def rewards_step6(judge_obj: dict[str, Any], known_mistake_names: list[str], weak_text: str) -> StepRewardsReport:
    judge_obj = judge_obj or {}
    known_mistake_names = known_mistake_names or []
    weak_text = weak_text or ""

    results: list[RewardResult] = []
    required_core = {"differentiation_achieved", "failures_weaker", "reasoning"}
    results.append(RewardResult("schema_core", required_core <= set(judge_obj.keys())))

    if judge_obj.get("differentiation_achieved") is True:
        failures = judge_obj.get("failures_weaker") or []
        results.append(RewardResult("failures_present", bool(failures)))
        known_lower = {name.lower() for name in known_mistake_names}
        failures_lower = {str(name).strip().lower() for name in failures}
        results.append(RewardResult("failures_subset_catalog", failures_lower <= known_lower))
    else:
        results.append(RewardResult("failures_present", True))
        results.append(RewardResult("failures_subset_catalog", True))

    evidence_spans = judge_obj.get("evidence_spans") or []
    if isinstance(evidence_spans, list) and evidence_spans:
        evidence_ok = all(isinstance(span, str) and span.strip().lower() in weak_text.lower() for span in evidence_spans)
        results.append(RewardResult("evidence_in_weak_text", evidence_ok))
    else:
        results.append(RewardResult("evidence_in_weak_text", True))

    return StepRewardsReport(step=6, results=results)


def rewards_step7(assessment_obj: dict[str, Any]) -> StepRewardsReport:
    assessment_obj = assessment_obj or {}
    results: list[RewardResult] = []

    lines = assessment_obj.get("content")
    if not isinstance(lines, list):
        lines = assessment_obj.get("code")
    if not isinstance(lines, list):
        lines = []
    lines = [str(line).rstrip("\r\n") for line in lines]
    results.append(RewardResult("line_count_24_60", 24 <= len(lines) <= 60, f"lines={len(lines)}"))

    errors = assessment_obj.get("errors")
    if not isinstance(errors, list):
        errors = []
    results.append(RewardResult("error_count_1_5", 1 <= len(errors) <= 5, f"errors={len(errors)}"))

    joined = "\n".join(lines)
    spans = re.findall(r"<<([^<>]+)>>", joined)
    results.append(RewardResult("spans_match_errors_len", len(spans) == len(errors), f"spans={len(spans)} errors={len(errors)}"))

    span_lengths_ok = all(10 <= len(span) <= 120 for span in spans)
    results.append(RewardResult("span_lengths_10_120", span_lengths_ok))

    ids = [str((err or {}).get("id", "")).strip() for err in errors if isinstance(err, dict)]
    results.append(RewardResult("ids_unique", len(set(ids)) == len(ids)))

    return StepRewardsReport(step=7, results=results)
