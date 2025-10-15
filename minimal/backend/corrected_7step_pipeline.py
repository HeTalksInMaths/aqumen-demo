'''
Corrected 7-Step Adversarial Pipeline Implementation
Step 3: Generates strategic implementation challenges (NO pre-embedded errors)
Step 4-5: Models provide complete implementations
Step 6: Judge compares implementations against error catalog
Step 7: Creates student assessment based on actual weak model failures
'''

import json
import os
import random
from copy import deepcopy
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
import re

from config import load_prompts, load_tools
from roles import load_model_roles
from clients.bedrock import BedrockRuntime
from services.invoke import Invoker
from persistence.repo import Repo
import sqlite3
from analytics.rewards import (
    StepRewardsReport,
    rewards_step1,
    rewards_step2,
    rewards_step3,
    rewards_step45,
    rewards_step6,
    rewards_step7,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PipelineStep:
    step_number: int
    step_name: str
    model_used: str
    success: bool
    response: str
    timestamp: str

@dataclass
class SevenStepResult:
    topic: str
    subtopic: str
    difficulty: str
    steps_completed: List[PipelineStep]
    final_success: bool
    stopped_at_step: int
    differentiation_achieved: bool
    student_assessment_created: bool
    total_attempts: int
    weak_model_failures: List[str]  # Track actual failure patterns

class CorrectedSevenStepPipeline:
    def __init__(self):
        '''Initialize the corrected 7-step pipeline with timestamped logging'''
        self.roles = load_model_roles()
        self.aws_region = "us-west-2"

        # Model assignments (env-driven with sensible defaults)
        self.model_strong = self.roles["judge"].id
        self.model_mid = self.roles["mid"].id
        self.model_weak = self.roles["weak"].id
        self.judge_supports_thinking = self.roles["judge"].supports_thinking

        self.bedrock_runtime = BedrockRuntime(region=self.aws_region)
        self.invoker = Invoker(self.bedrock_runtime)

        # Get the absolute path of the directory containing this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.script_dir = script_dir

        # Generate timestamped file names for this pipeline run
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create paths relative to the script's location
        log_dir = os.path.join(script_dir, "logs", "current")
        results_dir = os.path.join(script_dir, "results")
        self.log_file = os.path.join(log_dir, f"pipeline_run_{self.run_timestamp}.txt")
        self.results_file = os.path.join(script_dir, f"corrected_7step_results_{self.run_timestamp}.json")
        
        # Ensure log directories exist
        os.makedirs(log_dir, exist_ok=True)
        os.makedirs(os.path.join(script_dir, "logs", "archived"), exist_ok=True)
        os.makedirs(results_dir, exist_ok=True)
        
        # Initialize database connection relative to the script's location
        self.db_path = os.path.join(script_dir, "pipeline_results.db")
        self.repo = Repo(self.db_path)

        # Step 7 validation configuration
        self.allowed_difficulties = {"Beginner", "Intermediate", "Advanced", "Expert"}
        self.step7_max_attempts = 3
        self.min_code_lines = 24  # keeps the game substantive
        self.max_code_lines = 60
        self.min_errors = 1
        self.max_errors = 5
        self.min_error_span = 20
        self.max_error_span = 120

        try:
            self.prompts = load_prompts()
            self.tools = load_tools()
        except Exception as exc:
            logger.error(f"Failed to load prompt/tool configuration: {exc}")
            raise

    def invoke_model(self, model_id: str, prompt: str, max_tokens: int = 2048) -> str:
        '''Invoke a model via the Bedrock runtime wrapper.'''
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
        '''Invoke a model via the Bedrock runtime wrapper with tool support.'''
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
        '''Log a pipeline step to both file and database'''
        # Log to timestamped file
        with open(self.log_file, "a") as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"STEP {step.step_number}: {step.step_name}\n")
            f.write(f"MODEL: {step.model_used}\n")
            f.write(f"TIMESTAMP: {step.timestamp}\n")
            f.write(f"SUCCESS: {step.success}\n")
            f.write(f"RESPONSE:\n{step.response}\n")
        
        # Log to database
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

        metrics_path = os.path.join(self.script_dir, "results", f"metrics_{self.run_timestamp}.json")
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

    def _get_prompt_template(self, step_key: str) -> str:
        '''Retrieve the prompt template string for a pipeline step.'''
        entry = self.prompts.get(step_key)
        if isinstance(entry, dict):
            template = entry.get("template")
        else:
            template = entry

        if not isinstance(template, str):
            raise KeyError(f"Prompt template missing for step '{step_key}'")

        return template

    def _get_tools(self, step_key: str) -> List[Dict[str, Any]]:
        '''Retrieve tool specifications for a pipeline step.'''
        tool_entry = self.tools.get(step_key)

        if tool_entry is None:
            raise KeyError(f"Tool configuration missing for step '{step_key}'")

        if isinstance(tool_entry, list):
            return deepcopy(tool_entry)

        return [deepcopy(tool_entry)]


    def step1_generate_difficulty_categories(self, topic: str) -> Tuple[bool, Dict[str, List[str]], PipelineStep]:
        '''Step 1: Generate difficulty categories'''
        template = self._get_prompt_template("step1_difficulty_categories")
        prompt = template.format(topic=topic)
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
                else:
                    step.success = False
            else:
                step.success = False
        except Exception:
            step.success = False
            categories = {}

        self.log_step(step)
        self._log_step_reward(1, rewards_step1(categories if step.success else {}))

        if not step.success:
            categories = {}

        return step.success, categories, step

    def step2_generate_error_catalog(self, topic: str, subtopic: str, difficulty: str) -> Tuple[bool, List[Dict], PipelineStep]:
        '''Step 2: Generate conceptual error catalog - patterns that differentiate strong vs weak models'''
        template = self._get_prompt_template("step2_error_catalog")
        prompt = template.format(topic=topic, difficulty=difficulty, subtopic=subtopic)
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
        self._log_step_reward(2, rewards_step2(errors))

        if not step.success:
            errors = []

        return step.success, errors, step

    def step3_generate_strategic_question(self, topic: str, subtopic: str, difficulty: str, error_catalog: List[Dict], previous_failures: List[str] = None, use_thinking: bool = False) -> Tuple[bool, Dict, PipelineStep]:
        '''Step 3: Generate strategic implementation challenge (NO pre-embedded errors)'''
        template = self._get_prompt_template("step3_strategic_question")

        failure_feedback = ""
        if previous_failures:
            failure_feedback = (
                "\nVALIDATION FEEDBACK (resolve before returning a new challenge):\n"
                + "\n".join(f"- {failure}" for failure in previous_failures)
            )

        catalog_names: List[str] = []
        for error in error_catalog or []:
            name = error.get('mistake')
            if isinstance(name, str) and name.strip():
                catalog_names.append(f"- {name.strip()}")

        prompt = template.format(
            topic=topic,
            subtopic=subtopic,
            difficulty=difficulty,
            catalog_names="\n".join(catalog_names) if catalog_names else "- (no catalog names available)",
            failure_feedback=failure_feedback
        )

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
                else:
                    step.success = False
            else:
                step.success = False
        except Exception:
            step.success = False
            question = {}

        self.log_step(step)
        self._log_step_reward(3, rewards_step3(question if step.success else {}))

        if not step.success:
            question = {}

        return step.success, question, step

    def step4_test_sonnet(self, question: Dict) -> Tuple[bool, str, PipelineStep]:
        '''Step 4: Test Sonnet (Haiku 3.5) implementation response'''
        template = self._get_prompt_template("step4_test_sonnet")
        requirements = question.get('requirements', []) or []
        prompt = template.format(
            context=question.get('context', 'the domain'),
            artifact=question.get('artifact_type', 'artifact'),
            title=question.get('title', 'Implementation Challenge'),
            question_text=question.get('question_text', ''),
            requirements="\n".join(f"- {req}" for req in requirements) if requirements else "- (no requirements provided)",
            success_criteria=question.get('success_criteria', 'Meets requirements with sound reasoning and robustness')
        )

        response = self.invoke_model(self.model_mid, prompt)
        step = PipelineStep(4, "Test Sonnet (mid-tier) implementation", self.model_mid, True, response, datetime.now().isoformat())

        self.log_step(step)
        self._log_step_reward(4, rewards_step45(response, requirements))
        return True, response, step

    def step5_test_haiku(self, question: Dict) -> Tuple[bool, str, PipelineStep]:
        '''Step 5: Test Haiku (Haiku 3) implementation response'''
        template = self._get_prompt_template("step5_test_haiku")
        requirements = question.get('requirements', []) or []
        prompt = template.format(
            context=question.get('context', 'the domain'),
            artifact=question.get('artifact_type', 'artifact'),
            title=question.get('title', 'Implementation Challenge'),
            question_text=question.get('question_text', ''),
            requirements="\n".join(f"- {req}" for req in requirements) if requirements else "- (no requirements provided)",
            success_criteria=question.get('success_criteria', 'Meets requirements with sound reasoning and robustness')
        )

        response = self.invoke_model(self.model_weak, prompt)
        step = PipelineStep(5, "Test Haiku (weak-tier) implementation", self.model_weak, True, response, datetime.now().isoformat())

        self.log_step(step)
        self._log_step_reward(5, rewards_step45(response, requirements))
        return True, response, step

    def step6_judge_responses(self, question: Dict, sonnet_response: str, haiku_response: str, error_catalog: List[Dict]) -> Tuple[bool, Dict[str, Any], List[str], PipelineStep]:
        '''Step 6: Judge if differentiation was achieved by comparing implementations against error catalog'''
        
        # Format entire error catalog for judge visibility
        error_patterns_text = ""
        for i, error in enumerate(error_catalog or [], 1):
            error_patterns_text += (
                f"\n{i}. {error.get('mistake', 'Unknown error')}\n"
                f"   Why problematic: {error.get('why_wrong', 'Issues not specified')}\n"
                f"   Code pattern: {error.get('code_pattern', error.get('match_hint', 'Not specified'))}"
            )

        template = self._get_prompt_template("step6_judge_responses")
        prompt = template.format(
            question_text=question.get('question_text', ''),
            context=question.get('context', ''),
            requirements=", ".join(question.get('requirements', [])),
            error_patterns_text=error_patterns_text,
            sonnet_response=sonnet_response,
            haiku_response=haiku_response
        )
        
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
                else:
                    differentiation_achieved = False
                candidate["differentiation_achieved"] = differentiation_achieved

                failures_raw = candidate.get("failures_weaker", [])
                if isinstance(failures_raw, list):
                    failures_weaker = [
                        str(item).strip()
                        for item in failures_raw
                        if isinstance(item, (str, int, float)) and str(item).strip()
                    ]
                else:
                    failures_weaker = []

                judge_payload = candidate
                step.success = True
                step.response = json.dumps(judge_payload)
            else:
                step.success = False
        except Exception:
            step.success = False
            judge_payload = {}
            failures_weaker = []

        self.log_step(step)
        catalog_names = [str((entry or {}).get('mistake', '')).strip() for entry in (error_catalog or []) if isinstance(entry, dict)]
        self._log_step_reward(6, rewards_step6(judge_payload if step.success else {}, catalog_names, haiku_response))
        return differentiation_achieved, judge_payload, failures_weaker, step

    def _build_step7_prompt(
        self,
        topic: str,
        subtopic: str,
        haiku_failures: List[str],
        haiku_response: str,
        sonnet_response: str,
        validation_feedback: Optional[List[str]] = None
    ) -> Tuple[str, List[Dict[str, Any]]]:
        '''Compose the Step 7 prompt (optionally injecting feedback from validation failures).'''

        validation_block = ""
        if validation_feedback:
            feedback_lines = "\n".join(f"- {issue}" for issue in validation_feedback)
            validation_block = (
                "\n\nVALIDATION FEEDBACK FROM THE LAST ATTEMPT:\n"
                "Fix every issue below before returning the next result:\n"
                f"{feedback_lines}\n"
            )

        template = self._get_prompt_template("step7_student_assessment")
        prompt = template.format(
            haiku_failures="\n".join(f"- {failure}" for failure in haiku_failures),
            haiku_response_preview=haiku_response[:2000],
            sonnet_response_preview=sonnet_response[:1000],
            min_code_lines=self.min_code_lines,
            max_code_lines=self.max_code_lines,
            min_error_span=self.min_error_span,
            max_error_span=self.max_error_span,
            min_errors=self.min_errors,
            max_errors=self.max_errors,
            allowed_difficulties=", ".join(sorted(self.allowed_difficulties)),
            topic=topic,
            subtopic=subtopic,
            validation_feedback=validation_block
        )

        tools = self._get_tools("step7_student_assessment")
        if tools:
            difficulty_schema = tools[0].get("input_schema", {}).get("properties", {}).get("difficulty")
            if isinstance(difficulty_schema, dict):
                difficulty_schema["enum"] = sorted(self.allowed_difficulties)

        return prompt, tools

    def _validate_assessment_payload(self, payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
        '''Run deterministic checks to ensure Step 7 output matches frontend expectations.'''
        errors: List[str] = []

        if not isinstance(payload, dict):
            return False, {}, ["Model did not return a JSON object."]

        title = payload.get("title")
        if not isinstance(title, str) or not title.strip():
            errors.append("Title must be a non-empty string.")
        else:
            title = title.strip()

        difficulty = payload.get("difficulty")
        if not isinstance(difficulty, str) or difficulty not in self.allowed_difficulties:
            errors.append(f"Difficulty must be one of {sorted(self.allowed_difficulties)}.")

        allowed_content_types = {"code", "prose", "math", "email", "table", "diagram", "plan", "pseudo", "query", "other"}
        content_type = payload.get("content_type")
        if not isinstance(content_type, str):
            if isinstance(payload.get("code"), list):
                content_type = "code"
            else:
                errors.append("content_type must be provided and be one of the supported modalities.")
                content_type = "code"
        content_type = content_type.strip().lower()
        if content_type not in allowed_content_types:
            errors.append(f"content_type must be one of {sorted(allowed_content_types)}.")

        content_lines = payload.get("content")
        if content_lines is None:
            content_lines = payload.get("code")

        if isinstance(content_lines, str):
            try:
                parsed = json.loads(content_lines)
                if isinstance(parsed, list) and all(isinstance(line, str) for line in parsed):
                    content_lines = parsed
                    logger.warning(f"Step 7 auto-fix: Converted stringified array to native JSON array ({len(parsed)} lines)")
                else:
                    content_lines = content_lines.splitlines()
            except (json.JSONDecodeError, TypeError):
                content_lines = content_lines.splitlines()

        if not isinstance(content_lines, list) or not all(isinstance(line, str) for line in content_lines):
            errors.append("content must be an array of strings.")
            content_lines = []
        else:
            content_lines = [line.rstrip("\r\n") for line in content_lines]
            if not (self.min_code_lines <= len(content_lines) <= self.max_code_lines):
                errors.append(f"content must contain between {self.min_code_lines} and {self.max_code_lines} lines (found {len(content_lines)}).")

        errors_list = payload.get("errors")
        if not isinstance(errors_list, list) or not all(isinstance(item, dict) for item in (errors_list or [])):
            errors.append("Errors must be an array of objects.")
            errors_list = []

        if errors_list and not (self.min_errors <= len(errors_list) <= self.max_errors):
            errors.append(f"Errors array must contain between {self.min_errors} and {self.max_errors} entries (found {len(errors_list)}).")

        joined_content = "\n".join(content_lines)
        marked_spans = re.findall(r"<<([^<>]+)>>", joined_content)

        if not marked_spans:
            errors.append("No << >> error spans were found in the content.")

        # Ensure raw delimiter counts are balanced
        if joined_content.count("<<") != joined_content.count(">>"):
            errors.append("Unbalanced number of << and >> delimiters in the content.")

        sanitized_errors = []
        seen_ids = set()

        for idx, error_entry in enumerate(errors_list):
            error_id = error_entry.get("id")
            description = error_entry.get("description")

            if not isinstance(error_id, str) or not error_id.strip():
                errors.append(f"Error #{idx + 1} is missing a valid 'id'.")
                continue

            error_id = error_id.strip()
            if error_id in seen_ids:
                errors.append(f"Error id '{error_id}' is duplicated.")
            else:
                seen_ids.add(error_id)

            if not (self.min_error_span <= len(error_id) <= self.max_error_span):
                errors.append(f"Error id '{error_id}' must be between {self.min_error_span} and {self.max_error_span} characters (found {len(error_id)}).")

            occurrences = joined_content.count(f"<<{error_id}>>")
            if occurrences != 1:
                errors.append(f"Error id '{error_id}' must appear exactly once in the content; found {occurrences}.")

            if error_id not in marked_spans:
                errors.append(f"Error id '{error_id}' is not wrapped in << >> within the content.")

            if not isinstance(description, str) or not description.strip():
                errors.append(f"Error id '{error_id}' is missing a description.")
            else:
                desc = description.strip()
                if len(desc) > 180:
                    errors.append(f"Error description for id '{error_id}' is too long ({len(desc)} chars, max 180).")
                description = desc

            sanitized_errors.append({"id": error_id, "description": description})

        if marked_spans and errors_list and len(marked_spans) != len(errors_list):
            errors.append(f"Number of marked spans ({len(marked_spans)}) does not match number of error entries ({len(errors_list)}).")

        if errors:
            return False, {}, errors

        sanitized_payload = {
            "title": title,
            "difficulty": difficulty,
            "content_type": content_type,
            "content": content_lines,
            "code": content_lines,  # Backward compatibility for consumers expecting 'code'
            "errors": sanitized_errors
        }

        return True, sanitized_payload, []

    def step7_create_student_assessment(self, question: Dict, sonnet_response: str, haiku_response: str, haiku_failures: List[str]) -> Tuple[bool, Dict, PipelineStep]:
        '''Step 7: Create student assessment with error spans based on actual weak model failures'''

        topic = question.get('context', 'AI/ML implementation')
        subtopic = question.get('title', 'Implementation Challenge')

        validation_feedback: Optional[List[str]] = None
        last_step: Optional[PipelineStep] = None

        for attempt in range(1, self.step7_max_attempts + 1):
            prompt, tools = self._build_step7_prompt(
                topic=topic,
                subtopic=subtopic,
                haiku_failures=haiku_failures,
                haiku_response=haiku_response,
                sonnet_response=sonnet_response,
                validation_feedback=validation_feedback
            )

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
                payload = response if isinstance(response, dict) else {}
                self._log_step_reward(7, rewards_step7(payload))
                last_step = step
                continue

            is_valid, sanitized_payload, validation_errors = self._validate_assessment_payload(response)

            if is_valid:
                step.success = True
                step.response = json.dumps(sanitized_payload)
                self.log_step(step)
                self._log_step_reward(7, rewards_step7(sanitized_payload))
                return True, sanitized_payload, step

            validation_feedback = validation_errors
            step.response = json.dumps({
                "model_response": response,
                "validation_errors": validation_errors
            })
            self.log_step(step)
            self._log_step_reward(7, rewards_step7(response))
            last_step = step

        # If we exhaust retries, return failure with the last logged step
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
            self._log_step_reward(7, rewards_step7({}))

        return False, {}, last_step

    def run_full_pipeline(self, topic: str, max_attempts: int = 3) -> SevenStepResult:
        '''Run the complete corrected 7-step pipeline'''
        logger.info(f"Starting corrected 7-step pipeline for: {topic}")
        
        # Set current topic for database logging
        self.current_topic = topic
        
        # Initialize log file with run header
        with open(self.log_file, "w") as f:
            f.write(f"Pipeline Run Started: {datetime.now()}\n")
            f.write(f"Run ID: {self.run_timestamp}\n")
            f.write(f"Topic: {topic}\n")
            f.write("="*80 + "\n")
        
        steps_completed = []

        # Step 1: Generate difficulty categories
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

        # Randomly select difficulty level and subtopic for testing
        available_difficulties = [d for d in ["Beginner", "Intermediate", "Advanced"] if d in categories and categories[d]]
        if available_difficulties:
            difficulty = random.choice(available_difficulties)
            subtopics = categories.get(difficulty, ["General concepts"])
            subtopic = random.choice(subtopics) if subtopics else "General concepts"
        else:
            difficulty = "Intermediate"
            subtopic = "General concepts"

        # Step 2: Generate error catalog (run once)
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
        
        # Retry loop for steps 3-6 (strategic question → implementation testing → differentiation judgment)
        previous_failures = []
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Strategic differentiation attempt {attempt} for {topic}")
            attempt_steps = []

            # Enable thinking mode on retries (need deeper reasoning to craft harder questions)
            use_thinking = (attempt > 1 and getattr(self, 'judge_supports_thinking', False))

            # Step 3: Generate strategic implementation challenge
            success, question, step3 = self.step3_generate_strategic_question(
                topic, subtopic, difficulty, error_catalog, previous_failures, use_thinking=use_thinking)
            attempt_steps.append(step3)
            if not success:
                continue

            # Step 4: Test Sonnet implementation
            sonnet_success, sonnet_response, step4 = self.step4_test_sonnet(question)
            attempt_steps.append(step4)

            # Step 5: Test Haiku implementation
            haiku_success, haiku_response, step5 = self.step5_test_haiku(question)
            attempt_steps.append(step5)

            # Step 6: Judge differentiation (KEY DECISION POINT)
            differentiation_achieved, judge_payload, haiku_failures, step6 = self.step6_judge_responses(
                question, sonnet_response, haiku_response, error_catalog)
            attempt_steps.append(step6)

            steps_completed.extend(attempt_steps)

            judge_reasoning_text = ""
            if isinstance(judge_payload, dict):
                raw_reasoning = judge_payload.get("reasoning")
                if isinstance(raw_reasoning, str):
                    judge_reasoning_text = raw_reasoning.strip()
                if not judge_reasoning_text:
                    try:
                        judge_reasoning_text = json.dumps(judge_payload, ensure_ascii=False)
                    except (TypeError, ValueError):
                        judge_reasoning_text = str(judge_payload)
            else:
                judge_reasoning_text = ""

            judge_reasoning_lower = judge_reasoning_text.lower()

            if differentiation_achieved:
                logger.info(f"✅ Differentiation achieved on attempt {attempt}")

                # Step 7: Create student assessment based on actual weak model failures
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
                    weak_model_failures=haiku_failures
                )
                self.repo.mark_run_end(
                    self.run_timestamp,
                    total_steps=len(steps_completed),
                    differentiation_achieved=True,
                    final_success=True
                )
                self._write_final_result(result, assessment if success else None)
                return result
            else:
                logger.info(f"❌ Attempt {attempt} failed differentiation - Step 6 blocked progression")

                # Build detailed failure context for next attempt (includes actual responses)
                failure_summary = {
                    "attempt": attempt,
                    "judge_payload": judge_payload,
                    "sonnet_preview": sonnet_response[:300] + "..." if len(sonnet_response) > 300 else sonnet_response,
                    "haiku_preview": haiku_response[:300] + "..." if len(haiku_response) > 300 else haiku_response
                }

                # Extract specific failure reason
                if "both models succeeded" in judge_reasoning_lower:
                    failure_text = f"Attempt {attempt}: Both models avoided errors. Sonnet: {failure_summary['sonnet_preview']} | Haiku: {failure_summary['haiku_preview']} | Need MORE SUBTLE conceptual traps"
                elif "neither model succeeded" in judge_reasoning_lower:
                    failure_text = f"Attempt {attempt}: Neither model succeeded. Question may be too ambiguous. Judge said: {judge_reasoning_text[:200]}"
                else:
                    failure_text = f"Attempt {attempt}: Insufficient differentiation. Judge: {judge_reasoning_text[:300]}"

                previous_failures.append(failure_text)
        
        # All attempts failed - stopped at Step 6
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
        self._write_final_result(result)
        return result

    def run_full_pipeline_streaming(self, topic: str, max_attempts: int = 3):
        '''
        Generator version of run_full_pipeline that yields each step as it completes.

        This enables real-time streaming via SSE for debugging and progress tracking.

        Yields:
            PipelineStep objects as each step completes

        Final yield contains:
            Dict with final result including all metadata
        '''
        logger.info(f"Starting streaming 7-step pipeline for: {topic}")

        # Set current topic for database logging
        self.current_topic = topic

        # Initialize log file with run header
        with open(self.log_file, "w") as f:
            f.write(f"Pipeline Run Started: {datetime.now()}\n")
            f.write(f"Run ID: {self.run_timestamp}\n")
            f.write(f"Topic: {topic}\n")
            f.write("="*80 + "\n")

        steps_completed = []

        # Step 1: Generate difficulty categories
        self.repo.mark_run_start(self.run_timestamp, topic)
        success, categories, step1 = self.step1_generate_difficulty_categories(topic)
        steps_completed.append(step1)
        yield step1  # ← Yield immediately!

        if not success:
            result = SevenStepResult(topic, "", "", steps_completed, False, 1, False, False, 1, [])
            self.repo.mark_run_end(
                self.run_timestamp,
                total_steps=len(steps_completed),
                differentiation_achieved=False,
                final_success=False
            )
            self._write_final_result(result)
            yield {"final_result": result}
            return

        # Randomly select difficulty level and subtopic for testing
        available_difficulties = [d for d in ["Beginner", "Intermediate", "Advanced"] if d in categories and categories[d]]
        if available_difficulties:
            difficulty = random.choice(available_difficulties)
            subtopics = categories.get(difficulty, ["General concepts"])
            subtopic = random.choice(subtopics) if subtopics else "General concepts"
        else:
            difficulty = "Intermediate"
            subtopic = "General concepts"

        # Step 2: Generate error catalog
        success, error_catalog, step2 = self.step2_generate_error_catalog(topic, subtopic, difficulty)
        steps_completed.append(step2)
        yield step2  # ← Yield immediately!

        if not success:
            result = SevenStepResult(topic, subtopic, difficulty, steps_completed, False, 2, False, False, 1, [])
            self.repo.mark_run_end(
                self.run_timestamp,
                total_steps=len(steps_completed),
                differentiation_achieved=False,
                final_success=False
            )
            self._write_final_result(result)
            yield {"final_result": result}
            return

        # Retry loop for steps 3-6
        previous_failures = []
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Strategic differentiation attempt {attempt} for {topic}")
            attempt_steps = []

            # Enable thinking mode on retries
            use_thinking = (attempt > 1 and getattr(self, 'judge_supports_thinking', False))

            # Step 3: Generate strategic implementation challenge
            success, question, step3 = self.step3_generate_strategic_question(
                topic, subtopic, difficulty, error_catalog, previous_failures, use_thinking=use_thinking)
            attempt_steps.append(step3)
            yield step3  # ← Yield immediately!

            if not success:
                steps_completed.extend(attempt_steps)
                continue

            # Step 4: Test Sonnet implementation
            sonnet_success, sonnet_response, step4 = self.step4_test_sonnet(question)
            attempt_steps.append(step4)
            yield step4  # ← Yield immediately!

            # Step 5: Test Haiku implementation
            haiku_success, haiku_response, step5 = self.step5_test_haiku(question)
            attempt_steps.append(step5)
            yield step5  # ← Yield immediately!

            # Step 6: Judge differentiation (KEY DECISION POINT)
            differentiation_achieved, judge_payload, haiku_failures, step6 = self.step6_judge_responses(
                question, sonnet_response, haiku_response, error_catalog)
            attempt_steps.append(step6)
            yield step6  # ← Yield immediately!

            steps_completed.extend(attempt_steps)

            judge_reasoning_text = ""
            if isinstance(judge_payload, dict):
                raw_reasoning = judge_payload.get("reasoning")
                if isinstance(raw_reasoning, str):
                    judge_reasoning_text = raw_reasoning.strip()
                if not judge_reasoning_text:
                    try:
                        judge_reasoning_text = json.dumps(judge_payload, ensure_ascii=False)
                    except (TypeError, ValueError):
                        judge_reasoning_text = str(judge_payload)
            else:
                judge_reasoning_text = ""

            judge_reasoning_lower = judge_reasoning_text.lower()

            if differentiation_achieved:
                logger.info(f"✅ Differentiation achieved on attempt {attempt}")

                # Step 7: Create student assessment
                success, assessment, step7 = self.step7_create_student_assessment(
                    question, sonnet_response, haiku_response, haiku_failures)
                steps_completed.append(step7)
                yield step7  # ← Yield immediately!

                # Yield final result
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
                    weak_model_failures=haiku_failures
                )
                self.repo.mark_run_end(
                    self.run_timestamp,
                    total_steps=len(steps_completed),
                    differentiation_achieved=True,
                    final_success=True
                )
                self._write_final_result(final_result, assessment if success else None)
                yield {"final_result": final_result, "assessment": assessment}
                return
            else:
                logger.info(f"❌ Attempt {attempt} failed differentiation")

                # Extract specific failure reason
                if "both models succeeded" in judge_reasoning_lower:
                    failure_text = (
                        f"Attempt {attempt}: Both models avoided errors. Sonnet: "
                        f"{sonnet_response[:300]}... | Haiku: {haiku_response[:300]}... | Need MORE SUBTLE conceptual traps"
                    )
                elif "neither model succeeded" in judge_reasoning_lower:
                    failure_text = f"Attempt {attempt}: Neither model succeeded. Question may be too ambiguous."
                else:
                    failure_text = f"Attempt {attempt}: Insufficient differentiation."

                previous_failures.append(failure_text)

        # All attempts failed - stopped at Step 6
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
        self._write_final_result(final_result)
        yield {"final_result": final_result}

    def run_batch_test(self, topics: List[str]) -> List[SevenStepResult]:
        '''Run corrected 7-step pipeline on multiple topics'''
        results = []

        for i, topic in enumerate(topics, 1):
            print(f"\n{'='*60}")
            print(f"CORRECTED PIPELINE - TOPIC {i}/{len(topics)}: {topic}")
            print(f"{'='*60}")

            result = self.run_full_pipeline(topic)
            results.append(result)

            # Print immediate result
            if result.differentiation_achieved:
                print(f"✅ SUCCESS: Achieved differentiation in {result.total_attempts} attempts")
                if result.weak_model_failures:
                    print(f"   Weak model failures: {', '.join(result.weak_model_failures)}")
            else:
                print(f"❌ FAILED: Stopped at Step {result.stopped_at_step} after {result.total_attempts} attempts")

        # Save results
        self.save_results(results)
        return results

    def save_results(self, results: List[SevenStepResult]):
        '''Save comprehensive results'''
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Convert to serializable format
        results_data = []
        for result in results:
            steps_data = []
            for step in result.steps_completed:
                steps_data.append({
                    "step_number": step.step_number,
                    "step_name": step.step_name,
                    "model_used": step.model_used,
                    "success": step.success,
                    "timestamp": step.timestamp,
                    "response_length": len(step.response)
                })
            
            results_data.append({
                "topic": result.topic,
                "subtopic": result.subtopic,
                "difficulty": result.difficulty,
                "final_success": result.final_success,
                "stopped_at_step": result.stopped_at_step,
                "differentiation_achieved": result.differentiation_achieved,
                "student_assessment_created": result.student_assessment_created,
                "total_attempts": result.total_attempts,
                "weak_model_failures": result.weak_model_failures,
                "steps_completed": steps_data
            })
        
        final_data = {
            "pipeline_version": "corrected_7step_v1",
            "run_info": {
                "timestamp": datetime.now().isoformat(),
                "total_topics": len(results),
                "model_config": {
                    "strong": self.model_strong,
                    "mid": self.model_mid,
                    "weak": self.model_weak
                }
            },
            "results": results_data,
            "summary": {
                "topics_with_differentiation": len([r for r in results if r.differentiation_achieved]),
                "topics_stopped_at_step6": len([r for r in results if r.stopped_at_step == 6]),
                "average_attempts": sum(r.total_attempts for r in results) / len(results) if results else 0,
                "full_pipeline_success_rate": len([r for r in results if r.final_success]) / len(results) if results else 0,
                "common_weak_model_failures": self._extract_common_failures(results)
            }
        }
        
        filename = os.path.join(self.script_dir, f"corrected_7step_results_{timestamp}.json")
        with open(filename, "w") as f:
            json.dump(final_data, f, indent=2)
        
        print(f"\n📊 Results saved to: {filename}")
        print(f"📝 Detailed logs in: {self.log_file}")
        print(f"💾 Full step data stored in database: {self.db_path}")

    def _extract_common_failures(self, results: List[SevenStepResult]) -> Dict[str, int]:
        '''Extract common patterns from weak model failures'''
        failure_counts = {}
        for result in results:
            for failure in result.weak_model_failures:
                # Normalize failure text for counting
                normalized = failure.lower().strip()
                if normalized:
                    failure_counts[normalized] = failure_counts.get(normalized, 0) + 1
        
        # Return top 5 most common failures
        sorted_failures = sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_failures[:5])

