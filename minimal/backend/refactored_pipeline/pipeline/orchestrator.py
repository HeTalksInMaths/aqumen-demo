import json
import os
import random
from copy import deepcopy
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging
import sqlite3

from refactored_pipeline.datatypes import PipelineStep, SevenStepResult
from refactored_pipeline.prompts import builders
from refactored_pipeline.validators.assessment import AssessmentValidator
from config import load_prompts, load_tools
from roles import load_model_roles
import os
from clients.bedrock import BedrockRuntime
from clients.mock_bedrock import MockBedrockRuntime
from services.invoke import Invoker
from persistence.repo import Repo
from analytics.rewards import (
    StepRewardsReport,
    rewards_step1,
    rewards_step2,
    rewards_step3,
    rewards_step45,
    rewards_step6,
    rewards_step7,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self, db_path: str = "pipeline_results.db"):
        self.roles = load_model_roles()
        self.aws_region = "us-west-2"

        self.model_strong = self.roles["judge"].id
        self.model_mid = self.roles["mid"].id
        self.model_weak = self.roles["weak"].id
        self.judge_supports_thinking = self.roles["judge"].supports_thinking

        if os.getenv("AQU_MOCK_PIPELINE") == "1":
            self.bedrock_runtime = MockBedrockRuntime(region=self.aws_region)
        else:
            self.bedrock_runtime = BedrockRuntime(region=self.aws_region)
        self.invoker = Invoker(self.bedrock_runtime)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.script_dir = script_dir

        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        base_dir = os.path.abspath(os.path.join(self.script_dir, "..", ".."))
        log_dir = os.path.join(base_dir, "logs", "current")
        results_dir = os.path.join(base_dir, "results")
        self.log_file = os.path.join(log_dir, f"pipeline_run_{self.run_timestamp}.txt")
        self.results_file = os.path.join(results_dir, f"corrected_7step_results_{self.run_timestamp}.json")
        
        os.makedirs(log_dir, exist_ok=True)
        os.makedirs(os.path.join(base_dir, "logs", "archived"), exist_ok=True)
        os.makedirs(results_dir, exist_ok=True)
        
        self.db_path = os.path.join(base_dir, db_path)
        self._init_database()
        self.repo = Repo(self.db_path)

        self.config = {
            "allowed_difficulties": {"Beginner", "Intermediate", "Advanced", "Expert"},
            "step7_max_attempts": 3,
            "min_code_lines": 24,
            "max_code_lines": 60,
            "min_errors": 1,
            "max_errors": 5,
            "min_error_span": 20,
            "max_error_span": 120,
        }
        self.assessment_validator = AssessmentValidator(self.config)

        try:
            self.prompts = load_prompts()
            self.tools = load_tools()
        except Exception as exc:
            logger.error(f"Failed to load prompt/tool configuration: {exc}")
            raise

    def invoke_model(self, model_id: str, prompt: str, max_tokens: int = 2048) -> str:
        return self.invoker.text(model_id, prompt, max_tokens=max_tokens)

    def invoke_model_with_tools(
        self,
        model_id: str,
        prompt: str,
        tools: List[Dict[str, Any]],
        max_tokens: int = 2048,
        use_thinking: bool = False,
        thinking_budget: int = 2048,
    ) -> Dict[str, Any]:
        safe_use_thinking = use_thinking and self.judge_supports_thinking
        return self.invoker.tools(
            model_id,
            prompt,
            tools,
            max_tokens=max_tokens,
            use_thinking=safe_use_thinking,
            thinking_budget=thinking_budget,
        )

    def log_step(self, step: PipelineStep):
        with open(self.log_file, "a") as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"STEP {step.step_number}: {step.step_name}\n")
            f.write(f"MODEL: {step.model_used}\n")
            f.write(f"TIMESTAMP: {step.timestamp}\n")
            f.write(f"SUCCESS: {step.success}\n")
            f.write(f"RESPONSE:\n{step.response}\n")
        
        self.repo.save_step(
            self.run_timestamp,
            getattr(self, "current_topic", "Unknown"),
            step.step_number,
            step.step_name,
            step.model_used,
            step.success,
            step.response,
            step.timestamp
        )

    def _get_prompt_template(self, step_key: str) -> str:
        entry = self.prompts.get(step_key)
        if isinstance(entry, dict):
            template = entry.get("template")
        else:
            template = entry

        if not isinstance(template, str):
            raise KeyError(f"Prompt template missing for step '{step_key}'")

        return template

    def _get_tools(self, step_key: str) -> List[Dict[str, Any]]:
        tool_entry = self.tools.get(step_key)

        if tool_entry is None:
            raise KeyError(f"Tool configuration missing for step '{step_key}'")

        if isinstance(tool_entry, list):
            return deepcopy(tool_entry)

        return [deepcopy(tool_entry)]

    def step1_generate_difficulty_categories(self, topic: str) -> Tuple[bool, Dict[str, List[str]], PipelineStep]:
        template = self._get_prompt_template("step1_difficulty_categories")
        prompt = builders.build_step1_prompt(topic, template)
        tools = self._get_tools("step1_difficulty_categories")

        response = self.invoke_model_with_tools(self.model_strong, prompt, tools)
        step = PipelineStep(1, "Generate difficulty categories", self.model_strong, False, str(response), datetime.now().isoformat())

        categories: Dict[str, List[str]] = {}
        try:
            if isinstance(response, dict) and 'error' not in response:
                candidate = response
                required_keys = {"Beginner", "Intermediate", "Advanced"}
                key_set = set(candidate.keys())
                counts_valid = all(
                    isinstance(candidate.get(key), list) and 3 <= len(candidate.get(key, [])) <= 5
                    for key in required_keys
                )
                if key_set == required_keys and counts_valid:
                    categories = candidate
                    step.success = True
        except Exception:
            step.success = False
            categories = {}

        self.log_step(step)
        self._log_step_reward(1, rewards_step1(categories if step.success else {}))
        return step.success, categories, step

    def _log_step_reward(self, step_number: int, report: StepRewardsReport):
        if report is None:
            return

        details = [
            {
                "name": result.name,
                "passed": bool(result.passed),
                "detail": result.detail,
            }
            for result in report.results
        ]

        metrics_path = os.path.join(self.script_dir, "..", "..", "results", f"metrics_{self.run_timestamp}.json")
        if os.path.exists(metrics_path):
            with open(metrics_path, "r", encoding="utf-8") as f:
                metrics = json.load(f)
        else:
            metrics = {"run_timestamp": self.run_timestamp, "steps": {}}

        metrics["steps"][str(step_number)] = {
            "pass_rate": report.pass_rate,
            "results": details,
        }

        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        self._save_reward_to_database(step_number, report)

    def _save_reward_to_database(self, step_number: int, report: StepRewardsReport):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        details = [
            {
                "name": result.name,
                "passed": bool(result.passed),
                "detail": result.detail,
            }
            for result in report.results
        ]
        cursor.execute(
            '''
            INSERT INTO step_rewards (run_timestamp, step_number, pass_rate, num_tests, detail_json)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (
                self.run_timestamp,
                step_number,
                float(report.pass_rate),
                len(details),
                json.dumps(details),
            ),
        )
        conn.commit()
        conn.close()

    def _write_final_result(
        self,
        final_result: SevenStepResult,
        assessment: Optional[Dict[str, Any]] = None,
    ) -> None:
        steps_data = []
        for step in final_result.steps_completed:
            steps_data.append(
                {
                    "step_number": step.step_number,
                    "step_name": step.step_name,
                    "model_used": step.model_used,
                    "success": bool(step.success),
                    "timestamp": step.timestamp,
                    "response": step.response,
                }
            )

        payload: Dict[str, Any] = {
            "run_timestamp": self.run_timestamp,
            "topic": final_result.topic,
            "subtopic": final_result.subtopic,
            "difficulty": final_result.difficulty,
            "final_success": bool(final_result.final_success),
            "stopped_at_step": final_result.stopped_at_step,
            "differentiation_achieved": bool(final_result.differentiation_achieved),
            "student_assessment_created": bool(final_result.student_assessment_created),
            "total_attempts": final_result.total_attempts,
            "weak_model_failures": final_result.weak_model_failures,
            "steps": steps_data,
            "generated_at": datetime.now().isoformat(),
        }

        if assessment is not None:
            payload["assessment"] = assessment

        try:
            with open(self.results_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception as exc:
            logger.warning("Failed to write final result artifact: %s", exc)

    def _init_database(self):
        '''Initialize database with enhanced logging tables'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create enhanced_pipeline_runs table to track each run
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enhanced_pipeline_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_timestamp TEXT NOT NULL UNIQUE,
                topic TEXT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                total_steps INTEGER,
                differentiation_achieved BOOLEAN,
                final_success BOOLEAN
            )
        ''')

        # Create enhanced_step_responses table for full step data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enhanced_step_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_timestamp TEXT NOT NULL,
                topic TEXT NOT NULL,
                step_number INTEGER NOT NULL,
                step_name TEXT NOT NULL,
                model_used TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                response_length INTEGER NOT NULL,
                full_response TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create step_rewards table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS step_rewards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_timestamp TEXT NOT NULL,
                step_number INTEGER NOT NULL,
                pass_rate REAL NOT NULL,
                num_tests INTEGER NOT NULL,
                detail_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def step2_generate_error_catalog(self, topic: str, subtopic: str, difficulty: str) -> Tuple[bool, List[Dict], PipelineStep]:
        template = self._get_prompt_template("step2_error_catalog")
        prompt = builders.build_step2_prompt(topic, subtopic, difficulty, template)
        tools = self._get_tools("step2_error_catalog")
        
        response = self.invoke_model_with_tools(self.model_strong, prompt, tools)
        step = PipelineStep(2, "Generate conceptual error catalog", self.model_strong, False, str(response), datetime.now().isoformat())

        errors: List[Dict[str, Any]] = []
        try:
            if isinstance(response, dict) and isinstance(response.get('errors'), list):
                raw_errors = response['errors']
                for entry in raw_errors:
                    if not isinstance(entry, dict):
                        continue
                    entry_copy = dict(entry)
                    if 'match_hint' not in entry_copy and 'code_pattern' in entry_copy:
                        entry_copy['match_hint'] = entry_copy['code_pattern']
                    if 'code_pattern' not in entry_copy and 'match_hint' in entry_copy:
                        entry_copy['code_pattern'] = entry_copy['match_hint']
                    errors.append(entry_copy)

            step.success = len(errors) == 6
        except Exception:
            step.success = False
            errors = []

        self.log_step(step)
        return step.success, errors, step

    def step3_generate_strategic_question(self, topic: str, subtopic: str, difficulty: str, error_catalog: List[Dict], previous_failures: List[str] = None, use_thinking: bool = False) -> Tuple[bool, Dict, PipelineStep]:
        template = self._get_prompt_template("step3_strategic_question")
        prompt = builders.build_step3_prompt(topic, subtopic, difficulty, error_catalog, template, previous_failures)
        tools = self._get_tools("step3_strategic_question")

        response = self.invoke_model_with_tools(
            self.model_strong,
            prompt,
            tools,
            use_thinking=use_thinking,
            thinking_budget=2048
        )
        step = PipelineStep(3, "Generate strategic implementation challenge", self.model_strong, False, str(response), datetime.now().isoformat())

        question: Dict[str, Any] = {}
        try:
            if isinstance(response, dict) and 'error' not in response:
                candidate = response
                requirements = candidate.get("requirements")
                artifact_type = candidate.get("artifact_type")
                required_fields_present = all(
                    isinstance(candidate.get(field), str) and candidate.get(field).strip()
                    for field in ("title", "question_text", "context", "success_criteria")
                )
                valid_req_count = isinstance(requirements, list) and 4 <= len(requirements) <= 6
                valid_artifact = isinstance(artifact_type, str) and artifact_type in {
                    "code", "prose", "math", "email", "table", "diagram", "plan", "pseudo", "query", "other"
                }

                if required_fields_present and valid_req_count and valid_artifact:
                    question = candidate
                    step.success = True
        except Exception:
            step.success = False
            question = {}

        self.log_step(step)
        return step.success, question, step

    def step4_test_sonnet(self, question: Dict) -> Tuple[bool, str, PipelineStep]:
        template = self._get_prompt_template("step4_test_sonnet")
        prompt = builders.build_step45_prompt(question, template)
        response = self.invoke_model(self.model_mid, prompt)
        step = PipelineStep(4, "Test Sonnet (mid-tier) implementation", self.model_mid, True, response, datetime.now().isoformat())
        self.log_step(step)
        return True, response, step

    def step5_test_haiku(self, question: Dict) -> Tuple[bool, str, PipelineStep]:
        template = self._get_prompt_template("step5_test_haiku")
        prompt = builders.build_step45_prompt(question, template)
        response = self.invoke_model(self.model_weak, prompt)
        step = PipelineStep(5, "Test Haiku (weak-tier) implementation", self.model_weak, True, response, datetime.now().isoformat())
        self.log_step(step)
        return True, response, step

    def step6_judge_responses(self, question: Dict, sonnet_response: str, haiku_response: str, error_catalog: List[Dict]) -> Tuple[bool, Dict[str, Any], List[str], PipelineStep]:
        template = self._get_prompt_template("step6_judge_responses")
        prompt = builders.build_step6_prompt(question, sonnet_response, haiku_response, error_catalog, template)
        tools = self._get_tools("step6_judge_responses")
        response = self.invoke_model_with_tools(self.model_strong, prompt, tools)
        step = PipelineStep(
            6,
            "Judge implementation differentiation",
            self.model_strong,
            False,
            json.dumps(response) if isinstance(response, (dict, list, str)) else str(response),
            datetime.now().isoformat()
        )

        judge_payload: Dict[str, Any] = {}
        failures_weaker: List[str] = []
        differentiation_achieved = False

        try:
            if isinstance(response, dict) and 'error' not in response:
                candidate = dict(response)

                diff_val = candidate.get("differentiation_achieved")
                if isinstance(diff_val, str):
                    differentiation_achieved = diff_val.strip().lower() in {"yes", "true", "1"}
                elif isinstance(diff_val, bool):
                    differentiation_achieved = diff_val

                candidate["differentiation_achieved"] = differentiation_achieved

                failures_raw = candidate.get("failures_weaker", [])
                if isinstance(failures_raw, list):
                    failures_weaker = [
                        str(item).strip()
                        for item in failures_raw
                        if isinstance(item, (str, int, float)) and str(item).strip()
                    ]

                judge_payload = candidate
                step.success = True
                step.response = json.dumps(judge_payload)
        except Exception:
            step.success = False

        self.log_step(step)
        return differentiation_achieved, judge_payload, failures_weaker, step

    def step7_create_student_assessment(self, question: Dict, sonnet_response: str, haiku_response: str, haiku_failures: List[str]) -> Tuple[bool, Dict, PipelineStep]:
        topic = question.get('context', 'AI/ML implementation')
        subtopic = question.get('title', 'Implementation Challenge')

        validation_feedback: Optional[List[str]] = None
        last_step: Optional[PipelineStep] = None

        for attempt in range(1, self.config.get('step7_max_attempts', 3) + 1):
            template = self._get_prompt_template("step7_student_assessment")
            prompt = builders.build_step7_prompt(
                topic=topic,
                subtopic=subtopic,
                haiku_failures=haiku_failures,
                haiku_response=haiku_response,
                sonnet_response=sonnet_response,
                template=template,
                config=self.config,
                validation_feedback=validation_feedback
            )
            tools = self._get_tools("step7_student_assessment")

            response = self.invoke_model_with_tools(self.model_strong, prompt, tools)
            step = PipelineStep(
                7,
                f"Create student assessment from weak model failures (attempt {attempt})",
                self.model_strong,
                False,
                json.dumps(response) if isinstance(response, (dict, list, str)) else str(response),
                datetime.now().isoformat()
            )

            validation_feedback = []

            if not isinstance(response, dict) or 'error' in response:
                validation_feedback.append("The model did not return valid structured output via the student_assessment_tool.")
                step.response = json.dumps({
                    "model_response": response,
                    "validation_errors": validation_feedback
                })
                self.log_step(step)
                last_step = step
                continue

            is_valid, sanitized_payload, validation_errors = self.assessment_validator.validate(response)

            if is_valid:
                step.success = True
                step.response = json.dumps(sanitized_payload)
                self.log_step(step)
                return True, sanitized_payload, step

            validation_feedback = validation_errors
            step.response = json.dumps({
                "model_response": response,
                "validation_errors": validation_errors
            })
            self.log_step(step)
            last_step = step

        if last_step is None:
            last_step = PipelineStep(
                7,
                "Create student assessment from weak model failures",
                self.model_strong,
                False,
                json.dumps({"validation_errors": validation_feedback or ["Unknown Step 7 failure."]}),
                datetime.now().isoformat()
            )
            self.log_step(last_step)

        return False, {}, last_step

    def run_full_pipeline(self, topic: str, max_attempts: int = 3) -> SevenStepResult:
        logger.info(f"Starting corrected 7-step pipeline for: {topic}")
        
        self.current_topic = topic
        
        with open(self.log_file, "w") as f:
            f.write(f"Pipeline Run Started: {datetime.now()}\n")
            f.write(f"Run ID: {self.run_timestamp}\n")
            f.write(f"Topic: {topic}\n")
            f.write("="*80 + "\n")
        
        steps_completed = []

        self.repo.mark_run_start(self.run_timestamp, topic)
        success, categories, step1 = self.step1_generate_difficulty_categories(topic)
        steps_completed.append(step1)

        if not success:
            result = SevenStepResult(topic, "", "", steps_completed, False, 1, False, False, 1, [])
            self.repo.mark_run_end(
                self.run_timestamp,
                total_steps=len(steps_completed),
                differentiation_achieved=False,
                final_success=False
            )
            self._write_final_result(result)
            return result

        available_difficulties = [d for d in ["Beginner", "Intermediate", "Advanced"] if d in categories and categories[d]]
        if available_difficulties:
            difficulty = random.choice(available_difficulties)
            subtopics = categories.get(difficulty, ["General concepts"])
            subtopic = random.choice(subtopics) if subtopics else "General concepts"
        else:
            difficulty = "Intermediate"
            subtopic = "General concepts"

        success, error_catalog, step2 = self.step2_generate_error_catalog(topic, subtopic, difficulty)
        steps_completed.append(step2)
        if not success:
            result = SevenStepResult(topic, subtopic, difficulty, steps_completed, False, 2, False, False, 1, [])
            self.repo.mark_run_end(
                self.run_timestamp,
                total_steps=len(steps_completed),
                differentiation_achieved=False,
                final_success=False
            )
            self._write_final_result(result)
            return result
        
        previous_failures = []
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Strategic differentiation attempt {attempt} for {topic}")
            attempt_steps = []

            use_thinking = (attempt > 1 and getattr(self, 'judge_supports_thinking', False))

            success, question, step3 = self.step3_generate_strategic_question(
                topic, subtopic, difficulty, error_catalog, previous_failures, use_thinking=use_thinking)
            attempt_steps.append(step3)
            if not success:
                continue

            sonnet_success, sonnet_response, step4 = self.step4_test_sonnet(question)
            attempt_steps.append(step4)

            haiku_success, haiku_response, step5 = self.step5_test_haiku(question)
            attempt_steps.append(step5)

            differentiation_achieved, judge_payload, haiku_failures, step6 = self.step6_judge_responses(
                question, sonnet_response, haiku_response, error_catalog)
            attempt_steps.append(step6)

            steps_completed.extend(attempt_steps)

            if differentiation_achieved:
                logger.info(f"✅ Differentiation achieved on attempt {attempt}")

                success, assessment, step7 = self.step7_create_student_assessment(
                    question, sonnet_response, haiku_response, haiku_failures)
                steps_completed.append(step7)

                result = SevenStepResult(
                    topic=topic,
                    subtopic=subtopic,
                    difficulty=difficulty,
                    steps_completed=steps_completed,
                    final_success=True,
                    stopped_at_step=7,
                    differentiation_achieved=True,
                    student_assessment_created=success,
                    total_attempts=attempt,
                    weak_model_failures=haiku_failures,
                    assessment=assessment if success else {}
                )
                self.repo.mark_run_end(
                    self.run_timestamp,
                    total_steps=len(steps_completed),
                    differentiation_achieved=True,
                    final_success=True
                )
                return result
            else:
                logger.info(f"❌ Attempt {attempt} failed differentiation - Step 6 blocked progression")
                previous_failures.append(f"Attempt {attempt} failed.")
        
        result = SevenStepResult(
            topic=topic,
            subtopic=subtopic,
            difficulty=difficulty,
            steps_completed=steps_completed,
            final_success=False,
            stopped_at_step=6,
            differentiation_achieved=False,
            student_assessment_created=False,
            total_attempts=max_attempts,
            weak_model_failures=[]
        )
        self.repo.mark_run_end(
            self.run_timestamp,
            total_steps=len(steps_completed),
            differentiation_achieved=False,
            final_success=False
        )
        return result

    def run_full_pipeline_streaming(self, topic: str, max_attempts: int = 3):
        logger.info(f"Starting streaming 7-step pipeline for: {topic}")

        self.current_topic = topic

        with open(self.log_file, "w") as f:
            f.write(f"Pipeline Run Started: {datetime.now()}\n")
            f.write(f"Run ID: {self.run_timestamp}\n")
            f.write(f"Topic: {topic}\n")
            f.write("="*80 + "\n")

        steps_completed = []

        self.repo.mark_run_start(self.run_timestamp, topic)
        success, categories, step1 = self.step1_generate_difficulty_categories(topic)
        steps_completed.append(step1)
        yield step1

        if not success:
            result = SevenStepResult(topic, "", "", steps_completed, False, 1, False, False, 1, [])
            self.repo.mark_run_end(
                self.run_timestamp,
                total_steps=len(steps_completed),
                differentiation_achieved=False,
                final_success=False
            )
            yield {"final_result": result}
            return

        available_difficulties = [d for d in ["Beginner", "Intermediate", "Advanced"] if d in categories and categories[d]]
        if available_difficulties:
            difficulty = random.choice(available_difficulties)
            subtopics = categories.get(difficulty, ["General concepts"])
            subtopic = random.choice(subtopics) if subtopics else "General concepts"
        else:
            difficulty = "Intermediate"
            subtopic = "General concepts"

        success, error_catalog, step2 = self.step2_generate_error_catalog(topic, subtopic, difficulty)
        steps_completed.append(step2)
        yield step2

        if not success:
            result = SevenStepResult(topic, subtopic, difficulty, steps_completed, False, 2, False, False, 1, [])
            self.repo.mark_run_end(
                self.run_timestamp,
                total_steps=len(steps_completed),
                differentiation_achieved=False,
                final_success=False
            )
            yield {"final_result": result}
            return

        previous_failures = []
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Strategic differentiation attempt {attempt} for {topic}")
            attempt_steps = []

            use_thinking = (attempt > 1 and getattr(self, 'judge_supports_thinking', False))

            success, question, step3 = self.step3_generate_strategic_question(
                topic, subtopic, difficulty, error_catalog, previous_failures, use_thinking=use_thinking)
            attempt_steps.append(step3)
            yield step3

            if not success:
                steps_completed.extend(attempt_steps)
                continue

            sonnet_success, sonnet_response, step4 = self.step4_test_sonnet(question)
            attempt_steps.append(step4)
            yield step4

            haiku_success, haiku_response, step5 = self.step5_test_haiku(question)
            attempt_steps.append(step5)
            yield step5

            differentiation_achieved, judge_payload, haiku_failures, step6 = self.step6_judge_responses(
                question, sonnet_response, haiku_response, error_catalog)
            attempt_steps.append(step6)
            yield step6

            steps_completed.extend(attempt_steps)

            if differentiation_achieved:
                logger.info(f"✅ Differentiation achieved on attempt {attempt}")

                success, assessment, step7 = self.step7_create_student_assessment(
                    question, sonnet_response, haiku_response, haiku_failures)
                steps_completed.append(step7)
                yield step7

                final_result = SevenStepResult(
                    topic=topic,
                    subtopic=subtopic,
                    difficulty=difficulty,
                    steps_completed=steps_completed,
                    final_success=True,
                    stopped_at_step=7,
                    differentiation_achieved=True,
                    student_assessment_created=success,
                    total_attempts=attempt,
                    weak_model_failures=haiku_failures,
                    assessment=assessment if success else {}
                )
                self.repo.mark_run_end(
                    self.run_timestamp,
                    total_steps=len(steps_completed),
                    differentiation_achieved=True,
                    final_success=True
                )
                yield {"final_result": final_result, "assessment": assessment}
                return
            else:
                logger.info(f"❌ Attempt {attempt} failed differentiation")
                previous_failures.append(f"Attempt {attempt} failed.")

        final_result = SevenStepResult(
            topic=topic,
            subtopic=subtopic,
            difficulty=difficulty,
            steps_completed=steps_completed,
            final_success=False,
            stopped_at_step=6,
            differentiation_achieved=False,
            student_assessment_created=False,
            total_attempts=max_attempts,
            weak_model_failures=[]
        )
        self.repo.mark_run_end(
            self.run_timestamp,
            total_steps=len(steps_completed),
            differentiation_achieved=False,
            final_success=False
        )
        yield {"final_result": final_result}