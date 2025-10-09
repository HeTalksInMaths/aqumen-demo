"""
Corrected 7-Step Adversarial Pipeline Implementation
Step 3: Generates strategic implementation challenges (NO pre-embedded errors)
Step 4-5: Models provide complete implementations
Step 6: Judge compares implementations against error catalog
Step 7: Creates student assessment based on actual weak model failures
"""

import boto3
import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
import re

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
        """Initialize the corrected 7-step pipeline with timestamped logging"""
        self.aws_region = "us-west-2"
        
        # Model assignments - Updated to use Claude 4 via inference profiles
        # Note: Claude 4 models require inference profile IDs, not direct model IDs
        self.model_opus = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"    # Strong (Judge + Question Gen) - Sonnet 4.5 via inference profile
        self.model_sonnet = "us.anthropic.claude-sonnet-4-20250514-v1:0"    # Mid (Should succeed) - Sonnet 4 via inference profile
        self.model_haiku = "anthropic.claude-3-haiku-20240307-v1:0"         # Weak (Target to fail) - Haiku 3 direct model ID
        
        self.bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=self.aws_region
        )
        
        # Generate timestamped file names for this pipeline run
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = f"logs/current/pipeline_run_{self.run_timestamp}.txt"
        self.results_file = f"corrected_7step_results_{self.run_timestamp}.json"
        
        # Ensure log directories exist
        os.makedirs("logs/current", exist_ok=True)
        os.makedirs("logs/archived", exist_ok=True)
        
        # Initialize database connection
        self.db_path = "pipeline_results.db"
        self._init_database()

        # Step 7 validation configuration
        self.allowed_difficulties = {"Beginner", "Intermediate", "Advanced", "Expert"}
        self.step7_max_attempts = 3
        self.min_code_lines = 24  # keeps the game substantive
        self.max_code_lines = 60
        self.min_errors = 3
        self.max_errors = 5
        self.min_error_span = 20
        self.max_error_span = 120

    def invoke_model(self, model_id: str, prompt: str, max_tokens: int = 2048) -> str:
        """Invoke a model via AWS Bedrock with rate limiting"""
        import time
        time.sleep(1)  # Rate limiting
        
        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType='application/json',
                accept='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            
            if 'content' in response_body and len(response_body['content']) > 0:
                return response_body['content'][0]['text']
            else:
                return "Error: No content generated."
                
        except Exception as e:
            if "ThrottlingException" in str(e):
                logger.warning(f"Rate limited, waiting 10 seconds...")
                time.sleep(10)
                return self.invoke_model(model_id, prompt, max_tokens)  # Retry once
            else:
                logger.error(f"Bedrock API call failed: {str(e)}")
                return f"Error: {str(e)}"

    def invoke_model_with_tools(self, model_id: str, prompt: str, tools: List[Dict], max_tokens: int = 2048, use_thinking: bool = False, thinking_budget: int = 2048) -> Dict:
        """Invoke a model via AWS Bedrock with tool use for structured output"""
        import time
        time.sleep(1)  # Rate limiting

        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
                "tools": tools,
                "temperature": 0.7,
            }

            # Add thinking mode if requested (for retries on hard questions)
            if use_thinking:
                body["thinking"] = {
                    "type": "enabled",
                    "budget_tokens": thinking_budget
                }
            
            response = self.bedrock_client.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType='application/json',
                accept='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            
            # Extract structured data from tool use
            if 'content' in response_body:
                for content in response_body['content']:
                    if content.get('type') == 'tool_use':
                        return content.get('input', {})
            
            # Fallback - return error if no tool use found
            return {"error": "No tool use found in response"}
                
        except Exception as e:
            if "ThrottlingException" in str(e):
                logger.warning(f"Rate limited, waiting 10 seconds...")
                time.sleep(10)
                return self.invoke_model_with_tools(model_id, prompt, tools, max_tokens)  # Retry once
            else:
                logger.error(f"Bedrock API call with tools failed: {str(e)}")
                return {"error": f"Error: {str(e)}"}

    def log_step(self, step: PipelineStep):
        """Log a pipeline step to both file and database"""
        # Log to timestamped file
        with open(self.log_file, "a") as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"STEP {step.step_number}: {step.step_name}\n")
            f.write(f"MODEL: {step.model_used}\n")
            f.write(f"TIMESTAMP: {step.timestamp}\n")
            f.write(f"SUCCESS: {step.success}\n")
            f.write(f"RESPONSE:\n{step.response}\n")
        
        # Log to database
        self._save_step_to_database(step)

    def _init_database(self):
        """Initialize database with enhanced logging tables"""
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
        
        conn.commit()
        conn.close()

    def _save_step_to_database(self, step: PipelineStep):
        """Save complete step data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO enhanced_step_responses 
            (run_timestamp, topic, step_number, step_name, model_used, success, 
             response_length, full_response, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.run_timestamp,
            getattr(self, 'current_topic', 'Unknown'),
            step.step_number,
            step.step_name,
            step.model_used,
            step.success,
            len(step.response),
            step.response,
            step.timestamp
        ))
        
        conn.commit()
        conn.close()

    def step1_generate_difficulty_categories(self, topic: str) -> Tuple[bool, Dict[str, List[str]], PipelineStep]:
        """Step 1: Generate difficulty categories"""
        prompt = f'''For the topic "{topic}", create exactly 3 difficulty levels with specific subtopic examples.
Focus on creating a progression from basic concepts to advanced domain-specific knowledge.

Please use the difficulty_categories_tool to return the structured data.'''
        
        # Tool schema for structured difficulty categories
        tools = [{
            "name": "difficulty_categories_tool",
            "description": "Returns difficulty categories with subtopics",
            "input_schema": {
                "type": "object",
                "properties": {
                    "Beginner": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of beginner-level subtopics"
                    },
                    "Intermediate": {
                        "type": "array", 
                        "items": {"type": "string"},
                        "description": "List of intermediate-level subtopics"
                    },
                    "Advanced": {
                        "type": "array",
                        "items": {"type": "string"}, 
                        "description": "List of advanced-level subtopics"
                    }
                },
                "required": ["Beginner", "Intermediate", "Advanced"]
            }
        }]
        
        response = self.invoke_model_with_tools(self.model_opus, prompt, tools)
        step = PipelineStep(1, "Generate difficulty categories", self.model_opus, False, str(response), datetime.now().isoformat())
        
        try:
            if isinstance(response, dict) and not 'error' in response:
                categories = response
                step.success = True
            else:
                categories = {}
                step.success = False
            self.log_step(step)
            return step.success, categories, step
        except Exception as e:
            step.success = False
            self.log_step(step)
            return False, {}, step

    def step2_generate_error_catalog(self, topic: str, subtopic: str, difficulty: str) -> Tuple[bool, List[Dict], PipelineStep]:
        """Step 2: Generate conceptual error catalog - patterns that differentiate strong vs weak models"""
        prompt = f'''For the topic "{topic}" at {difficulty} level, specifically "{subtopic}", identify 5-7 common implementation mistakes that create clear differentiation between stronger and weaker AI models.

Focus on conceptual errors where:
- Stronger models (like Haiku 3.5) have the domain knowledge to avoid the mistake
- Weaker models (like Haiku 3) are likely to fall into the trap due to limited domain expertise
- The errors are subtle and domain-specific, not obvious syntax issues

Please use the error_catalog_tool to return the structured data.'''
        
        # Tool schema for structured error catalog
        tools = [{
            "name": "error_catalog_tool",
            "description": "Returns a structured error catalog with implementation mistakes",
            "input_schema": {
                "type": "object",
                "properties": {
                    "errors": {
                        "type": "array",
                        "items": {
                            "type": "object", 
                            "properties": {
                                "mistake": {"type": "string"},
                                "why_wrong": {"type": "string"},
                                "code_pattern": {"type": "string"},
                                "likelihood_strong_avoids": {"type": "number"},
                                "likelihood_weak_makes": {"type": "number"},
                                "domain_specific": {"type": "boolean"},
                                "impact": {"type": "string"}
                            },
                            "required": ["mistake", "why_wrong", "code_pattern", "likelihood_strong_avoids", "likelihood_weak_makes", "domain_specific", "impact"]
                        }
                    }
                },
                "required": ["errors"]
            }
        }]
        
        response = self.invoke_model_with_tools(self.model_opus, prompt, tools)
        step = PipelineStep(2, "Generate conceptual error catalog", self.model_opus, False, str(response), datetime.now().isoformat())
        
        try:
            if isinstance(response, dict) and 'errors' in response:
                error_catalog = response['errors']
            else:
                error_catalog = response  # Fallback
            step.success = True
            self.log_step(step)
            return True, error_catalog, step
        except json.JSONDecodeError:
            step.success = False
            self.log_step(step)
            return False, [], step

    def step3_generate_strategic_question(self, topic: str, subtopic: str, difficulty: str, error_catalog: List[Dict], previous_failures: List[str] = None, use_thinking: bool = False) -> Tuple[bool, Dict, PipelineStep]:
        """Step 3: Generate strategic implementation challenge (NO pre-embedded errors)"""
        # Build failure feedback section
        failure_feedback = ""
        if previous_failures:
            failure_feedback = f'''
PREVIOUS ATTEMPT FAILURES (adapt strategy):
{chr(10).join(f"- {failure}" for failure in previous_failures)}

STRATEGIC ADJUSTMENTS:
- If "both models succeeded": Make requirements MORE SUBTLE and require deeper domain expertise
- If "neither model succeeded": Clarify requirements while keeping conceptual challenges  
- If "no clear differentiation": Focus on MORE NUANCED domain-specific implementation decisions
'''
        
        # Extract key error patterns from catalog
        error_patterns = []
        for i, error in enumerate(error_catalog[:3]):
            pattern = error.get('mistake', f'Error pattern {i+1}')
            reasoning = error.get('why_wrong', 'Conceptual issue')
            error_patterns.append(f"{pattern}: {reasoning}")
        
        prompt = f'''Create a strategic implementation challenge for "{subtopic}" ({difficulty} level) that naturally exposes these potential failure points:

ERROR PATTERNS TO TEST FOR:
{chr(10).join(f"- {pattern}" for pattern in error_patterns)}
{failure_feedback}
GOAL: Create a realistic implementation task where stronger models naturally avoid these pitfalls, but weaker models are likely to fall into them.

Design an implementation scenario that:
1. Requires genuine {topic} domain expertise to implement optimally
2. Has natural opportunities for weaker models to make the catalog errors
3. Represents a real scenario practitioners encounter
4. Tests conceptual understanding, not documentation lookup
5. Allows both models to provide complete solutions (no hints about errors)

Please use the strategic_question_tool to return the structured data.'''
        
        # Tool schema for structured strategic question
        tools = [{
            "name": "strategic_question_tool", 
            "description": "Returns a strategic implementation challenge",
            "input_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Implementation challenge title"},
                    "question_text": {"type": "string", "description": "Clear implementation task description"},
                    "context": {"type": "string", "description": "Realistic business/technical scenario"},
                    "requirements": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of specific functional requirements"
                    },
                    "success_criteria": {"type": "string", "description": "How to evaluate implementation correctness"},
                    "target_error_patterns": {
                        "type": "array", 
                        "items": {"type": "string"},
                        "description": "Error patterns this question targets"
                    }
                },
                "required": ["title", "question_text", "context", "requirements", "success_criteria"]
            }
        }]
        
        response = self.invoke_model_with_tools(self.model_opus, prompt, tools, use_thinking=use_thinking, thinking_budget=2048)
        step = PipelineStep(3, "Generate strategic implementation challenge", self.model_opus, False, str(response), datetime.now().isoformat())
        
        try:
            if isinstance(response, dict) and not 'error' in response:
                question = response
                # Success if we have basic structure (no pre-embedded error requirement)
                step.success = bool(question.get("question_text") and question.get("requirements"))
            else:
                question = {}
                step.success = False
            self.log_step(step)
            return step.success, question, step
        except Exception as e:
            step.success = False
            self.log_step(step)
            return False, {}, step

    def step4_test_sonnet(self, question: Dict) -> Tuple[bool, str, PipelineStep]:
        """Step 4: Test Sonnet (Haiku 3.5) implementation response"""
        prompt = f'''You are a {question.get('context', 'software engineering')} expert. Implement the following:

TASK: {question.get('title', 'Implementation Challenge')}
DESCRIPTION: {question.get('question_text', '')}
CONTEXT: {question.get('context', '')}

REQUIREMENTS:
{chr(10).join(f"- {req}" for req in question.get('requirements', []))}

SUCCESS CRITERIA: {question.get('success_criteria', 'Working, production-ready implementation')}

Provide:
1. IMPLEMENTATION: [Your complete code implementation]
2. EXPLANATION: [2-3 sentences explaining your key design decisions]
3. CONSIDERATIONS: [Any important production considerations]

Format your response clearly with these three sections.'''
        
        response = self.invoke_model(self.model_sonnet, prompt)
        step = PipelineStep(4, "Test Sonnet (mid-tier) implementation", self.model_sonnet, True, response, datetime.now().isoformat())
        
        self.log_step(step)
        return True, response, step

    def step5_test_haiku(self, question: Dict) -> Tuple[bool, str, PipelineStep]:
        """Step 5: Test Haiku (Haiku 3) implementation response"""
        prompt = f'''You are a {question.get('context', 'software engineering')} expert. Implement the following:

TASK: {question.get('title', 'Implementation Challenge')}
DESCRIPTION: {question.get('question_text', '')}
CONTEXT: {question.get('context', '')}

REQUIREMENTS:
{chr(10).join(f"- {req}" for req in question.get('requirements', []))}

SUCCESS CRITERIA: {question.get('success_criteria', 'Working, production-ready implementation')}

Provide:
1. IMPLEMENTATION: [Your complete code implementation]
2. EXPLANATION: [2-3 sentences explaining your key design decisions]
3. CONSIDERATIONS: [Any important production considerations]

Format your response clearly with these three sections.'''
        
        response = self.invoke_model(self.model_haiku, prompt)
        step = PipelineStep(5, "Test Haiku (weak-tier) implementation", self.model_haiku, True, response, datetime.now().isoformat())
        
        self.log_step(step)
        return True, response, step

    def step6_judge_responses(self, question: Dict, sonnet_response: str, haiku_response: str, error_catalog: List[Dict]) -> Tuple[bool, str, List[str], PipelineStep]:
        """Step 6: Judge if differentiation was achieved by comparing implementations against error catalog"""
        
        # Format error catalog for judge
        error_patterns_text = ""
        for i, error in enumerate(error_catalog[:3], 1):
            error_patterns_text += f"\n{i}. {error.get('mistake', 'Unknown error')}\n   Why problematic: {error.get('why_wrong', 'Issues not specified')}\n   Code pattern: {error.get('code_pattern', 'Not specified')}"
        
        prompt = f'''You are evaluating two AI model implementations of the same task to determine if there is clear differentiation in domain expertise.

ORIGINAL TASK:
{question.get('question_text', '')}
Context: {question.get('context', '')}
Requirements: {', '.join(question.get('requirements', []))}

KNOWN ERROR PATTERNS FOR THIS DOMAIN:
{error_patterns_text}

IMPLEMENTATION A (Haiku 3.5 - should be stronger):
{sonnet_response}

IMPLEMENTATION B (Haiku 3 - should be weaker):  
{haiku_response}

EVALUATION CRITERIA:
1. Does Implementation A show better domain expertise than Implementation B?
2. Does Implementation B fall into any of the known error patterns while A avoids them?
3. Is there clear differentiation in solution quality and domain understanding?
4. Would this question effectively distinguish between stronger and weaker models?

Provide your judgment:
DIFFERENTIATION_ACHIEVED: [YES/NO]
QUALITY_SCORE: [1-10 scale where 10 = perfect differentiation]
SONNET_QUALITY: [Brief assessment of Implementation A strengths/weaknesses]
HAIKU_QUALITY: [Brief assessment of Implementation B strengths/weaknesses] 
HAIKU_FAILURES: [List specific errors/weaknesses in Implementation B that Implementation A avoided]
REASONING: [2-3 sentences explaining your differentiation assessment]

If DIFFERENTIATION_ACHIEVED is NO, the pipeline will retry with a refined question.'''
        
        response = self.invoke_model(self.model_opus, prompt)
        step = PipelineStep(6, "Judge implementation differentiation", self.model_opus, False, response, datetime.now().isoformat())
        
        # Check if differentiation was achieved
        success = "DIFFERENTIATION_ACHIEVED: YES" in response.upper()
        
        # Extract Haiku failures for Step 7
        haiku_failures = []
        try:
            if "HAIKU_FAILURES:" in response:
                failures_section = response.split("HAIKU_FAILURES:")[1].split("REASONING:")[0].strip()
                # Extract bullet points or numbered items
                import re
                failure_items = re.findall(r'[•\-\*\d\.]\s*([^\n\r]+)', failures_section)
                haiku_failures = [item.strip() for item in failure_items if item.strip()]
        except:
            haiku_failures = ["General implementation weaknesses compared to stronger model"]
        
        step.success = success
        self.log_step(step)
        return success, response, haiku_failures, step

    def _build_step7_prompt(
        self,
        topic: str,
        subtopic: str,
        haiku_failures: List[str],
        haiku_response: str,
        sonnet_response: str,
        validation_feedback: Optional[List[str]] = None
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Compose the Step 7 prompt (optionally injecting feedback from validation failures)."""

        feedback_block = ""
        if validation_feedback:
            feedback_lines = "\n".join(f"- {issue}" for issue in validation_feedback)
            feedback_block = f"""

VALIDATION FEEDBACK FROM THE LAST ATTEMPT:
Fix every issue below before returning the next result:
{feedback_lines}
"""

        prompt = f'''You will create a single interactive error-spotting game question for students to review code.

The weak model (Haiku) made these conceptual errors that the strong model (Sonnet) avoided:
{chr(10).join(f"- {failure}" for failure in haiku_failures)}

WEAK MODEL'S BUGGY IMPLEMENTATION (use this as your source):
{haiku_response[:2000]}

STRONG MODEL'S CORRECT APPROACH (for reference only):
{sonnet_response[:1000]}

YOUR TASK:
Create a game question by extracting the BUGGY code from the weak model's response and marking the errors with << >> delimiters.

STRICT VALIDATION RULES (these are enforced automatically):
1. Code must be a COMPLETE, runnable snippet between {self.min_code_lines} and {self.max_code_lines} lines.
   - Include necessary imports / context (class/function wrappers, helper comments).
2. Mark errors with << >> delimiters INLINE in code.
   - Each marked segment must be between {self.min_error_span} and {self.max_error_span} characters.
   - There must be between {self.min_errors} and {self.max_errors} errors.
   - Every error must be conceptual/algorithmic (no typos or stylistic nits).
3. Error IDs must match EXACTLY what appears between << >> in the code, character-for-character.
   - If an ID appears twice or is missing from the code, the output will be rejected.
4. Each error description must be 1-2 sentences (< 150 characters) explaining why it's wrong and what to do instead.
5. Use only straight quotes (" '), no curly quotes.
6. Difficulty must be one of: {", ".join(sorted(self.allowed_difficulties))}.
7. Return ONLY valid JSON via the tool — no plain text.

Topic: {topic}
Subtopic: {subtopic}

Target pitfalls to encode (do NOT name these in code, just mark where they occur):
{chr(10).join(f"- {failure[:200]}" for failure in haiku_failures[:5])}
{feedback_block}'''

        tools = [{
            "name": "student_assessment_tool",
            "description": "Returns a code review game question with inline error markup for interactive UI",
            "input_schema": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Concise, descriptive title describing the implementation (e.g., 'Group-Relative Reward Processing for Multi-Task RL')"
                    },
                    "difficulty": {
                        "type": "string",
                        "enum": list(self.allowed_difficulties),
                        "description": "Difficulty level based on domain expertise required"
                    },
                    "code": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Array of code lines (must include imports and context). Mark errors inline with <<error_substring>>."
                    },
                    "errors": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "string",
                                    "description": "EXACT text between << >> delimiters (character-for-character match)."
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Concise explanation (1-2 sentences, under 150 chars) of WHY it's wrong and what the correct approach should be."
                                }
                            },
                            "required": ["id", "description"]
                        },
                        "description": "3-5 conceptual/algorithmic errors (not typos) with matching IDs from the code"
                    }
                },
                "required": ["title", "difficulty", "code", "errors"]
            }
        }]

        return prompt, tools

    def _validate_assessment_payload(self, payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
        """Run deterministic checks to ensure Step 7 output matches frontend expectations."""
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

        code_lines = payload.get("code")
        if not isinstance(code_lines, list) or not all(isinstance(line, str) for line in code_lines):
            errors.append("Code must be an array of strings.")
            code_lines = []
        else:
            code_lines = [line.rstrip("\r\n") for line in code_lines]
            if not (self.min_code_lines <= len(code_lines) <= self.max_code_lines):
                errors.append(f"Code must contain between {self.min_code_lines} and {self.max_code_lines} lines (found {len(code_lines)}).")

        errors_list = payload.get("errors")
        if not isinstance(errors_list, list) or not all(isinstance(item, dict) for item in (errors_list or [])):
            errors.append("Errors must be an array of objects.")
            errors_list = []

        if errors_list and not (self.min_errors <= len(errors_list) <= self.max_errors):
            errors.append(f"Errors array must contain between {self.min_errors} and {self.max_errors} entries (found {len(errors_list)}).")

        joined_code = "\n".join(code_lines)
        marked_spans = re.findall(r"<<([^<>]+)>>", joined_code)

        if not marked_spans:
            errors.append("No << >> error spans were found in the code.")

        # Ensure raw delimiter counts are balanced
        if joined_code.count("<<") != joined_code.count(">>"):
            errors.append("Unbalanced number of << and >> delimiters in the code.")

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

            occurrences = joined_code.count(f"<<{error_id}>>")
            if occurrences != 1:
                errors.append(f"Error id '{error_id}' must appear exactly once in the code; found {occurrences}.")

            if error_id not in marked_spans:
                errors.append(f"Error id '{error_id}' is not wrapped in << >> within the code.")

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
            "code": code_lines,
            "errors": sanitized_errors
        }

        return True, sanitized_payload, []

    def step7_create_student_assessment(self, question: Dict, sonnet_response: str, haiku_response: str, haiku_failures: List[str], judge_response: str) -> Tuple[bool, Dict, PipelineStep]:
        """Step 7: Create student assessment with error spans based on actual weak model failures"""

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

            response = self.invoke_model_with_tools(self.model_opus, prompt, tools)
            step = PipelineStep(
                7,
                f"Create student assessment from weak model failures (attempt {attempt})",
                self.model_opus,
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

            is_valid, sanitized_payload, validation_errors = self._validate_assessment_payload(response)

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

        # If we exhaust retries, return failure with the last logged step
        if last_step is None:
            last_step = PipelineStep(
                7,
                "Create student assessment from weak model failures",
                self.model_opus,
                False,
                json.dumps({"validation_errors": validation_feedback or ["Unknown Step 7 failure."]}),
                datetime.now().isoformat()
            )
            self.log_step(last_step)

        return False, {}, last_step

    def run_full_pipeline(self, topic: str, max_attempts: int = 3) -> SevenStepResult:
        """Run the complete corrected 7-step pipeline"""
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
        success, categories, step1 = self.step1_generate_difficulty_categories(topic)
        steps_completed.append(step1)
        
        if not success:
            return SevenStepResult(topic, "", "", steps_completed, False, 1, False, False, 1, [])
        
        # Select intermediate subtopic for testing
        subtopic = categories.get("Intermediate", ["General concepts"])[0]
        difficulty = "Intermediate"
        
        # Step 2: Generate error catalog (run once)
        success, error_catalog, step2 = self.step2_generate_error_catalog(topic, subtopic, difficulty)
        steps_completed.append(step2)
        if not success:
            return SevenStepResult(topic, subtopic, difficulty, steps_completed, False, 2, False, False, 1, [])
        
        # Retry loop for steps 3-6 (strategic question → implementation testing → differentiation judgment)
        previous_failures = []
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Strategic differentiation attempt {attempt} for {topic}")
            attempt_steps = []

            # Enable thinking mode on retries (need deeper reasoning to craft harder questions)
            use_thinking = (attempt > 1)

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
            differentiation_achieved, judge_response, haiku_failures, step6 = self.step6_judge_responses(
                question, sonnet_response, haiku_response, error_catalog)
            attempt_steps.append(step6)

            steps_completed.extend(attempt_steps)

            if differentiation_achieved:
                logger.info(f"✅ Differentiation achieved on attempt {attempt}")

                # Step 7: Create student assessment based on actual weak model failures
                success, assessment, step7 = self.step7_create_student_assessment(
                    question, sonnet_response, haiku_response, haiku_failures, judge_response)
                steps_completed.append(step7)

                return SevenStepResult(
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
            else:
                logger.info(f"❌ Attempt {attempt} failed differentiation - Step 6 blocked progression")

                # Build detailed failure context for next attempt (includes actual responses)
                failure_summary = {
                    "attempt": attempt,
                    "judge_reasoning": judge_response,
                    "sonnet_preview": sonnet_response[:300] + "..." if len(sonnet_response) > 300 else sonnet_response,
                    "haiku_preview": haiku_response[:300] + "..." if len(haiku_response) > 300 else haiku_response
                }

                # Extract specific failure reason
                if "both models succeeded" in judge_response.lower():
                    failure_text = f"Attempt {attempt}: Both models avoided errors. Sonnet: {failure_summary['sonnet_preview']} | Haiku: {failure_summary['haiku_preview']} | Need MORE SUBTLE conceptual traps"
                elif "neither model succeeded" in judge_response.lower():
                    failure_text = f"Attempt {attempt}: Neither model succeeded. Question may be too ambiguous. Judge said: {judge_response[:200]}"
                else:
                    failure_text = f"Attempt {attempt}: Insufficient differentiation. Judge: {judge_response[:300]}"

                previous_failures.append(failure_text)
        
        # All attempts failed - stopped at Step 6
        return SevenStepResult(
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

    def run_full_pipeline_streaming(self, topic: str, max_attempts: int = 3):
        """
        Generator version of run_full_pipeline that yields each step as it completes.

        This enables real-time streaming via SSE for debugging and progress tracking.

        Yields:
            PipelineStep objects as each step completes

        Final yield contains:
            Dict with final result including all metadata
        """
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
        success, categories, step1 = self.step1_generate_difficulty_categories(topic)
        steps_completed.append(step1)
        yield step1  # ← Yield immediately!

        if not success:
            yield {"final_result": SevenStepResult(topic, "", "", steps_completed, False, 1, False, False, 1, [])}
            return

        # Select intermediate subtopic for testing
        subtopic = categories.get("Intermediate", ["General concepts"])[0]
        difficulty = "Intermediate"

        # Step 2: Generate error catalog
        success, error_catalog, step2 = self.step2_generate_error_catalog(topic, subtopic, difficulty)
        steps_completed.append(step2)
        yield step2  # ← Yield immediately!

        if not success:
            yield {"final_result": SevenStepResult(topic, subtopic, difficulty, steps_completed, False, 2, False, False, 1, [])}
            return

        # Retry loop for steps 3-6
        previous_failures = []
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Strategic differentiation attempt {attempt} for {topic}")
            attempt_steps = []

            # Enable thinking mode on retries
            use_thinking = (attempt > 1)

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
            differentiation_achieved, judge_response, haiku_failures, step6 = self.step6_judge_responses(
                question, sonnet_response, haiku_response, error_catalog)
            attempt_steps.append(step6)
            yield step6  # ← Yield immediately!

            steps_completed.extend(attempt_steps)

            if differentiation_achieved:
                logger.info(f"✅ Differentiation achieved on attempt {attempt}")

                # Step 7: Create student assessment
                success, assessment, step7 = self.step7_create_student_assessment(
                    question, sonnet_response, haiku_response, haiku_failures, judge_response)
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
                yield {"final_result": final_result, "assessment": assessment}
                return
            else:
                logger.info(f"❌ Attempt {attempt} failed differentiation")

                # Build failure context for next attempt
                failure_summary = {
                    "attempt": attempt,
                    "judge_reasoning": judge_response,
                    "sonnet_preview": sonnet_response[:300] + "..." if len(sonnet_response) > 300 else sonnet_response,
                    "haiku_preview": haiku_response[:300] + "..." if len(haiku_response) > 300 else haiku_response
                }

                # Extract specific failure reason
                if "both models succeeded" in judge_response.lower():
                    failure_text = f"Attempt {attempt}: Both models avoided errors. Need MORE SUBTLE conceptual traps"
                elif "neither model succeeded" in judge_response.lower():
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
        yield {"final_result": final_result}

    def run_batch_test(self, topics: List[str]) -> List[SevenStepResult]:
        """Run corrected 7-step pipeline on multiple topics"""
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
        """Save comprehensive results"""
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
                    "opus": self.model_opus,
                    "sonnet": self.model_sonnet,
                    "haiku": self.model_haiku
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
        
        filename = f"backend/corrected_7step_results_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(final_data, f, indent=2)
        
        print(f"\n📊 Results saved to: {filename}")
        print(f"📝 Detailed logs in: {self.log_file}")
        print(f"💾 Full step data stored in database: {self.db_path}")

    def _extract_common_failures(self, results: List[SevenStepResult]) -> Dict[str, int]:
        """Extract common patterns from weak model failures"""
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
    """Run corrected 7-step pipeline test"""
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
    
    print(f"\n🏆 CORRECTED PIPELINE RESULTS")
    print(f"Topics with successful differentiation: {successful}/{len(results)}")
    print(f"Topics stopped at Step 6 (no differentiation): {stopped_at_6}/{len(results)}")
    print(f"Step 6 blocking rate: {(stopped_at_6/len(results))*100:.1f}%")
    
    # Show common failure patterns
    if results:
        common_failures = pipeline._extract_common_failures(results)
        if common_failures:
            print(f"\n📊 Common Weak Model Failure Patterns:")
            for failure, count in common_failures.items():
                print(f"  {count}x: {failure}")

if __name__ == "__main__":
    main()
