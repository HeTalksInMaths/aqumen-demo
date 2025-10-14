# Frontend Integration Guide

## Overview
This document explains how to integrate the adversarial question generation pipeline output with the React frontend deployed at https://demo.aqumen.ai

## Repository Structure

### Frontend Repository
- **Location**: https://github.com/HeTalksInMaths/aqumen-demo (main branch)
- **Deployment**: Vercel → https://demo.aqumen.ai
- **Framework**: React 18 + Vite + Tailwind CSS v4
- **Main Files**:
  - `src/App.jsx` - Single component with all game logic
  - `src/main.jsx` - React initialization
  - `src/index.css` - Tailwind styles

### Backend Pipeline
- **Location**: `/Users/hetalksinmaths/adversarial demo/backend/corrected_7step_pipeline.py`
- **Output**: Step 7 generates student assessment questions in JSON format

---

## Data Format Comparison

### Frontend Expected Format (from App.jsx, lines 15-229)

```javascript
{
  title: "Transformer Attention Implementation",
  difficulty: "Intermediate",  // "Beginner" | "Intermediate" | "Advanced" | "Expert"
  code: [
    "def attention(query, key, value, mask=None):",
    "    d_k = query.size(-1)",
    "    scores = torch.matmul(query, key.transpose(-2, -1)) / <<math.sqrt(d_k)>>",
    "    ",
    "    if mask is not None:",
    "        scores = scores.masked_fill(<<mask == 0>>, -1e9)",
    "    ",
    "    attention_weights = F.softmax(scores, dim=-1)",
    "    return torch.matmul(attention_weights, value), attention_weights"
  ],
  errors: [
    {
      id: "math.sqrt(d_k)",
      description: "Should check if d_k > 0 before taking sqrt to avoid potential domain errors"
    },
    {
      id: "mask == 0",
      description: "Mask logic is inverted - should mask where mask == 1 (padding tokens), not mask == 0"
    }
  ]
}
```

**Key Requirements**:
1. **Error Markup**: Code segments wrapped in `<<error_text>>` delimiters
2. **Error IDs**: Must match EXACTLY the text between delimiters (character-for-character)
3. **Code Length**: 8-40 lines typical (can be shorter for simple examples)
4. **Code Completeness**: Should be runnable with imports, class/function definitions
5. **Error Count**: 1-5 errors per question (most have 2-3)
6. **Description Length**: Concise, 1-2 sentences

### Current Pipeline Output (from step7_new_format.json)

```json
{
  "title": "Group-Relative Reward Processing in Multi-Task RL",
  "difficulty": "Advanced",
  "code": [
    "def process_trajectories(self, trajectories):",
    "    group_relative_rewards = []",
    "    advantages = []",
    "",
    "    for trajectory in trajectories:",
    "        group_id = trajectory['group_id']",
    "        rewards = trajectory['rewards']",
    "        ",
    "        # Compute group-relative rewards",
    "        group_mean = self.group_rewards[group_id]",
    "        <<group_std = self.group_rewards[group_id] / self.group_sizes[group_id]**0.5>>",
    "        <<group_relative_reward = (rewards - group_mean) / group_std>>",
    "        group_relative_rewards.append(group_relative_reward)",
    "        ",
    "        # Compute advantages using GAE",
    "        last_gae = 0",
    "        trajectory_advantages = []",
    "        for reward, next_value in zip(reversed(rewards), reversed(trajectory['values'][1:])):",
    "            <<delta = reward + self.gamma * next_value - trajectory['values'][-1]>>",
    "            last_gae = delta + self.gamma * self.gae_lambda * last_gae",
    "            trajectory_advantages.insert(0, last_gae)",
    "        advantages.append(trajectory_advantages)",
    "",
    "    return {'group_relative_rewards': group_relative_rewards, 'advantages': advantages}"
  ],
  "errors": [
    {
      "id": "group_std = self.group_rewards[group_id] / self.group_sizes[group_id]**0.5",
      "description": "Uses group mean divided by sqrt(size) as standard deviation, which is mathematically invalid. Should compute actual std from reward distribution within the group."
    },
    {
      "id": "group_relative_reward = (rewards - group_mean) / group_std",
      "description": "Transforms raw rewards before GAE computation, corrupting temporal credit assignment. Should normalize advantages after GAE, not raw rewards."
    },
    {
      "id": "delta = reward + self.gamma * next_value - trajectory['values'][-1]",
      "description": "Uses final value ([-1]) for all timesteps instead of current value at index i. This breaks the TD error calculation needed for proper GAE."
    }
  ]
}
```

---

## ✅ Format Compatibility Analysis

### Matching Fields
- ✅ `title` - Direct match
- ✅ `difficulty` - Direct match (same enum values)
- ✅ `code` - Array of strings with `<<>>` delimiters
- ✅ `errors[].id` - Matches delimited text
- ✅ `errors[].description` - Direct match

