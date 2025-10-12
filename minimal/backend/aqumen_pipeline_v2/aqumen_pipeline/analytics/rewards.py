import re
from dataclasses import dataclass
from typing import Any, Dict, List
from ..validators.assessment import validate_assessment_payload

@dataclass
class RewardResult:
    name: str
    passed: bool
    detail: str = ""

@dataclass
class StepRewardsReport:
    step: int
    results: List[RewardResult]
    @property
    def pass_rate(self) -> float:
        return (sum(1 for r in self.results if r.passed) / max(1, len(self.results)))

def rewards_step1(categories: Dict[str, List[str]]) -> StepRewardsReport:
    res = []
    res.append(RewardResult("keys_exact", set(categories.keys()) == {"Beginner","Intermediate","Advanced"}))
    res.append(RewardResult("count_range", all(3 <= len(categories[k]) <= 5 for k in categories)))
    lowered = {k: {s.strip().lower() for s in categories.get(k, [])} for k in categories}
    union = set.union(*map(set, lowered.values())) if lowered else set()
    res.append(RewardResult("no_overlaps", len(union) == sum(len(v) for v in lowered.values())))
    BAD = {"overview","introduction","basics","general","misc"}
    concrete = all(len(s.split()) >= 2 and all(w not in s.lower() for w in BAD) for k in categories for s in categories.get(k, []))
    res.append(RewardResult("subtopics_concrete", concrete))
    return StepRewardsReport(step=1, results=res)

def rewards_step2(catalog: Dict[str, Any]) -> StepRewardsReport:
    errs = catalog.get("errors", [])
    res = []
    res.append(RewardResult("count_exact_6", len(errs) == 6, f"found={len(errs)}"))
    req = {"mistake","why_wrong","match_hint","impact","domain_specific","likelihood_strong_avoids","likelihood_weak_makes"}
    res.append(RewardResult("schema_fields", all(req <= set(e.keys()) for e in errs)))
    res.append(RewardResult("likelihood_ranges", all(0 <= e.get("likelihood_strong_avoids",0) <= 1 and 0 <= e.get("likelihood_weak_makes",0) <= 1 for e in errs)))
    res.append(RewardResult("impact_normalized", all(e.get("impact") in {"Minor","Moderate","Major"} for e in errs)))
    names = [e.get("mistake"," ").strip().lower() for e in errs]
    res.append(RewardResult("distinct_mistakes", len(set(names)) == len(names)))
    GENERIC = {"bad","wrong","error","issue"}
    res.append(RewardResult("match_hint_present", all(len(e.get("match_hint"," ").strip()) >= 6 and e.get("match_hint"," ").strip().lower() not in GENERIC for e in errs)))
    return StepRewardsReport(step=2, results=res)

def rewards_step3(question: Dict[str, Any], known_mistake_names: List[str]) -> StepRewardsReport:
    res = []
    reqd = {"title","question_text","context","artifact_type","requirements","success_criteria"}
    res.append(RewardResult("fields_present", reqd <= set(question.keys())))
    L = len(question.get("requirements", []))
    res.append(RewardResult("requirements_count_4_6", 4 <= L <= 6, f"found={L}"))
    VALID = {"code","prose","math","email","table","diagram","plan","pseudo","query","other"}
    res.append(RewardResult("artifact_type_valid", question.get("artifact_type") in VALID))
    q = (question.get("title","") + " " + question.get("question_text"," ")).lower()
    res.append(RewardResult("no_preembedded_mistakes", all(b not in q for b in ("<<","bug","fix the","incorrect"))))
    res.append(RewardResult("targets_subset_catalog", set(question.get("target_error_patterns", [])) <= set(known_mistake_names)))
    return StepRewardsReport(step=3, results=res)

def rewards_step45(output_text: str, requirements: List[str]) -> StepRewardsReport:
    res = []
    res.append(RewardResult("sections_present", all(h in output_text for h in ("### OUTPUT","### RATIONALE","### CONSIDERATIONS"))))
    lines = [line for line in output_text.splitlines() if line.strip()]
    res.append(RewardResult("length_24_120", 24 <= len(lines) <= 120, f"lines={len(lines)}"))
    hits = sum(any(tok.lower() in output_text.lower() for tok in r.split()) for r in requirements)
    coverage_ratio = hits / max(1, len(requirements))
    res.append(RewardResult("coverage_soft>=0.5", coverage_ratio >= 0.5, f"coverage={coverage_ratio:.2f}"))
    return StepRewardsReport(step=45, results=res)

def rewards_step6(judge_obj: Dict[str, Any], known_mistake_names: List[str], weak_text: str) -> StepRewardsReport:
    res = []
    req = {"differentiation_achieved","failures_weaker","reasoning"}
    res.append(RewardResult("schema_core", req <= set(judge_obj.keys())))
    if judge_obj.get("differentiation_achieved") is True:
        fw = judge_obj.get("failures_weaker", [])
        res.append(RewardResult("failures_present", bool(fw)))
        res.append(RewardResult("failures_subset_catalog", set(map(str.lower, fw)) <= set(map(str.lower, known_mistake_names))))
    ev = judge_obj.get("evidence_spans", [])
    res.append(RewardResult("evidence_in_weak_text", all((isinstance(e, str) and (e.lower() in weak_text.lower())) for e in ev) if ev else True))
    return StepRewardsReport(step=6, results=res)

def rewards_step7(assessment_obj: Dict[str, Any]) -> StepRewardsReport:
    res = []
    ok, _, issues = validate_assessment_payload(assessment_obj)
    res.append(RewardResult("validator_ok", ok, "; ".join(issues[:3])))
    lines = assessment_obj.get("content", [])
    joined = "\n".join(lines) if isinstance(lines, list) else str(lines)
    spans = re.findall(r"<<([^<>]+)>>", joined)
    res.append(RewardResult("spans_match_errors_len", len(spans) == len(assessment_obj.get("errors", [])), f"spans={len(spans)} errors={len(assessment_obj.get('errors', []))}"))
    res.append(RewardResult("no_crossline_spans", all(line.count("<<")==line.count(">>") for line in (lines or []))))
    res.append(RewardResult("span_lengths_10_120", all(10 <= len(s) <= 120 for s in spans)))
    return StepRewardsReport(step=7, results=res)
