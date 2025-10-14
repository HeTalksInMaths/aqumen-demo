# Current 7-Step Pipeline Prompts - Full Extraction

**File**: `corrected_7step_pipeline.py`  
**Date**: 2025-09-14  
**Purpose**: Complete prompt analysis for optimization

---

## **Step 1: Generate Difficulty Categories**

```python
prompt = f'''For the topic "{topic}", create exactly 3 difficulty levels with specific subtopic examples.
Focus on creating a progression from basic concepts to advanced domain-specific knowledge.

Please use the difficulty_categories_tool to return the structured data.'''
```

**Issues Identified:**
- ❌ **Too generic** - no domain-specific guidance
- ❌ **Always assumes 3 levels** - some topics may need different structures
- ❌ **No examples** of what good categories look like

---

## **Step 2: Generate Error Catalog**

```python
prompt = f'''For the topic "{topic}" at {difficulty} level, specifically "{subtopic}", identify 5-7 common implementation mistakes that create clear differentiation between stronger and weaker AI models.

Focus on conceptual errors where:
- Stronger models (like Haiku 3.5) have the domain knowledge to avoid the mistake
- Weaker models (like Haiku 3) are likely to fall into the trap due to limited domain expertise
- The errors are subtle and domain-specific, not obvious syntax issues

Please use the error_catalog_tool to return the structured data.'''
```

**Issues Identified:**
- ✅ **Good differentiation focus**
- ❌ **Always assumes "implementation mistakes"** - not all domains are about coding
- ❌ **No domain adaptation** - math vs business vs coding need different error types
- ❌ **Hard-coded model names** that may become outdated

---

## **Step 3: Generate Strategic Question**

```python
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
```

**Issues Identified:**
- ❌ **Forces "implementation challenge"** language - wrong for math/theory topics
- ❌ **Assumes coding context** - "implement", "solutions", "practitioners"
- ❌ **No domain type detection** - should adapt language per domain
- ✅ **Good error pattern integration**

---

## **Step 4: Test Strong Model (Sonnet)**

```python
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
```

**Issues Identified:**
- ❌ **Hard-coded "software engineering"** default context
- ❌ **Forces code "implementation"** format even for non-coding topics
- ❌ **"Production-ready"** irrelevant for math/theory problems
- ❌ **Fixed 3-section format** doesn't work for all domains

---

## **Step 5: Test Weak Model (Haiku)**

```python
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
```

**Issues Identified:**
- ❌ **Identical to Step 4** - should be the same for fair comparison, but...
- ❌ **Same coding assumptions** as Step 4
- ❌ **No domain adaptation** for mathematical proofs, business scenarios, etc.

---

## **Step 6: Judge Differentiation**

```python
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
```

**Issues Identified:**
- ✅ **Good structured output format**
- ❌ **Assumes "implementations"** - wrong for theory/math/business domains
- ❌ **Model name confusion** - says "Haiku 3.5" for Implementation A but it's actually Sonnet
- ✅ **Good error pattern integration**
- ✅ **Clear decision criteria**

---

## **Step 7: Student Assessment Creation**

```python
prompt = f'''Based on the successful model differentiation, create an educational assessment for students.

ORIGINAL IMPLEMENTATION TASK:
{question.get('question_text', '')}

STRONG MODEL IMPLEMENTATION (Reference):
{sonnet_response}

WEAK MODEL IMPLEMENTATION (With Issues):
{haiku_response}

IDENTIFIED WEAK MODEL FAILURES:
{chr(10).join(f"- {failure}" for failure in haiku_failures)}

JUDGE EVALUATION:
{judge_response}

Create a student assessment that highlights where the weak model went wrong:

1. Extract the key problematic code sections from the weak model implementation
2. Create clickable error spans for interactive learning
3. Provide educational explanations for why each error is problematic
4. Focus on the conceptual understanding gaps, not syntax issues

Please use the student_assessment_tool to return the structured data.'''
```

**Issues Identified:**
- ❌ **Forces "code sections"** - wrong for non-coding domains
- ❌ **Vague "clickable error spans"** instruction
- ❌ **No specific marker format** guidance (causes bracket vs span confusion)
- ❌ **Assumes programming context** throughout
- ✅ **Good focus on conceptual gaps**

---

## 🔍 **Major Pattern Issues Across All Prompts**

### **1. Coding Bias Problem**
- **Issue**: All prompts assume coding/implementation context
- **Impact**: Math topics get forced into code format (like Sylow theorem → Python function)
- **Fix Needed**: Domain-aware prompt templates

### **2. No Domain Detection**
- **Issue**: No logic to detect topic type (math, business, technical, etc.)
- **Impact**: Grammar topics get "implementation challenges", math gets "production code"
- **Fix Needed**: Topic classification system

### **3. Fixed Format Assumptions**
- **Issue**: Hard-coded section structures that don't fit all domains
- **Impact**: Forces inappropriate formats (business writing → code blocks)
- **Fix Needed**: Flexible response formats per domain

### **4. Error Span Generation Unclear**
- **Issue**: Step 7 gives vague instructions about "clickable spans"
- **Impact**: Gets `[error1]` brackets instead of proper HTML spans
- **Fix Needed**: Explicit format specification with examples

### **5. Model Name Inconsistencies**  
- **Issue**: Wrong model names in Step 6 (says Haiku 3.5 for Sonnet responses)
- **Impact**: Confusing judge evaluations
- **Fix Needed**: Correct model identification

---

## 💡 **Key Insights for Optimization**

1. **Domain-Specific Templates Needed**: Math, Business, Technical, Creative domains need different prompt structures
2. **Error Marker Format Critical**: Must specify exact HTML/comment format with examples  
3. **Context Detection Required**: Pipeline should detect topic type and adapt language
4. **Flexible Output Formats**: Not everything should be "implementation" with "code sections"
5. **Consistent Model Naming**: Fix judge evaluation model identification

**Next Steps**: Create domain-aware prompt templates and test with various topic types.