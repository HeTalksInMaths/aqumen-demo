📋 COMPLETE PROMPT ANALYSIS WITH IMPROVEMENTS
STEP 1: DIFFICULTY CATEGORIES (Sonnet)
Current Prompt:
For the topic "{topic}", create exactly 3 difficulty levels with specific subtopic examples.

Focus on creating a progression from basic concepts to advanced domain-specific knowledge.
Ensure each level has concrete, assessable subtopics that can differentiate between skill levels.

Return JSON format:
{
  "Beginner": ["subtopic1", "subtopic2", "subtopic3"],
  "Intermediate": ["subtopic1", "subtopic2", "subtopic3"], 
  "Advanced": ["subtopic1", "subtopic2", "subtopic3"]
}
Expected Response Issues:

Sonnet likely returns generic categories like "Basic X", "Advanced X"
No clear skill differentiation criteria
Subtopics might overlap between levels
Missing context about what makes each level distinct

Improved Prompt:
You are a domain expert in "{topic}". Create 3 difficulty levels that test progressively deeper expertise, not just complexity.

CRITICAL: Each level should test different types of knowledge:
- Beginner: Foundational concepts, basic applications
- Intermediate: Integration skills, common pitfalls, practical implementation  
- Advanced: Edge cases, optimization, research-level understanding

For topic: "{topic}"

Examples of good progression:
- Machine Learning: "Supervised Learning" → "Feature Engineering & Cross-validation" → "Distributed Training & Model Compression" 
- Database Design: "Basic Queries" → "Index Optimization & Transactions" → "Sharding & CAP Theorem Trade-offs"

Return JSON with skill indicators:
{
  "Beginner": {
    "subtopics": ["concept1", "concept2", "concept3"],
    "skill_level": "Recognizes patterns, applies standard methods",
    "time_to_learn": "2-6 months"
  },
  "Intermediate": {
    "subtopics": ["concept1", "concept2", "concept3"], 
    "skill_level": "Integrates concepts, debugs issues, adapts methods",
    "time_to_learn": "6-18 months"
  },
  "Advanced": {
    "subtopics": ["concept1", "concept2", "concept3"],
    "skill_level": "Designs novel solutions, handles edge cases, research-level",
    "time_to_learn": "2+ years"
  }
}
Further Improvements:

Add industry context (startup vs enterprise vs research)
Include specific assessment criteria for each level
Reference real-world complexity indicators


STEP 2: ERROR CATALOG (Opus) - CRITICAL MISSING
Current Prompt:
Generate domain-specific errors
Expected Response Issues:

This is completely broken! Just 31 characters
No structure, format, or guidance
Would return generic list without ranking or context

Improved Prompt:
You are a senior technical interviewer and domain expert in "{subtopic}" at {difficulty_level} level.

Generate a comprehensive catalog of DOMAIN-SPECIFIC conceptual errors that practitioners commonly make in {subtopic}. 

CRITICAL REQUIREMENTS:
1. Focus on CONCEPTUAL/ALGORITHMIC errors, NOT basic programming syntax
2. Errors should be subtle - things that look correct but have domain-specific issues
3. Avoid generic ML errors (data leakage, scaling) unless domain-specific
4. Include production impact and likelihood

For each error provide:
- mistake: Exact conceptual error description
- code_pattern: How this error typically manifests in code/reasoning
- why_wrong: Domain-specific explanation of why it's incorrect
- likelihood: 0.0-1.0 probability of making this error
- impact: Production consequences (performance, correctness, reliability)
- difficulty_to_spot: easy/medium/hard for experts to catch
- common_in: What type of practitioners make this (junior, intermediate, senior)

Return JSON:
{
  "domain": "{subtopic}",
  "difficulty": "{difficulty_level}",
  "errors": [
    {
      "mistake": "Specific conceptual error in {subtopic}",
      "code_pattern": "How it appears in implementation", 
      "why_wrong": "Domain-specific reasoning why it fails",
      "likelihood": 0.8,
      "impact": "Causes X performance degradation in production",
      "difficulty_to_spot": "medium",
      "common_in": "intermediate practitioners"
    }
  ]
}

EXAMPLES for "Reinforcement Learning - Policy Gradients":
- Using undiscounted returns in infinite horizon problems
- Applying policy gradients without variance reduction in high-dimensional action spaces
- Incorrect advantage estimation with function approximation

Generate 5-8 domain-specific errors ranked by likelihood.
Further Improvements:

Add real-world case studies where these errors occurred
Include frequency data from actual codebases/papers
Reference specific research papers or industry incidents


STEP 3: ADVERSARIAL QUESTION (Opus)
Current Prompt:
For the topic "{subtopic}", create a coding/reasoning question that targets these specific conceptual errors:
{conceptualErrors.map(e => `- ${e.description} (likelihood: ${e.likelihood})`).join('\n')}

Create a question that a strong model (Sonnet) would get right but a weak model (Haiku) would make one of these domain-specific errors.

Focus on {subtopic} domain knowledge, not general programming errors.

Return just the question prompt - no code, no answers.
Expected Response Issues:

