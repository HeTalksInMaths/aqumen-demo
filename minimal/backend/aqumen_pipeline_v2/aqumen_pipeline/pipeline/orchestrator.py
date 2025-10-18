import json
import os
from datetime import datetime
from typing import Any

from ..analytics.rewards import (
    rewards_step1,
    rewards_step2,
    rewards_step3,
    rewards_step6,
    rewards_step7,
    rewards_step45,
)
from ..clients.bedrock import BedrockRuntime
from ..config import BACKEND_DIR, LOG_DIR_ARCHIVED, LOG_DIR_CURRENT, RESULTS_DIR, SQLITE_DB_PATH, STEP7_MAX_ATTEMPTS
from ..datatypes import PipelineStep
from ..persistence.repo import Repo
from ..prompts import builders as P
from ..roles import load_model_roles
from ..services.invoke import Invoker
from ..tools.schemas import (
    difficulty_categories_tool,
    error_catalog_tool,
    judge_decision_tool,
    strategic_question_tool,
    student_assessment_tool,
)
from ..validators.assessment import validate_assessment_payload


def ensure_dirs(dirs: list[str]):
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def log_step_to_file(path: str, step: PipelineStep):
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n" + "="*80 + "\n")
        f.write(f"STEP {step.step_number}: {step.step_name}\n")
        f.write(f"MODEL: {step.model_used}\n")
        f.write(f"TIMESTAMP: {step.timestamp}\n")
        f.write(f"SUCCESS: {step.success}\n")
        f.write(f"RESPONSE:\n{step.response}\n")

