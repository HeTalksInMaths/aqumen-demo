import boto3
import json
import streamlit as st
from typing import Dict, Any, List

# Centralized Bedrock client management
class BedrockClient:
    def __init__(self):
        try:
            aws_access_key = st.secrets["aws"]["AWS_ACCESS_KEY_ID"]
            aws_secret_key = st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"]
            aws_region = st.secrets["aws"].get("AWS_DEFAULT_REGION", "us-east-1")
            
            self.bedrock_client = boto3.client(
                service_name='bedrock-runtime', region_name=aws_region,
                aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key
            )
            self.models = {
                'STRONG': st.secrets["models"]["CLAUDE_OPUS"],
                'MID': st.secrets["models"]["CLAUDE_SONNET"],
                'WEAK': st.secrets["models"]["CLAUDE_HAIKU"]
            }
            self.initialized = True
        except Exception:
            self.initialized = False
            self.bedrock_client = None

    def is_available(self) -> bool:
        return self.initialized

    def invoke_model(self, model_tier: str, prompt: str, max_tokens: int = 4096) -> Dict[str, Any]:
        if not self.is_available():
            raise ConnectionError("Bedrock client not initialized. Check AWS credentials.")
        
        model_id = self.models.get(model_tier)
        if not model_id:
            raise ValueError(f"Invalid model tier: {model_tier}")

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7, "top_p": 0.9
        }
        
        response = self.bedrock_client.invoke_model(
            modelId=model_id, body=json.dumps(body),
            contentType='application/json', accept='application/json'
        )
        response_body = json.loads(response['body'].read())
        
        if 'content' in response_body and len(response_body['content']) > 0:
            text_response = response_body['content'][0]['text']
            return json.loads(text_response)
        raise ValueError("Received an empty or invalid response from the model.")

_bedrock_client = None

def get_bedrock_client() -> BedrockClient:
    global _bedrock_client
    if _bedrock_client is None:
        _bedrock_client = BedrockClient()
    return _bedrock_client

# STEP 1: Difficulty Categories (Sonnet)
def generate_difficulty_levels(topic: str) -> Dict[str, Any]:
    client = get_bedrock_client()
    prompt = f"""You are a domain expert in "{topic}". Create 3 difficulty levels that test progressively deeper expertise, not just complexity.

CRITICAL: Each level should test different types of knowledge:
- Beginner: Foundational concepts, basic applications
- Intermediate: Integration skills, common pitfalls, practical implementation
- Advanced: Edge cases, optimization, research-level understanding

For topic: "{topic}"

Return JSON with skill indicators:
{{
  "Beginner": {{ "subtopics": ["..."], "skill_level": "...", "time_to_learn": "..." }},
  "Intermediate": {{ "subtopics": ["..."], "skill_level": "...", "time_to_learn": "..." }},
  "Advanced": {{ "subtopics": ["..."], "skill_level": "...", "time_to_learn": "..." }}
}}"""
    return client.invoke_model('MID', prompt)

# STEP 2: Error Catalog (Opus)
def generate_error_catalog(subtopic: str, difficulty_level: str) -> Dict[str, Any]:
    client = get_bedrock_client()
    prompt = f"""You are a senior technical interviewer and domain expert in "{subtopic}" at {difficulty_level} level. Generate a comprehensive catalog of DOMAIN-SPECIFIC conceptual errors.

CRITICAL REQUIREMENTS:
1. Focus on CONCEPTUAL/ALGORITHMIC errors, NOT basic syntax.
2. Errors should be subtle - things that look correct but have domain-specific issues.
3. Include production impact and likelihood.

Return JSON:
{{
  "domain": "{subtopic}",
  "difficulty": "{difficulty_level}",
  "errors": [
    {{
      "mistake": "Specific conceptual error",
      "code_pattern": "How it appears in implementation",
      "why_wrong": "Domain-specific reasoning",
      "likelihood": 0.8,
      "impact": "Production consequences",
      "difficulty_to_spot": "medium",
      "common_in": "intermediate"
    }}
  ]
}}
Generate 5-8 domain-specific errors ranked by likelihood."""
    return client.invoke_model('STRONG', prompt)

# STEP 3: Adversarial Question (Opus)
def generate_adversarial_question(subtopic: str, difficulty_level: str, selected_error: Dict[str, Any], attempt_number: int, previous_failure_reasons: str) -> Dict[str, Any]:
    client = get_bedrock_client()
    prompt = f"""You are an expert in {subtopic} creating an adversarial technical assessment.

CONTEXT: This is attempt #{attempt_number}/5. Previous attempts failed because: {previous_failure_reasons}

TARGET ERROR: Focus specifically on this error:
- Error: {selected_error.get('mistake')}
- Pattern: {selected_error.get('code_pattern')}
- Why wrong: {selected_error.get('why_wrong')}

CREATE A QUESTION THAT:
1. Tests {subtopic} domain expertise, NOT general programming.
2. Has a subtle flaw that matches the target error pattern.
3. Is appropriate for {difficulty_level} practitioners.

Return only the question prompt as a JSON object: {{"question": "Your generated question here..."}}"""
    return client.invoke_model('STRONG', prompt)