Opus might still default to generic programming problems
No guidance on question format or complexity
Missing retry strategy context
Could create questions too esoteric for practical assessment

Improved Prompt:
You are an expert in {subtopic} creating an adversarial technical assessment.

CONTEXT: This is attempt #{attempt_number}/5. Previous attempts failed because:
{previous_failure_reasons}

TARGET ERROR: Focus specifically on this error from the catalog:
- Error: {selected_error.mistake}
- Pattern: {selected_error.code_pattern}  
- Why wrong: {selected_error.why_wrong}
- Likelihood: {selected_error.likelihood}

CREATE A QUESTION THAT:
1. Tests {subtopic} domain expertise, NOT general programming
2. Has a subtle flaw that matches the target error pattern
3. Looks correct to non-experts but has the domain-specific issue
4. Is appropriate for {difficulty_level} practitioners
5. Would be solved correctly by an expert but trip up intermediate practitioners

QUESTION FORMAT:
- 20-40 lines of code/pseudocode OR reasoning scenario
- Include realistic context (not toy examples)
- Make the domain-specific error seem reasonable
- Avoid obvious syntax errors or generic mistakes

DIFFICULTY CALIBRATION:
- Beginner: Test fundamental concept application
- Intermediate: Test integration and edge case handling  
- Advanced: Test optimization and research-level understanding

Return only the question prompt without solutions or hints.

ANTI-GENERIC ERROR RULES:
- NO data preprocessing errors (unless domain-specific to {subtopic})
- NO basic syntax or import errors
- NO generic ML pipeline mistakes
- FOCUS on {subtopic}-specific algorithmic/conceptual issues
Further Improvements:

Add specific industry scenarios (e.g., "You're optimizing a recommendation system for 100M users")
Include performance constraints or business requirements
Reference specific tools or frameworks commonly used in the domain


STEP 4/5: MODEL TESTING (Sonnet & Haiku)
Current Prompt:
{question}

Please provide your solution or reasoning.
Expected Response Issues:

Models won't focus on domain-specific aspects
Generic analysis instead of expert-level review
No structured format for comparison
Missing domain context

Improved Prompt:
You are a senior {subtopic} expert conducting a technical code review.

SCENARIO: {question}

Analyze this from a {subtopic} domain expertise perspective, focusing on:

1. ALGORITHMIC CORRECTNESS: Does the approach follow {subtopic} best practices?
2. DOMAIN-SPECIFIC ISSUES: Are there subtle {subtopic} errors that would cause production problems?
3. PERFORMANCE IMPLICATIONS: How would this perform in real-world {subtopic} scenarios?
4. EDGE CASES: What {subtopic}-specific edge cases are not handled?

IGNORE generic programming style, imports, or basic syntax.
FOCUS on {subtopic} domain knowledge and expert-level concerns.

Provide your analysis in this format:
CORRECTNESS: [Correct/Incorrect - domain-specific reasoning]
MAIN ISSUES: [List domain-specific problems, not generic coding issues]
PRODUCTION IMPACT: [Real-world consequences in {subtopic} applications]
RECOMMENDATIONS: [Domain-expert fixes, not generic improvements]
EXPERTISE LEVEL: [What level practitioner would write this code?]

Be specific about {subtopic} concepts and avoid generic software development advice.
Further Improvements:

Add specific performance benchmarks or industry standards
Include compliance or safety requirements for the domain
Reference current research or industry trends


STEP 6: JUDGMENT (Opus)
Current Prompt:
I generated this question to test model capabilities:
QUESTION: {question}

SONNET RESPONSE: {sonnetResponse}

HAIKU RESPONSE: {haikuResponse}

EXPECTED ERRORS (what Haiku should make):
{expectedErrors.map(e => `- ${e.description}`).join('\n')}

Did Sonnet get it right and did Haiku make one of the expected domain-specific errors?

Respond with JSON:
{
  "sonnet_correct": true/false,
  "haiku_made_expected_error": true/false,
  "haiku_error_type": "description of error Haiku made",
  "differentiation_success": true/false,
  "reasoning": "explanation"
}
Expected Response Issues:

Binary success/failure doesn't capture nuanced differences
No confidence scoring or uncertainty handling
Might miss partial success cases
Doesn't validate domain-specificity vs generic errors

Improved Prompt:
You are evaluating an adversarial technical assessment for {subtopic} expertise.

ASSESSMENT QUESTION: {question}

SONNET (Strong Model) RESPONSE: {sonnetResponse}

HAIKU (Weak Model) RESPONSE: {haikuResponse}

TARGETED ERROR CATALOG:
{expectedErrors.map(e => `- ${e.mistake}: ${e.why_wrong} (likelihood: ${e.likelihood})`).join('\n')}

EVALUATION CRITERIA:
1. Did Sonnet demonstrate {subtopic} domain expertise?
2. Did Haiku make a domain-specific error (not generic programming mistakes)?
3. Is there clear differentiation based on {subtopic} knowledge depth?
4. Would this question effectively assess {subtopic} practitioners?

