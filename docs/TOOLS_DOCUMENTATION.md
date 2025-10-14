# 🛠️ Claude API Tools Documentation

## Overview
This document describes the structured output tools used in the 7-step adversarial pipeline. These tools ensure Claude returns properly formatted JSON responses for each pipeline step.

---

## 🔧 Tool Implementation

### Location
**File**: `backend/corrected_7step_pipeline.py`
**Method**: `invoke_model_with_tools()` (lines 109-149)

### How It Works
```python
def invoke_model_with_tools(self, model_id: str, prompt: str, tools: List[Dict], max_tokens: int = 2048) -> Dict:
    """
    Invoke a model via AWS Bedrock with tool use for structured output

    The model is provided with:
    1. A prompt describing the task
    2. A list of tool schemas defining expected output structure
    3. The model responds by "calling" the tool with properly structured data
    """
```

**Key Concept**: Tools in Claude's API act as **structured output schemas**. When given a tool definition, Claude responds by providing data that matches the tool's input schema, ensuring consistent JSON formatting.

---

## 📋 Tools Used in Pipeline

### 1️⃣ `difficulty_categories_tool`

**Step**: 1 - Generate Difficulty Categories
**File Location**: `corrected_7step_pipeline.py:237-261`
**Model**: Opus (Claude 3.5 Sonnet v2)

**Purpose**: Categorize topics into 3 difficulty levels with specific subtopics

**Schema**:
```json
{
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
}
```

**Example Output**:
```json
{
  "Beginner": [
    "Basic fine-tuning concepts",
    "Supervised fine-tuning (SFT)",
    "Dataset preparation"
  ],
  "Intermediate": [
    "RLHF pipeline design",
    "DPO vs PPO trade-offs",
    "Preference data curation"
  ],
  "Advanced": [
    "Multi-stage optimization",
    "Constitutional AI",
    "RLAIF and iterative refinement"
  ]
}
```

---

### 2️⃣ `error_catalog_tool`

**Step**: 2 - Generate Conceptual Error Catalog
**File Location**: `corrected_7step_pipeline.py:291-317`
**Model**: Opus (Claude 3.5 Sonnet v2)

**Purpose**: Identify implementation mistakes that differentiate strong vs weak models

**Schema**:
```json
{
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
          "required": [
            "mistake",
            "why_wrong",
            "code_pattern",
            "likelihood_strong_avoids",
            "likelihood_weak_makes",
            "domain_specific",
            "impact"
          ]
        }
      }
    },
    "required": ["errors"]
  }
}
```

**Example Output**:
```json
{
  "errors": [
    {
      "mistake": "Applying DPO directly to base model",
      "why_wrong": "DPO requires instruction-following capability from SFT first",
      "code_pattern": "DPOTrainer(model=base_model, ...)",
      "likelihood_strong_avoids": 0.9,
      "likelihood_weak_makes": 0.7,
      "domain_specific": true,
      "impact": "Training will fail or produce incoherent outputs"
    }
  ]
}
```

---

### 3️⃣ `strategic_question_tool`

**Step**: 3 - Generate Strategic Implementation Challenge
**File Location**: `corrected_7step_pipeline.py:373-397`
**Model**: Opus (Claude 3.5 Sonnet v2)

**Purpose**: Create implementation tasks that expose error patterns naturally (NO pre-embedded errors)

**Schema**:
```json
{
  "name": "strategic_question_tool",
  "description": "Returns a strategic implementation challenge",
  "input_schema": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "description": "Implementation challenge title"
      },
      "question_text": {
        "type": "string",
        "description": "Clear implementation task description"
      },
      "context": {
        "type": "string",
        "description": "Realistic business/technical scenario"
      },
      "requirements": {
        "type": "array",
        "items": {"type": "string"},
        "description": "List of specific functional requirements"
      },
      "success_criteria": {
        "type": "string",
        "description": "How to evaluate implementation correctness"
      },
      "target_error_patterns": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Error patterns this question targets"
      }
    },
    "required": [
      "title",
      "question_text",
      "context",
      "requirements",
      "success_criteria"
    ]
  }
}
```

**Example Output**:
```json
{
  "title": "RLHF Training Pipeline Implementation",
  "question_text": "Implement a complete RLHF training pipeline for a code generation model using DPO",
  "context": "You're building a code assistant that needs to learn from human preferences",
  "requirements": [
    "Load a pre-trained foundation model",
    "Set up preference dataset",
    "Configure DPO training",
    "Train and save the model"
  ],
  "success_criteria": "Working training pipeline that produces a model fine-tuned on preferences",
  "target_error_patterns": [
    "Applying DPO directly to base model without SFT",
    "Incorrect hyperparameter choices",
    "Missing dataset validation"
  ]
}
```