class Orchestrator:
    def __init__(self):
        self.roles = load_model_roles()
        self.inv = Invoker(BedrockRuntime())
        self.repo = Repo(SQLITE_DB_PATH)
        self.run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        ensure_dirs([LOG_DIR_CURRENT, LOG_DIR_ARCHIVED, RESULTS_DIR, BACKEND_DIR])
        self.log_file = f"{LOG_DIR_CURRENT}/pipeline_run_{self.run_ts}.txt"
        self.topic = "Unknown"

    def _log_rewards(self, step: int, report):
        details = [{"name": r.name, "passed": r.passed, "detail": r.detail} for r in report.results]
        self.repo.save_rewards(self.run_ts, step, report.pass_rate, details)
        metrics_path = f"{RESULTS_DIR}/metrics_{self.run_ts}.json"
        if os.path.exists(metrics_path):
            with open(metrics_path, encoding="utf-8") as f:
                existing = json.load(f)
        else:
            existing = {"run_ts": self.run_ts, "steps": {}}
        existing["steps"][str(step)] = {"pass_rate": report.pass_rate, "results": details}
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)

    def _save_step(self, step: PipelineStep):
        log_step_to_file(self.log_file, step)
        self.repo.save_step(self.run_ts, self.topic, step.step_number, step.step_name,
                            step.model_used, step.success, step.response, step.timestamp)

    # Step 1
    def step1(self, topic: str) -> tuple[bool, dict[str, list[str]], PipelineStep]:
        self.topic = topic
        self.repo.mark_run_start(self.run_ts, topic)
        prompt = P.p_step1_difficulty(topic)
        tool = difficulty_categories_tool()
        resp = self.inv.tools(self.roles["judge"].id, prompt, [tool])
        ok = isinstance(resp, dict) and set(resp.keys()) == {"Beginner","Intermediate","Advanced"}
        step = PipelineStep(1, "Generate difficulty categories", self.roles["judge"].id, ok, json.dumps(resp), datetime.now().isoformat())
        self._save_step(step)
        report = rewards_step1(resp if isinstance(resp, dict) else {})
        self._log_rewards(1, report)
        return ok, (resp if isinstance(resp, dict) else {}), step

    # Step 2
    def step2(self, topic: str, subtopic: str, difficulty: str):
        prompt = P.p_step2_error_catalog(topic, subtopic, difficulty, keep_likelihood=True)
        tool = error_catalog_tool(keep_likelihood=True)
        resp = self.inv.tools(self.roles["judge"].id, prompt, [tool])
        if isinstance(resp, dict) and "errors" in resp:
            for e in resp["errors"]:
                if "match_hint" not in e and "code_pattern" in e:
                    e["match_hint"] = e["code_pattern"]
        ok = isinstance(resp, dict) and "errors" in resp
        step = PipelineStep(2, "Generate error catalog", self.roles["judge"].id, ok, json.dumps(resp), datetime.now().isoformat())
        self._save_step(step)
        report = rewards_step2(resp if isinstance(resp, dict) else {"errors":[]})
        self._log_rewards(2, report)
        return ok, (resp if isinstance(resp, dict) else {}), step

    # Step 3
    def step3(self, topic: str, subtopic: str, difficulty: str, catalog: dict[str, Any], previous_failures: list[str]):
        names = [e.get("mistake","") for e in catalog.get("errors", [])]
        prompt = P.p_step3_strategic(topic, subtopic, difficulty, names, previous_failures)
        tool = strategic_question_tool()
        resp = self.inv.tools(self.roles["judge"].id, prompt, [tool], use_thinking=bool(previous_failures))
        ok = isinstance(resp, dict) and resp.get("artifact_type") in {"code","prose","math","email","table","diagram","plan","pseudo","query","other"} and 4 <= len(resp.get("requirements", [])) <= 6
        step = PipelineStep(3, "Generate strategic challenge", self.roles["judge"].id, ok, json.dumps(resp), datetime.now().isoformat())
        self._save_step(step)
        report = rewards_step3(resp if isinstance(resp, dict) else {}, names)
        self._log_rewards(3, report)
        return ok, (resp if isinstance(resp, dict) else {}), step

    # Step 4
    def step4(self, question: dict[str, Any]):
        prompt = P.p_step4_or_5_producer(question)
        text = self.inv.text(self.roles["mid"].id, prompt)
        step = PipelineStep(4, "Produce mid-tier implementation", self.roles["mid"].id, True, text, datetime.now().isoformat())
        self._save_step(step)
        report = rewards_step45(text, question.get("requirements", []))
        self._log_rewards(4, report)
        return True, text, step

    # Step 5
    def step5(self, question: dict[str, Any]):
        prompt = P.p_step4_or_5_producer(question)
        text = self.inv.text(self.roles["weak"].id, prompt)
        step = PipelineStep(5, "Produce weak-tier implementation", self.roles["weak"].id, True, text, datetime.now().isoformat())
        self._save_step(step)
        report = rewards_step45(text, question.get("requirements", []))
        self._log_rewards(5, report)
        return True, text, step

    # Step 6
    def step6(self, question: dict[str, Any], catalog: dict[str, Any], mid_text: str, weak_text: str):
        def rank_key(e):
            impact_rank = {"Minor":0,"Moderate":1,"Major":2}.get(e.get("impact"),0)
            return (impact_rank, float(e.get("likelihood_weak_makes",0.0)))
        topk = sorted(catalog.get("errors", []), key=rank_key, reverse=True)[:5]
        cat_names = [e.get("mistake","") for e in topk]

        prompt = P.p_step6_judge(question, cat_names, mid_text, weak_text)
        tool = judge_decision_tool(include_evidence=True, include_confidence=True)
        resp = self.inv.tools(self.roles["judge"].id, prompt, [tool])
        ok = isinstance(resp, dict) and "differentiation_achieved" in resp and "failures_weaker" in resp
        step = PipelineStep(6, "Judge differentiation", self.roles["judge"].id, ok, json.dumps(resp), datetime.now().isoformat())
        self._save_step(step)
        full_names = [e.get("mistake","") for e in catalog.get("errors", [])]
        report = rewards_step6(resp if isinstance(resp, dict) else {}, full_names, weak_text)
        self._log_rewards(6, report)
        return ok, (resp if isinstance(resp, dict) else {}), step

    # Step 7
    def step7(self, topic: str, subtopic: str, question: dict[str, Any],
              mid_text: str, weak_text: str, judge_obj: dict[str, Any]):
        failures_weaker = judge_obj.get("failures_weaker", [])
        target_names = question.get("target_error_patterns", [])
        last_step = None

        tool = student_assessment_tool()

        for attempt in range(1, STEP7_MAX_ATTEMPTS + 1):
            prompt = P.p_step7_assessment(topic, subtopic, weak_text, mid_text, failures_weaker, target_names)
            resp = self.inv.tools(self.roles["judge"].id, prompt, [tool])
            ok, sanitized, issues = validate_assessment_payload(resp if isinstance(resp, dict) else {})
            payload = sanitized if ok else {"model_response": resp, "validation_errors": issues}
            step = PipelineStep(7, f"Create assessment (attempt {attempt})", self.roles["judge"].id, ok, json.dumps(payload), datetime.now().isoformat())
            self._save_step(step)
            report = rewards_step7(resp if isinstance(resp, dict) else {})
            self._log_rewards(7, report)
            last_step = step
            if ok:
                return True, sanitized, step
        return False, json.loads(last_step.response), last_step

    def mark_end(self, steps_completed: list[PipelineStep], differentiation: bool, final_success: bool):
        self.repo.mark_run_end(self.run_ts, total_steps=len(steps_completed),
                               differentiation_achieved=differentiation, final_success=final_success)