### Current Status: **100% COMPATIBLE!** 🎉

The pipeline output format **already matches** the frontend requirements perfectly. No conversion needed!

---

## Frontend Parsing Logic (App.jsx lines 237-275)

The frontend automatically parses the `<<>>` delimiters:

```javascript
const parseQuestion = (question) => {
  const parsedLines = [];
  const errorPositions = [];

  question.code.forEach((line, lineIndex) => {
    // Find all delimited sections: <<error_text>>
    const delimiterRegex = /<<([^>]+)>>/g;
    let match;

    while ((match = delimiterRegex.exec(line)) !== null) {
      const errorText = match[1];  // Extract text between << >>
      const startPos = match.index;
      const endPos = startPos + errorText.length;

      errorPositions.push({
        line: lineIndex,
        startPos,
        endPos,
        text: errorText,
        id: errorText  // ID is the delimited text
      });
    }

    // Remove delimiters for display
    cleanLine = line.replace(/<<([^>]+)>>/g, '$1');
    parsedLines.push(cleanLine);
  });

  return {
    ...question,
    parsedCode: parsedLines,       // Code without delimiters
    errorPositions                  // Clickable error locations
  };
};
```

**Process**:
1. Scans each line for `<<text>>` patterns
2. Extracts error positions and text
3. Removes delimiters for display
4. Creates clickable segments based on error positions

---

## Integration Steps

### Option 1: Direct Replacement (Simplest)

Replace the hardcoded `rawQuestions` array in `src/App.jsx` (lines 15-229) with JSON exported from the pipeline:

1. **Generate questions** using the pipeline:
   ```bash
   cd /Users/hetalksinmaths/adversarial\ demo/backend
   python corrected_7step_pipeline.py
   ```

2. **Export Step 7 outputs** to a JSON array file (need to add export functionality)

3. **Replace hardcoded array** in App.jsx:
   ```javascript
   // OLD (line 15)
   const rawQuestions = [ /* 10 hardcoded questions */ ];

   // NEW
   import generatedQuestions from './data/generated_questions.json';
   const rawQuestions = generatedQuestions;
   ```

4. **Rebuild and deploy**:
   ```bash
   npm run build
   vercel deploy
   ```

### Option 2: Dynamic API (Production-Ready)

Create an API endpoint to serve questions dynamically:

1. **Backend API** (Flask/FastAPI):
   ```python
   @app.get("/api/questions")
   def get_questions():
       # Load from database or generate on-demand
       questions = load_from_db()  # Or run pipeline
       return {"questions": questions}
   ```

2. **Frontend fetch** (replace hardcoded array):
   ```javascript
   const [rawQuestions, setRawQuestions] = useState([]);

   useEffect(() => {
     fetch('https://api.aqumen.ai/questions')
       .then(res => res.json())
       .then(data => setRawQuestions(data.questions));
   }, []);
   ```

3. **Environment-based toggle**:
   ```javascript
   const USE_API = import.meta.env.VITE_USE_API === 'true';

   if (USE_API) {
     // Fetch from API
   } else {
     // Use hardcoded for demo
   }
   ```

### Option 3: Static JSON File (Recommended for MVP)

Export pipeline output to a static JSON file in the frontend repo:

1. **Create export script** (`backend/export_questions.py`):
   ```python
   import json
   from corrected_7step_pipeline import AdversarialPipeline

   # Run pipeline and collect Step 7 outputs
   pipeline = AdversarialPipeline()
   questions = []

   for topic in topics:
       success, output, _ = pipeline.run_full_pipeline(topic)
       if success:
           questions.append(output)

   # Export to frontend repo
   with open('/Users/hetalksinmaths/aqumen-demo-frontend/src/data/generated_questions.json', 'w') as f:
       json.dump(questions, f, indent=2)
   ```

2. **Update frontend** to import from file:
   ```javascript
   import rawQuestionsData from './data/generated_questions.json';
   const rawQuestions = rawQuestionsData;
   ```

3. **Commit and deploy** via git push (auto-deploys on Vercel)

---

## Current Pipeline → Frontend Workflow

### Existing Pipeline Steps (corrected_7step_pipeline.py)

1. **Step 1**: Generate difficulty categories (uses `difficulty_categories_tool`)
2. **Step 2**: Generate common errors (uses `error_catalog_tool`)
3. **Step 3**: Generate strategic question (uses `strategic_question_tool`)
4. **Step 4**: Strong model (Sonnet 4.5) answers question
5. **Step 5**: Mid model (Sonnet 4) answers question
6. **Step 6**: Weak model (Haiku 3) answers question
7. **Step 7**: Judge compares answers and identifies failures
8. **Step 7 (Final)**: Generate student assessment with error markup (uses `student_assessment_tool`)

### What Step 7 Needs (Already Provided!)