---

### 4️⃣ `student_assessment_tool`

**Step**: 7 - Create Student Assessment
**File Location**: `corrected_7step_pipeline.py:560-590`
**Model**: Opus (Claude 3.5 Sonnet v2)

**Purpose**: Transform weak model failures into educational assessments with error spans

**Schema**:
```json
{
  "name": "student_assessment_tool",
  "description": "Returns a student assessment with error spans based on weak model failures",
  "input_schema": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "description": "Student assessment title"
      },
      "learning_objective": {
        "type": "string",
        "description": "What students will learn"
      },
      "scenario": {
        "type": "string",
        "description": "Brief context for assessment"
      },
      "code": {
        "type": "string",
        "description": "Code with error span markup"
      },
      "errors": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id": {"type": "string"},
            "description": {"type": "string"},
            "severity": {
              "type": "string",
              "enum": ["high", "medium", "low"]
            },
            "concept": {"type": "string"},
            "learning_value": {"type": "string"},
            "hint": {"type": "string"}
          },
          "required": [
            "id",
            "description",
            "severity",
            "concept",
            "learning_value"
          ]
        }
      },
      "total_errors": {"type": "integer"},
      "estimated_time": {"type": "string"}
    },
    "required": [
      "title",
      "learning_objective",
      "scenario",
      "code",
      "errors",
      "total_errors",
      "estimated_time"
    ]
  }
}
```

**Example Output**:
```json
{
  "title": "RLHF Pipeline Error Detection",
  "learning_objective": "Understand the correct sequence of training steps in RLHF",
  "scenario": "Reviewing an RLHF implementation that has subtle training issues",
  "code": "def implement_rlhf(base_model):\n    [ERROR_1]trainer = DPOTrainer(model=base_model)[/ERROR_1]\n    return trainer.train()",
  "errors": [
    {
      "id": "ERROR_1",
      "description": "Cannot apply DPO to base model - needs SFT first",
      "severity": "high",
      "concept": "training_sequence",
      "learning_value": "Teaches proper RLHF pipeline ordering",
      "hint": "What capability must the model have before preference learning?"
    }
  ],
  "total_errors": 1,
  "estimated_time": "10-15 minutes"
}
```

---

## 🎯 Why Tools Matter

### Without Tools (Text-based responses)
```python
# Inconsistent parsing required
response = model.invoke("Generate difficulty categories...")
# Response might be: "Here are the categories:\n\n**Beginner**\n- Topic 1\n- Topic 2..."
# Requires regex/string parsing, prone to errors
```

### With Tools (Structured responses)
```python
# Guaranteed JSON structure
response = model.invoke_with_tools(prompt, tools=[difficulty_tool])
# Response is always: {"Beginner": [...], "Intermediate": [...], "Advanced": [...]}
# Direct JSON access, no parsing needed
```

### Benefits
1. **Type Safety**: Guaranteed data structure
2. **Validation**: Required fields enforced
3. **Consistency**: Same format every time
4. **Debugging**: Easy to log and inspect
5. **Integration**: Direct use in downstream steps

---

## 🔄 Tool Flow Through Pipeline

```
Step 1: difficulty_categories_tool
   ↓ (provides structured categories)
Step 2: error_catalog_tool
   ↓ (provides error patterns)
Step 3: strategic_question_tool
   ↓ (provides implementation challenge)
Step 4: [No tool - text implementation]
   ↓ (Sonnet provides code)
Step 5: [No tool - text implementation]
   ↓ (Haiku provides code)
Step 6: [No tool - judge compares implementations]
   ↓ (Judge evaluates differentiation)
Step 7: student_assessment_tool
   ↓ (creates final assessment with error spans)
```

**Steps 4-6 don't use tools** because they need free-form code and analysis rather than structured data.

---

## 📚 Related Files

- **Pipeline Implementation**: `backend/corrected_7step_pipeline.py`
- **Streamlit Demo**: `backend/demo_light_app.py`
- **Sample Data (Old Architecture)**: `backend/streamlit_app.py:89-248`

---

## 🔍 How to Find Tool Usage

### Search Pattern
```bash
grep -n "invoke_model_with_tools" backend/*.py
```

### Key Method Signatures
```python
# Method that uses tools
invoke_model_with_tools(model_id, prompt, tools, max_tokens)

# Method without tools (plain text)
invoke_model(model_id, prompt, max_tokens)
```

---

## 💡 Key Insight

**Tools are not functions the model executes** - they're **structured output schemas**. When Claude sees a tool definition, it formats its response as a "tool call" with data matching the schema. This ensures consistent, parseable outputs across all pipeline steps.

This approach is critical for the pipeline because each step depends on structured data from previous steps (e.g., Step 3 needs error patterns from Step 2 in a specific format).