def main():
    '''Run corrected 7-step pipeline test'''
    pipeline = CorrectedSevenStepPipeline()
    
    test_topics = [
        "LLM Post-Training with DPO",
        "Model Quantization and Optimization",
        "Reinforcement Learning from Human Feedback (RLHF)"
    ]
    
    print("🧠 CORRECTED 7-Step Adversarial Pipeline Test")
    print("="*50)
    print("Key Changes:")
    print("- Step 3: Strategic questions (NO pre-embedded errors)")
    print("- Steps 4-5: Models provide complete implementations")
    print("- Step 6: Judge compares implementations vs error catalog")
    print("- Step 7: Creates assessment based on actual weak failures")
    print("="*50)
    
    results = pipeline.run_batch_test(test_topics)
    
    # Summary analysis
    successful = len([r for r in results if r.differentiation_achieved])
    stopped_at_6 = len([r for r in results if r.stopped_at_step == 6])
    
    print("\n🏆 CORRECTED PIPELINE RESULTS")
    print(f"Topics with successful differentiation: {successful}/{len(results)}")
    print(f"Topics stopped at Step 6 (no differentiation): {stopped_at_6}/{len(results)}")
    print(f"Step 6 blocking rate: {(stopped_at_6/len(results))*100:.1f}%")
    
    # Show common failure patterns
    if results:
        common_failures = pipeline._extract_common_failures(results)
        if common_failures:
            print("\n📊 Common Weak Model Failure Patterns:")
            for failure, count in common_failures.items():
                print(f"  {count}x: {failure}")

if __name__ == "__main__":
    main()