JUDGMENT RUBRIC:
- EXCELLENT: Clear domain expertise difference, Haiku makes predicted error
- GOOD: Some domain differentiation, partial error matching
- FAIR: Generic differentiation, not domain-specific  
- POOR: Both responses similar or both incorrect

Respond with JSON:
{
  "sonnet_analysis": {
    "correct": true/false,
    "domain_expertise_shown": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "Domain-specific analysis"
  },
  "haiku_analysis": {
    "made_expected_error": true/false,
    "error_type": "specific error classification",
    "error_severity": "minor/major/critical",
    "generic_vs_domain": "domain-specific/generic/mixed"
  },
  "differentiation_quality": "excellent/good/fair/poor",
  "assessment_effectiveness": {
    "tests_domain_knowledge": true/false,
    "appropriate_difficulty": true/false,
    "clear_success_criteria": true/false
  },
  "overall_success": true/false,
  "improvement_suggestions": "How to make question better target domain errors",
  "confidence": 0.0-1.0
}
Further Improvements:

Add comparison to industry assessment standards
Include false positive/negative rate analysis
Reference specific competency frameworks


STEP 7: STUDENT QUESTION (Opus)
Current Prompt:
Based on this adversarial testing:

ORIGINAL QUESTION: {originalQuestion}

HAIKU'S RESPONSE: {haikuResponse}

HAIKU'S ERROR TYPE: {haikuErrorType}

Create a student assessment question that embeds Haiku's actual error as a clickable error span.

Requirements:
1. Create code/reasoning that contains the same error Haiku made
2. Mark error spans with <span class="error-span tight" data-error-id="X" data-concept="conceptname">error text</span>
3. Make spans as tight as possible (individual tokens/expressions, not full lines)
4. Include 1-3 errors total, with at least one inspired by Haiku's mistake

Return JSON:
{
  "title": "Assessment Title",
  "code": "Code with error spans marked",
  "errors": [
    {
      "id": "1",
      "description": "What's wrong",
      "severity": "high/medium/trick", 
      "concept": "domain concept",
      "span_tightness": "tight/loose",
      "inspired_by_haiku": true/false
    }
  ]
}
Expected Response Issues:

No pedagogical guidance on learning objectives
Missing difficulty calibration for students vs practitioners
Span tightness might be subjective without clear criteria
Could create overly complex questions for educational use

Improved Prompt:
You are an educational technology expert creating an interactive {subtopic} assessment.

LEARNING CONTEXT:
- Target audience: {difficulty_level} students in {subtopic}
- Learning objective: Identify common {subtopic} conceptual errors
- Assessment type: Interactive error detection with clickable spans

HAIKU'S ACTUAL ERROR:
- Original question: {originalQuestion}
- Haiku's response: {haikuResponse}  
- Error type: {haikuErrorType}
- Why it's wrong: {domain_specific_reasoning}

CREATE AN EDUCATIONAL QUESTION THAT:

1. PEDAGOGICAL DESIGN:
   - Clear learning objective focused on {subtopic} concepts
   - Appropriate cognitive load for {difficulty_level} students
   - Builds on fundamental {subtopic} knowledge
   - Provides teachable moment when error is found

2. ERROR EMBEDDING:
   - Embed Haiku's actual conceptual error in realistic code/scenario
   - Make error subtle but detectable with {subtopic} knowledge
   - Include 1-2 additional errors of varying difficulty (optional "trick" correct sections)

3. SPAN DESIGN:
   - Mark errors with: <span class="error-span tight" data-error-id="X" data-concept="conceptname">exact error token</span>
   - TIGHT spans: Individual variables, operators, function calls (preferred)
   - LOOSE spans: Only when error spans multiple tokens conceptually
   - Each span should be unambiguous - clicking it clearly indicates the specific issue

4. ASSESSMENT QUALITY:
   - Include "trick" sections that are actually correct to test discrimination
   - Vary error severity to assess different skill levels
   - Ensure each error teaches a specific {subtopic} concept

Return JSON:
{
  "title": "Clear assessment title",
  "learning_objective": "What students will learn by finding these errors",
  "difficulty_level": "{difficulty_level}",
  "code": "Code with precisely marked error spans",
  "errors": [
    {
      "id": "1",
      "description": "Student-friendly explanation of what's wrong",
      "severity": "high/medium/low/trick",
      "concept": "Specific {subtopic} concept being tested", 
      "span_tightness": "tight/loose",
      "inspired_by_haiku": true/false,
      "learning_value": "What students learn from finding this error",
      "hint": "Optional hint if error is subtle"
    }
  ],
  "total_errors": 2,
  "estimated_time": "5-10 minutes"
}

SPAN TIGHTNESS EXAMPLES:
- TIGHT: <span>np.argmax</span> (specific function)
- TIGHT: <span>epsilon</span> (specific variable)  
- LOOSE: <span>reward + gamma * max_next_q</span> (conceptual expression)
- AVOID: <span>entire line of code</span>
Further Improvements:

Add adaptive difficulty based on student performance
Include prerequisite knowledge checks
Reference educational standards or learning frameworks
Add analytics for tracking common student mistakes