Step 7 receives from prior steps:
- `question` - The strategic question from Step 3
- `sonnet_response` - Strong model's correct implementation
- `haiku_response` - Weak model's buggy implementation
- `haiku_failures` - List of conceptual errors Haiku made
- `judge_response` - Judge's analysis

Step 7 prompt (lines 544-589) already instructs the model to:
- ✅ Create complete, runnable code (25-40 lines)
- ✅ Include imports and class definitions
- ✅ Mark errors with `<<>>` delimiters
- ✅ Ensure error IDs match delimited text exactly
- ✅ Generate 3-5 conceptual errors
- ✅ Provide concise descriptions (under 150 chars)

---

## Testing the Integration

### Validation Checklist

Use this to verify pipeline output matches frontend requirements:

```python
def validate_question(question):
    """Validate question format for frontend compatibility"""
    errors = []

    # Required fields
    if 'title' not in question:
        errors.append("Missing 'title' field")
    if 'difficulty' not in question:
        errors.append("Missing 'difficulty' field")
    if question.get('difficulty') not in ['Beginner', 'Intermediate', 'Advanced', 'Expert']:
        errors.append(f"Invalid difficulty: {question.get('difficulty')}")

    # Code validation
    code = question.get('code', [])
    if not isinstance(code, list):
        errors.append("'code' must be an array of strings")
    if len(code) < 5:
        errors.append(f"Code too short ({len(code)} lines, need 5+)")

    # Error delimiter validation
    delimited_errors = []
    for line in code:
        matches = re.findall(r'<<([^>]+)>>', line)
        delimited_errors.extend(matches)

    # Error array validation
    error_array = question.get('errors', [])
    if len(error_array) < 1 or len(error_array) > 5:
        errors.append(f"Should have 1-5 errors, got {len(error_array)}")

    # Error ID matching
    error_ids = [e.get('id') for e in error_array]
    for error_id in error_ids:
        if error_id not in delimited_errors:
            errors.append(f"Error ID '{error_id[:50]}...' not found in code delimiters")

    for delimited in delimited_errors:
        if delimited not in error_ids:
            errors.append(f"Delimited error '{delimited[:50]}...' not in errors array")

    # Description validation
    for i, error in enumerate(error_array):
        if 'id' not in error:
            errors.append(f"Error {i} missing 'id' field")
        if 'description' not in error:
            errors.append(f"Error {i} missing 'description' field")
        if len(error.get('description', '')) > 200:
            errors.append(f"Error {i} description too long ({len(error['description'])} chars)")

    return len(errors) == 0, errors
```

### Example Validation Run

```python
import json

# Load pipeline output
with open('backend/step7_new_format.json') as f:
    question = json.load(f)

# Validate
is_valid, errors = validate_question(question)

if is_valid:
    print("✅ Question is valid for frontend!")
else:
    print("❌ Validation errors:")
    for error in errors:
        print(f"  - {error}")
```

---

## Deployment Workflow

### Current Frontend Deployment (Vercel)

From the repo README:
- Push to `main` branch → Auto-deploys to https://demo.aqumen.ai
- Manual deploy: `vercel deploy`
- Preview deploys for PRs

### Recommended CI/CD Flow

1. **Generate questions** (run pipeline on schedule or manually)
2. **Export to JSON** file in frontend repo
3. **Commit to git**:
   ```bash
   cd /Users/hetalksinmaths/aqumen-demo-frontend
   git add src/data/generated_questions.json
   git commit -m "Update generated questions from pipeline"
   git push origin main
   ```
4. **Vercel auto-deploys** to production

### Quality Control

Before deploying:
- Validate all questions with the validation script
- Test locally: `npm run dev`
- Preview on Vercel before merging to main
- Monitor error rates after deployment

---

## Next Steps

### Immediate (MVP)
1. ✅ Pipeline already generates correct format
2. 🔲 Create export script to save Step 7 outputs to JSON array
3. 🔲 Test with 10 generated questions
4. 🔲 Replace hardcoded questions in frontend
5. 🔲 Deploy to Vercel

### Short-term (Enhancement)
1. Add topic/subtopic filtering in frontend
2. Generate 50+ questions across different topics
3. Implement question rotation/randomization
4. Add difficulty level filtering

### Long-term (Production)
1. Build REST API to serve questions dynamically
2. Store questions in database (PostgreSQL/MongoDB)
3. Implement user authentication and progress tracking
4. A/B test different question types
5. Collect analytics on which errors are hardest to spot

---

## Conclusion

**Current Status**: The pipeline output format is already 100% compatible with the frontend! ✅

**Required Work**: Just need to create an export script to generate multiple questions and save them to a JSON file that the frontend can import.

**Estimated Time**:
- Export script: 30 minutes
- Testing with 10 questions: 1 hour
- Frontend integration: 30 minutes
- Deployment: 15 minutes
- **Total: ~2.5 hours to go live**