# STEP 4/5: Model Testing (Sonnet & Haiku)
def test_model(model_tier: str, subtopic: str, question: str) -> Dict[str, Any]:
    client = get_bedrock_client()
    prompt = f"""You are a senior {subtopic} expert conducting a technical code review.

SCENARIO: {question}

Analyze this from a {subtopic} domain expertise perspective, focusing on:
1. ALGORITHMIC CORRECTNESS: Does it follow {subtopic} best practices?
2. DOMAIN-SPECIFIC ISSUES: Are there subtle {subtopic} errors?
3. PERFORMANCE IMPLICATIONS: How would this perform in real-world scenarios?
4. EDGE CASES: What {subtopic}-specific edge cases are not handled?

Provide your analysis in this JSON format:
{{
  "correctness": "[Correct/Incorrect - reasoning]",
  "main_issues": "[List domain-specific problems]",
  "production_impact": "[Real-world consequences]",
  "recommendations": "[Domain-expert fixes]",
  "expertise_level": "[What level practitioner would write this?]"
}}"""
    return client.invoke_model(model_tier, prompt)

# STEP 6: Judgment (Opus)
def judge_responses(subtopic: str, question: str, sonnet_response: Dict[str, Any], haiku_response: Dict[str, Any], expected_errors: List[Dict[str, Any]]) -> Dict[str, Any]:
    client = get_bedrock_client()
    expected_errors_str = json.dumps(expected_errors, indent=2)
    prompt = f"""You are evaluating an adversarial technical assessment for {subtopic} expertise.

ASSESSMENT QUESTION: {question}
SONNET (Strong Model) RESPONSE: {json.dumps(sonnet_response)}
HAIKU (Weak Model) RESPONSE: {json.dumps(haiku_response)}
TARGETED ERROR CATALOG: {expected_errors_str}

EVALUATION CRITERIA:
1. Did Sonnet demonstrate {subtopic} domain expertise?
2. Did Haiku make a domain-specific error?
3. Is there clear differentiation based on {subtopic} knowledge depth?

Return JSON with confidence scores:
{{
  "sonnet_analysis": {{ "correct": true/false, "domain_expertise_shown": true/false, "confidence": 0.0-1.0, "reasoning": "..." }},
  "haiku_analysis": {{ "made_expected_error": true/false, "error_type": "...", "error_severity": "...", "generic_vs_domain": "..." }},
  "differentiation_quality": "excellent/good/fair/poor",
  "assessment_effectiveness": {{ "tests_domain_knowledge": true/false, "appropriate_difficulty": true/false }},
  "overall_success": true/false,
  "improvement_suggestions": "...",
  "confidence": 0.0-1.0
}}"""
    return client.invoke_model('STRONG', prompt)

# STEP 7: Student Question (Opus)
def create_student_assessment(subtopic: str, difficulty_level: str, original_question: str, haiku_response: Dict[str, Any], haiku_error_type: str, domain_reasoning: str) -> Dict[str, Any]:
    client = get_bedrock_client()
    prompt = f"""You are an educational technology expert creating an interactive {subtopic} assessment.

LEARNING CONTEXT:
- Target audience: {difficulty_level} students in {subtopic}
- Learning objective: Identify common {subtopic} conceptual errors
- Haiku's error: {haiku_error_type} ({domain_reasoning})

CREATE AN EDUCATIONAL QUESTION THAT:
1. Embeds Haiku's actual conceptual error in a realistic code/scenario.
2. Marks error spans with <span class="error-span tight" data-error-id="X" data-concept="...">error text</span>.
3. Makes spans as TIGHT as possible (individual tokens/expressions).
4. Includes 1-3 errors total (including Haiku's).

Return JSON:
{{
  "title": "Assessment Title",
  "learning_objective": "What students will learn",
  "difficulty_level": "{difficulty_level}",
  "code": "Code with <span ...>marked spans</span>",
  "errors": [
    {{
      "id": "1",
      "description": "Student-friendly explanation",
      "severity": "high/medium/low/trick",
      "concept": "Specific {subtopic} concept",
      "span_tightness": "tight/loose",
      "inspired_by_haiku": true/false,
      "learning_value": "What students learn from this error"
    }}
  ],
  "total_errors": 2,
  "estimated_time": "5-10 minutes"
}}"""
    return client.invoke_model('STRONG', prompt)