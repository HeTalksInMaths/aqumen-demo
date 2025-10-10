import React, { useState, useRef, useEffect } from 'react';
import { CheckCircle, XCircle, RotateCcw, Trophy, Eye, EyeOff, Target, Award, Loader, Sparkles } from 'lucide-react';
import { fetchQuestionStreaming, checkAPIHealth } from './api';

const App = () => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [clicks, setClicks] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const [gameComplete, setGameComplete] = useState(false);
  const [totalScore, setTotalScore] = useState(0);
  const [showSolution, setShowSolution] = useState(false);
  const [currentResult, setCurrentResult] = useState(null);
  const [parsedQuestions, setParsedQuestions] = useState([]);
  const [generationMode, setGenerationMode] = useState('demo'); // 'demo' or 'live'
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationError, setGenerationError] = useState(null);
  const [showTopicInput, setShowTopicInput] = useState(false);
  const [topicInput, setTopicInput] = useState('');
  const [viewMode, setViewMode] = useState('student'); // 'student' or 'dev'
  const [pipelineSteps, setPipelineSteps] = useState([]);
  const [pipelineFinal, setPipelineFinal] = useState(null);
  const [streamingCleanup, setStreamingCleanup] = useState(null);
  const [apiHealthy, setApiHealthy] = useState(null);
  const codeRef = useRef(null);
  const isDevMode = viewMode === 'dev';
  const [activePipelineTab, setActivePipelineTab] = useState(null);

  // GRPO Example for Dev Mode Demo with full 7-step pipeline trace
  const grpoExample = {
    title: "Group-Relative Policy Optimization (GRPO) Implementation",
    difficulty: "Expert",
    code: [
      "def grpo_loss(policy_logprobs, ref_logprobs, advantages, group_ids):",
      "    # Compute KL divergence with reference policy",
      "    kl_div = policy_logprobs - ref_logprobs",
      "    ",
      "    # Apply group-relative advantage normalization",
      "    <<normalized_advantages = (advantages - advantages.mean()) / advantages.std()>>",
      "    ",
      "    # Compute policy gradient loss",
      "    policy_loss = <<-(normalized_advantages * policy_logprobs).mean()>>",
      "    ",
      "    # Add KL penalty",
      "    kl_penalty = <<0.1 * kl_div.mean()>>",
      "    ",
      "    total_loss = policy_loss + kl_penalty",
      "    return total_loss"
    ],
    errors: [
      {
        id: "normalized_advantages = (advantages - advantages.mean()) / advantages.std()",
        description: "Normalizing across ALL samples instead of within groups! Should be: advantages.groupby(group_ids).transform(lambda x: (x - x.mean()) / x.std()). This defeats the entire purpose of GRPO - you need group-relative normalization."
      },
      {
        id: "-(normalized_advantages * policy_logprobs).mean()",
        description: "Missing importance sampling ratio! Should multiply by exp(policy_logprobs - ref_logprobs) to correct for off-policy data. Without this, policy updates are biased."
      },
      {
        id: "0.1 * kl_div.mean()",
        description: "KL penalty should use KL divergence, not simple difference! Need: 0.1 * (exp(ref_logprobs) * (ref_logprobs - policy_logprobs)).sum(). Current implementation doesn't properly constrain policy deviation."
      }
    ]
  };

  // Mock 7-step pipeline trace for GRPO example (for Dev + Demo mode)
  const grpoPipelineSteps = [
    {
      _id: "grpo-step-1",
      step_number: 1,
      description: "Generate Difficulty Categories",
      model: "claude-sonnet-4",
      timestamp: "2025-10-09T10:30:15.234Z",
      success: true,
      response_full: JSON.stringify({
  "Beginner": {
    "subtopics": ["Policy gradient basics", "Simple advantage estimation", "Basic RL optimization"],
    "skill_level": "Understands policy gradients, can implement vanilla PG",
    "time_to_learn": "3-6 months"
  },
  "Intermediate": {
    "subtopics": ["PPO vs DPO trade-offs", "Importance sampling", "KL divergence constraints"],
    "skill_level": "Implements RLHF algorithms, debugs convergence issues",
    "time_to_learn": "8-18 months"
  },
  "Expert": {
    "subtopics": ["Group-relative normalization", "Multi-objective RL", "Advanced variance reduction"],
    "skill_level": "Designs novel RL algorithms, handles complex training dynamics",
    "time_to_learn": "2+ years"
  }
})
    },
    {
      _id: "grpo-step-2",
      step_number: 2,
      description: "Generate Error Catalog",
      model: "claude-opus-4",
      timestamp: "2025-10-09T10:30:28.567Z",
      success: true,
      response_full: JSON.stringify({
  "domain": "Group-relative normalization in RLHF",
  "difficulty": "Expert",
  "errors": [
    {
      "mistake": "Normalizing advantages globally instead of within groups",
      "code_pattern": "normalized_adv = (advantages - advantages.mean()) / advantages.std()",
      "why_wrong": "GRPO requires group-relative normalization to reduce variance within comparison groups. Global normalization destroys the group structure.",
      "likelihood": 0.87,
      "impact": "Training instability, poor sample efficiency, incorrect policy updates",
      "difficulty_to_spot": "hard",
      "common_in": "experts transitioning from PPO"
    },
    {
      "mistake": "Missing importance sampling ratio in off-policy updates",
      "code_pattern": "loss = -(advantages * policy_logprobs).mean()",
      "why_wrong": "Off-policy RL requires importance sampling ratio exp(new_logprob - old_logprob) to correct distribution mismatch",
      "likelihood": 0.82,
      "impact": "Biased policy updates, divergence from optimal policy",
      "difficulty_to_spot": "hard",
      "common_in": "practitioners new to off-policy methods"
    },
    {
      "mistake": "Using simple difference instead of KL divergence for policy constraint",
      "code_pattern": "kl_penalty = (policy_logprobs - ref_logprobs).mean()",
      "why_wrong": "KL divergence is not a simple difference - requires proper calculation with exponentials",
      "likelihood": 0.79,
      "impact": "Policy deviates too far from reference, causes instability",
      "difficulty_to_spot": "medium",
      "common_in": "intermediate practitioners"
    }
  ]
})
    },
    {
      _id: "grpo-step-3",
      step_number: 3,
      description: "Generate Adversarial Question (Attempt 1)",
      model: "claude-opus-4",
      timestamp: "2025-10-09T10:30:45.123Z",
      success: true,
      response_full: `Generated adversarial code snippet targeting all 3 errors from catalog:

def grpo_loss(policy_logprobs, ref_logprobs, advantages, group_ids):
    # Compute KL divergence with reference policy
    kl_div = policy_logprobs - ref_logprobs

    # Apply group-relative advantage normalization
    normalized_advantages = (advantages - advantages.mean()) / advantages.std()

    # Compute policy gradient loss
    policy_loss = -(normalized_advantages * policy_logprobs).mean()

    # Add KL penalty
    kl_penalty = 0.1 * kl_div.mean()

    total_loss = policy_loss + kl_penalty
    return total_loss

Target errors embedded:
1. Global normalization (line 6) - should normalize within groups
2. Missing importance sampling (line 9) - should multiply by ratio
3. Incorrect KL (line 12) - should use proper KL divergence formula`
    },
    {
      _id: "grpo-step-4",
      step_number: 4,
      description: "Test with Strong Model (Sonnet)",
      model: "claude-sonnet-4",
      timestamp: "2025-10-09T10:31:02.456Z",
      success: true,
      response_full: JSON.stringify({
  "correctness": "Incorrect - Multiple critical errors in GRPO implementation",
  "main_issues": [
    "Line 6: Normalizing advantages globally defeats the purpose of GRPO. Must normalize within groups using group_ids.",
    "Line 9: Missing importance sampling ratio exp(policy_logprobs - ref_logprobs) for off-policy correction.",
    "Line 12: KL penalty uses simple difference instead of proper KL divergence formula."
  ],
  "production_impact": "Severe training instability, biased policy updates, poor convergence. This would fail in production RLHF.",
  "recommendations": [
    "Use grouped normalization: advantages.groupby(group_ids).transform(lambda x: (x - x.mean()) / x.std())",
    "Add importance sampling: ratio = exp(policy_logprobs - ref_logprobs); loss = -(ratio * advantages * policy_logprobs).mean()",
    "Fix KL: kl = (exp(ref_logprobs) * (ref_logprobs - policy_logprobs)).sum()"
  ],
  "expertise_level": "Expert - caught all 3 subtle GRPO implementation errors"
})
    },
    {
      _id: "grpo-step-5",
      step_number: 5,
      description: "Test with Weak Model (Haiku)",
      model: "claude-haiku-4",
      timestamp: "2025-10-09T10:31:18.789Z",
      success: true,
      response_full: JSON.stringify({
  "correctness": "Looks correct - implements GRPO loss function properly",
  "main_issues": [
    "KL penalty coefficient 0.1 might need tuning based on task",
    "Could add gradient clipping for stability"
  ],
  "production_impact": "Should work well for GRPO training with proper hyperparameter tuning",
  "recommendations": [
    "Consider adding max_grad_norm parameter for gradient clipping",
    "Experiment with KL coefficient in range [0.01, 0.5]",
    "Add logging for advantage statistics to monitor training"
  ],
  "expertise_level": "Intermediate - understands GRPO basics but missed the subtle errors"
})
    },
    {
      _id: "grpo-step-6",
      step_number: 6,
      description: "Judge Model Differentiation",
      model: "claude-opus-4",
      timestamp: "2025-10-09T10:31:35.234Z",
      success: true,
      response_full: JSON.stringify({
  "sonnet_analysis": {
    "correct": true,
    "identified_all_errors": true,
    "domain_expertise_shown": true,
    "confidence": 0.95,
    "reasoning": "Sonnet correctly identified all 3 critical GRPO errors: group normalization, importance sampling, and KL divergence. Shows expert-level understanding of RLHF algorithms."
  },
  "haiku_analysis": {
    "made_expected_error": true,
    "missed_critical_bugs": ["global_normalization", "missing_importance_sampling", "incorrect_kl"],
    "error_type": "surface_level_review_without_deep_algorithm_understanding",
    "error_severity": "critical",
    "reasoning": "Haiku focused on hyperparameter tuning suggestions but completely missed the fundamental algorithmic errors. Treated code as correct when it has severe bugs."
  },
  "differentiation_quality": "excellent",
  "differentiation_achieved": true,
  "assessment_effectiveness": {
    "tests_domain_knowledge": true,
    "requires_expert_understanding": true,
    "appropriate_difficulty": true,
    "clear_success_criteria": true
  },
  "overall_success": true,
  "confidence": 0.93
})
    },
    {
      _id: "grpo-step-7",
      step_number: 7,
      description: "Generate Student Assessment",
      model: "claude-opus-4",
      timestamp: "2025-10-09T10:31:52.567Z",
      success: true,
      response_full: `Final student assessment created with 3 clickable errors:

Error 1 (Line 6): Global advantage normalization
Error 2 (Line 9): Missing importance sampling ratio
Error 3 (Line 12): Incorrect KL divergence calculation

Assessment difficulty: Expert
Topic: Group-Relative Policy Optimization (GRPO)
Differentiation achieved: Yes (Sonnet caught all errors, Haiku missed all)
Assessment ready for student gameplay.`
    }
  ];

  const grpoPipelineFinal = {
    title: "Group-Relative Policy Optimization (GRPO) Implementation",
    difficulty: "Expert",
    success: true,
    differentiation_achieved: true,
    total_attempts: 1,
    stopped_at_step: 7,
    metadata: {
      topic: "Group-Relative Policy Optimization (GRPO)",
      topic_requested: "GRPO",
      weak_model_failures: 0
    }
  };

  const rawQuestions = [
    {
      title: "Transformer Attention Implementation",
      difficulty: "Intermediate",
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
        { id: "math.sqrt(d_k)", description: "Should check if d_k > 0 before taking sqrt to avoid potential domain errors" },
        { id: "mask == 0", description: "Mask logic is inverted - should mask where mask == 1 (padding tokens), not mask == 0" }
      ]
    },
    {
      title: "RAG Document Retrieval Pipeline",
      difficulty: "Beginner",
      code: [
        "def retrieve_documents(query, embeddings, documents, top_k=5):",
        "    query_embedding = embed_query(query)",
        "    ",
        "    similarities = cosine_similarity(query_embedding, embeddings)",
        "    top_indices = <<similarities.argsort()[-top_k:]>>",
        "    ",
        "    retrieved_docs = [documents[i] for i in top_indices]",
        "    return retrieved_docs, similarities[top_indices]"
      ],
      errors: [
        { id: "similarities.argsort()[-top_k:]", description: "argsort() returns ascending order - this gets the LOWEST similarities! Need [::-1] or use argpartition" }
      ]
    },
    {
      title: "Modern LLM API Integration",
      difficulty: "Intermediate",
      code: [
        "def call_openai_api(user_message, max_tokens=1000):",
        "    headers = {\"Authorization\": f\"Bearer {API_KEY}\"}",
        "    ",
        "    payload = {",
        "        \"model\": \"gpt-4\",",
        "        <<\"prompt\": user_message>>",
        "        \"max_tokens\": max_tokens,",
        "        \"temperature\": 0.7",
        "    }",
        "    ",
        "    response = requests.post(API_URL, headers=headers, json=payload)",
        "    return <<response.json()[\"choices\"][0][\"text\"]>>"
      ],
      errors: [
        { id: "\"prompt\": user_message", description: "GPT-4 uses 'messages' parameter with role-based format: [{'role': 'user', 'content': message}]" },
        { id: "response.json()[\"choices\"][0][\"text\"]", description: "GPT-4 response structure is ['choices'][0]['message']['content'], not ['text']" }
      ]
    },
    {
      title: "Fine-tuning Hyperparameter Configuration",
      difficulty: "Advanced",
      code: [
        "def setup_fine_tuning(model, train_loader, epochs=10):",
        "    optimizer = torch.optim.AdamW(model.parameters(), <<lr=1e-2>>)",
        "    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, <<step_size=1, gamma=0.1>>)",
        "    ",
        "    for epoch in range(epochs):",
        "        for batch in train_loader:",
        "            optimizer.zero_grad()",
        "            loss = model(batch)",
        "            loss.backward()",
        "            optimizer.step()",
        "        scheduler.step()"
      ],
      errors: [
        { id: "lr=1e-2", description: "Learning rate 1e-2 is way too high for fine-tuning! Should be 1e-5 to 5e-5 for stability" },
        { id: "step_size=1, gamma=0.1", description: "Reducing LR by 90% every epoch is too aggressive - consider step_size=3-5" }
      ]
    },
    {
      title: "Gradient Accumulation Implementation",
      difficulty: "Advanced",
      code: [
        "def train_with_accumulation(model, data_loader, accumulation_steps=4):",
        "    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5)",
        "    ",
        "    for i, batch in enumerate(data_loader):",
        "        <<optimizer.zero_grad()>>",
        "        ",
        "        loss = model(batch)<<  # Missing / accumulation_steps>>",
        "        loss.backward()",
        "        ",
        "        if (i + 1) % accumulation_steps == 0:",
        "            optimizer.step()",
        "            <<# Missing optimizer.zero_grad() here>>"
      ],
      errors: [
        { id: "optimizer.zero_grad()", description: "zero_grad() should be called OUTSIDE the loop, not every iteration" },
        { id: "  # Missing / accumulation_steps", description: "Loss should be divided by accumulation_steps to maintain equivalent gradient magnitudes" },
        { id: "# Missing optimizer.zero_grad() here", description: "Need optimizer.zero_grad() after optimizer.step() for next accumulation cycle" }
      ]
    },
    {
      title: "RLHF Reward Model Training",
      difficulty: "Advanced",
      code: [
        "def train_reward_model(model, comparison_data):",
        "    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)",
        "    ",
        "    for batch in comparison_data:",
        "        preferred, rejected = batch",
        "        ",
        "        preferred_reward = model(preferred)",
        "        rejected_reward = model(rejected)",
        "        ",
        "        loss = <<-torch.log(torch.sigmoid(preferred_reward - rejected_reward))>>",
        "        <<# Missing optimizer.zero_grad()>>",
        "        loss.backward()",
        "        optimizer.step()"
      ],
      errors: [
        { id: "-torch.log(torch.sigmoid(preferred_reward - rejected_reward))", description: "Missing .mean() - loss should be averaged across batch dimension for proper gradients" },
        { id: "# Missing optimizer.zero_grad()", description: "Must call optimizer.zero_grad() before loss.backward() to clear accumulated gradients" }
      ]
    },
    {
      title: "Attention Mask Broadcasting",
      difficulty: "Expert",
      code: [
        "def apply_attention_mask(attention_scores, mask):",
        "    # attention_scores: [batch, heads, seq_len, seq_len]",
        "    # mask: [batch, seq_len]",
        "    ",
        "    if mask is not None:",
        "        expanded_mask = <<mask.unsqueeze(1).unsqueeze(1)>>  # Wrong dimensions!",
        "        attention_scores = attention_scores.masked_fill(",
        "            <<expanded_mask == 0>>, -1e9)",
        "    ",
        "    return F.softmax(attention_scores, dim=-1)"
      ],
      errors: [
        { id: "mask.unsqueeze(1).unsqueeze(1)", description: "Wrong broadcasting! Should be unsqueeze(1).unsqueeze(2) for [batch, 1, seq_len, 1] shape" },
        { id: "expanded_mask == 0", description: "Mask should be applied where mask == 1 (padding positions), not mask == 0" }
      ]
    },
    {
      title: "Prompt Injection Defense",
      difficulty: "Intermediate",
      code: [
        "def secure_prompt_handler(user_input, system_prompt):",
        "    # Basic injection detection",
        "    injection_patterns = [<<\"ignore previous\", \"disregard instructions\">>]",
        "    ",
        "    for pattern in injection_patterns:",
        "        if pattern in user_input.lower():",
        "            return \"Potential injection detected\"",
        "    ",
        "    # Construct prompt",
        "    <<full_prompt = system_prompt + \"\n\nUser: \" + user_input>>",
        "    ",
        "    return call_llm(full_prompt)"
      ],
      errors: [
        { id: "\"ignore previous\", \"disregard instructions\"", description: "Keyword-based detection is trivially bypassed (e.g., 'ign0re prev10us') - need semantic analysis" },
        { id: "full_prompt = system_prompt + \"\n\nUser: \" + user_input", description: "String concatenation allows injection! Use structured messages: [{'role': 'system', 'content': system_prompt}]" }
      ]
    },
    {
      title: "Model Evaluation with Proper Metrics",
      difficulty: "Beginner",
      code: [
        "def evaluate_classification_model(y_true, y_pred):",
        "    accuracy = np.mean(y_pred == y_true)",
        "    ",
        "    # Calculate precision and recall",
        "    <<tp = fp = fn = 0>>  # These are never computed!",
        "    precision = tp / (tp + fp) if (tp + fp) > 0 else 0",
        "    recall = tp / (tp + fn) if (tp + fn) > 0 else 0",
        "    ",
        "    f1_score = <<2 * (precision * recall) / (precision + recall)>> if (precision + recall) > 0 else 0",
        "    ",
        "    return {\"accuracy\": accuracy, \"precision\": precision, \"recall\": recall, \"f1\": f1_score}"
      ],
      errors: [
        { id: "tp = fp = fn = 0", description: "Variables tp, fp, fn are initialized but never calculated from y_true and y_pred arrays!" },
        { id: "2 * (precision * recall) / (precision + recall)", description: "F1 score will always be 0 since precision/recall are based on uncomputed tp/fp/fn values" }
      ]
    },
    {
      title: "Vector Database Optimization",
      difficulty: "Intermediate",
      code: [
        "def build_optimized_vector_index(documents, embedding_model):",
        "    embeddings = []",
        "    ",
        "    for doc in documents:",
        "        embedding = embedding_model.encode(doc)",
        "        embeddings.append(embedding)",
        "    ",
        "    # Initialize FAISS index",
        "    <<dimension = embedding.shape[0]>>  # Loop variable scope issue",
        "    index = faiss.IndexFlatL2(dimension)",
        "    ",
        "    embeddings_array = <<np.array(embeddings)>>  # Wrong dtype",
        "    index.add(embeddings_array)",
        "    ",
        "    return index"
      ],
      errors: [
        { id: "dimension = embedding.shape[0]", description: "Using 'embedding' from loop scope after loop ends! Should use embeddings[0].shape[0]" },
        { id: "np.array(embeddings)", description: "Should specify dtype=np.float32 - FAISS requires float32 for optimal performance" }
      ]
    }
  ];

  // Load questions based on viewMode and generationMode
  useEffect(() => {
    if (generationMode === 'demo') {
      if (viewMode === 'dev') {
        // Dev + Demo: Show GRPO example with full pipeline trace
        const parsed = parseQuestion(grpoExample);
        setParsedQuestions([parsed]);
        setPipelineSteps(grpoPipelineSteps);
        setPipelineFinal(grpoPipelineFinal);
        setActivePipelineTab('final'); // Default to showing final assessment
      } else {
        // Student + Demo: Show 10 hardcoded questions
        const parsed = rawQuestions.map(question => parseQuestion(question));
        setParsedQuestions(parsed);
        // Clear pipeline data in Student mode
        setPipelineSteps([]);
        setPipelineFinal(null);
        setActivePipelineTab(null);
      }
    } else {
      // Live mode: Start with empty canvas
      setParsedQuestions([]);
      setCurrentQuestion(0);
      // Clear pipeline data (will be populated on generation)
      setPipelineSteps([]);
      setPipelineFinal(null);
      setActivePipelineTab(null);

      // Check API health
      checkAPIHealth().then(healthy => {
        setApiHealthy(healthy);
        if (!healthy) {
          setGenerationError('Backend API is not reachable. Make sure FastAPI is running on port 8000.');
        }
      });
    }
  }, [generationMode, viewMode]);

  useEffect(() => {
    return () => {
      if (streamingCleanup) {
        streamingCleanup();
      }
    };
  }, [streamingCleanup]);

  // Generate new question from pipeline
  const generateNewQuestion = async () => {
    if (!topicInput.trim()) {
      alert('Please enter a topic first!');
      return;
    }

    const normalizedTopic = topicInput.trim();

    if (streamingCleanup) {
      streamingCleanup();
      setStreamingCleanup(null);
    }

    setPipelineSteps([]);
    setPipelineFinal(null);
    setActivePipelineTab(null);

    setIsGenerating(true);
    setGenerationError(null);

    const handleStepUpdate = (stepData) => {
      const enrichedStep = {
        ...stepData,
        _id: `${stepData.step_number}-${Date.now()}-${Math.random().toString(16).slice(2)}`
      };
      setPipelineSteps(prev => {
        const updated = [...prev, enrichedStep];
        setActivePipelineTab(enrichedStep._id);
        return updated;
      });
    };

    const handleComplete = (question, finalData) => {
      const parsed = parseQuestion(question);
      registerGeneratedQuestion(parsed);
      setPipelineFinal({
        ...finalData,
        title: question.title,
        difficulty: question.difficulty
      });
      setActivePipelineTab('final');
      setIsGenerating(false);
      setTopicInput('');
      setShowTopicInput(false);
      setStreamingCleanup(null);
    };

    const handleError = (error) => {
      console.error('Streaming generation error:', error);
      setGenerationError(error.message || 'Failed to generate question. Please try again.');
      setIsGenerating(false);
      setStreamingCleanup(null);
      setActivePipelineTab(null);
    };

    try {
      const cleanup = fetchQuestionStreaming(
        normalizedTopic,
        3,
        handleStepUpdate,
        handleComplete,
        handleError
      );
      setStreamingCleanup(() => cleanup);
    } catch (error) {
      console.error('Streaming initialization error:', error);
      setGenerationError(error.message || 'Failed to start streaming generation. Please try again.');
      setIsGenerating(false);
    }
  };

  const registerGeneratedQuestion = (parsedQuestion) => {
    setParsedQuestions(prev => {
      const updated = [...prev, parsedQuestion];
      setCurrentQuestion(updated.length - 1);
      return updated;
    });
    setClicks([]);
    setShowResults(false);
    setShowSolution(false);
    setCurrentResult(null);
    setGameComplete(false);
  };

  const parseQuestion = (question) => {
    const parsedLines = [];
    const errorPositions = [];
    
    question.code.forEach((line, lineIndex) => {
      let cleanLine = line;
      let processedChars = 0;
      
      // Find all delimited sections in this line
      const delimiterRegex = /<<([^>]+)>>/g;
      let match;
      
      while ((match = delimiterRegex.exec(line)) !== null) {
        const errorText = match[1];
        const startPos = match.index - processedChars;
        const endPos = startPos + errorText.length;
        
        errorPositions.push({
          line: lineIndex,
          startPos,
          endPos,
          text: errorText,
          id: errorText
        });
        
        processedChars += 4; // Account for removed << >>
      }
      
      // Remove delimiters for display
      cleanLine = line.replace(/<<([^>]+)>>/g, '$1');
      parsedLines.push(cleanLine);
    });
    
    return {
      ...question,
      parsedCode: parsedLines,
      errorPositions
    };
  };

  const calculateScore = (clicks, errors, hasNoErrors = false) => {
    const correctClicks = clicks.filter(click => 
      click.errorId && errors.some(error => error.id === click.errorId)
    ).length;
    
    const falsePositives = clicks.length - correctClicks;
    const missedErrors = errors.length - correctClicks;
    
    // Handle no-error questions
    if (hasNoErrors || errors.length === 0) {
      return {
        score: falsePositives === 0 ? 100 : Math.max(0, 100 - (falsePositives * 25)),
        correctClicks: 0,
        falsePositives,
        missedErrors: 0,
        breakdown: {
          baseScore: falsePositives === 0 ? "100.0" : "0.0",
          penalty: falsePositives * 25,
          final: (falsePositives === 0 ? 100 : Math.max(0, 100 - (falsePositives * 25))).toFixed(1)
        }
      };
    }
    
    // Precision: How many of your clicks were correct?
    const precision = clicks.length > 0 ? correctClicks / clicks.length : 1;
    
    // Recall: How many errors did you find?  
    const recall = errors.length > 0 ? correctClicks / errors.length : 1;
    
    // F1-style balanced score
    const f1Score = precision + recall > 0 ? 
      (2 * precision * recall) / (precision + recall) : 0;
    
    const finalScore = f1Score * 100;
    
    return {
      score: finalScore,
      correctClicks,
      falsePositives,
      missedErrors,
      breakdown: {
        baseScore: (recall * 100).toFixed(1),
        penalty: falsePositives > 0 ? `Precision: ${(precision * 100).toFixed(1)}%` : "No false positives",
        final: finalScore.toFixed(1)
      }
    };
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '—';
    try {
      const date = new Date(timestamp);
      if (Number.isNaN(date.getTime())) {
        return timestamp;
      }
      return date.toLocaleTimeString();
    } catch {
      return timestamp;
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch(difficulty) {
      case 'Beginner': return 'bg-green-100 text-green-800';
      case 'Intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'Advanced': return 'bg-orange-100 text-orange-800';
      case 'Expert': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const renderCodeWithClickableSpans = (codeLines, errorPositions) => {
    const spanBaseStyle = { whiteSpace: 'pre' };
    
    return codeLines.map((line, lineIndex) => {
      const lineErrors = errorPositions.filter(error => error.line === lineIndex);
      
      if (lineErrors.length === 0) {
        return (
          <div key={lineIndex} className="relative group" data-line={lineIndex}>
            <span className="text-gray-500 mr-4 select-none text-right inline-block w-8 text-xs">
              {lineIndex + 1}
            </span>
            <span 
              className="cursor-pointer hover:bg-gray-700 hover:bg-opacity-50 transition-colors rounded px-1"
              style={spanBaseStyle}
              onClick={(e) => handleLineClick(e, lineIndex)}
            >
              {line || ' '}
            </span>
          </div>
        );
      }
      
      // Sort errors by position
      const sortedErrors = [...lineErrors].sort((a, b) => a.startPos - b.startPos);
      
      // Split line into clickable segments
      const segments = [];
      let lastPos = 0;
      
      sortedErrors.forEach((error) => {
        // Add text before error
        if (error.startPos > lastPos) {
          segments.push({
            text: line.substring(lastPos, error.startPos),
            isError: false,
            lineIndex
          });
        }
        
        // Add error segment
        segments.push({
          text: error.text,
          isError: true,
          errorId: error.id,
          lineIndex
        });
        
        lastPos = error.endPos;
      });
      
      // Add remaining text
      if (lastPos < line.length) {
        segments.push({
          text: line.substring(lastPos),
          isError: false,
          lineIndex
        });
      }
      
      return (
        <div key={lineIndex} className="relative group" data-line={lineIndex}>
          <span className="text-gray-500 mr-4 select-none text-right inline-block w-8 text-xs">
            {lineIndex + 1}
          </span>
          {segments.map((segment, segIndex) => (
            <span
              key={segIndex}
              className={`cursor-pointer transition-all duration-200 rounded px-1 ${segment.isError ? 'hover:bg-gray-700 hover:bg-opacity-50' : 'hover:bg-gray-700 hover:bg-opacity-50'}`}
              style={spanBaseStyle}
              onClick={(e) => segment.isError 
                ? handleErrorClick(e, segment.errorId, segment.lineIndex)
                : handleLineClick(e, segment.lineIndex)
              }
              title={segment.isError ? "Click to identify this error" : ""}
            >
              {segment.text}
            </span>
          ))}
        </div>
      );
    });
  };

  const handleErrorClick = (event, errorId, lineIndex) => {
    if (showResults || clicks.length >= 3) return;
    
    event.stopPropagation();
    
    const rect = event.currentTarget.getBoundingClientRect();
    const codeRect = codeRef.current.getBoundingClientRect();
    
    const clickPosition = {
      x: event.clientX - codeRect.left,
      y: event.clientY - codeRect.top
    };
    
    const newClick = { 
      line: lineIndex, 
      errorId: errorId,
      position: clickPosition,
      id: Date.now(),
      isCorrect: true
    };
    
    const newClicks = [...clicks, newClick];
    setClicks(newClicks);
    
    // Auto-submit after 3 clicks
    if (newClicks.length >= 3) {
      setTimeout(() => checkAnswer(newClicks), 500);
    }
  };

  const handleLineClick = (event, lineIndex) => {
    if (showResults || clicks.length >= 3) return;
    
    event.stopPropagation();
    
    const rect = event.currentTarget.getBoundingClientRect();
    const codeRect = codeRef.current.getBoundingClientRect();
    
    const clickPosition = {
      x: event.clientX - codeRect.left,
      y: event.clientY - codeRect.top
    };
    
    const newClick = { 
      line: lineIndex, 
      errorId: null,
      position: clickPosition,
      id: Date.now(),
      isCorrect: false
    };
    
    const newClicks = [...clicks, newClick];
    setClicks(newClicks);
    
    // Auto-submit after 3 clicks
    if (newClicks.length >= 3) {
      setTimeout(() => checkAnswer(newClicks), 500);
    }
  };

  const checkAnswer = (clicksToCheck = clicks) => {
    if (parsedQuestions.length === 0) return;
    
    const currentQ = parsedQuestions[currentQuestion];
    const result = calculateScore(clicksToCheck, currentQ.errors);
    
    setTotalScore(prev => prev + result.score);
    setCurrentResult(result);
    setShowResults(true);
  };

  const nextQuestion = () => {
    if (currentQuestion < parsedQuestions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
      setClicks([]);
      setShowResults(false);
      setShowSolution(false);
      setCurrentResult(null);
    } else {
      setGameComplete(true);
    }
  };

  const resetGame = () => {
    setCurrentQuestion(0);
    setClicks([]);
    setShowResults(false);
    setGameComplete(false);
    setTotalScore(0);
    setShowSolution(false);
    setCurrentResult(null);
  };

  const submitAnswer = () => {
    checkAnswer();
  };

  // Don't show loading screen in Live mode - show empty state instead
  if (parsedQuestions.length === 0 && generationMode === 'demo') {
    return (
      <div className="flex justify-center items-center h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <div className="text-gray-600">Loading AI Code Review Challenge...</div>
        </div>
      </div>
    );
  }

  // Handle empty state in Live mode
  if (parsedQuestions.length === 0 && generationMode === 'live') {
    return (
      <div className="max-w-7xl mx-auto p-6 bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
        <div className="bg-white rounded-lg shadow-2xl p-6">
          {/* Header */}
          <div className="flex justify-between items-start mb-6">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-3xl font-bold text-gray-800">AI Code Review Mastery</h1>
                <Award className="w-8 h-8 text-indigo-600" />
              </div>
              <p className="text-gray-600 text-lg">Hunt down conceptual errors by clicking on problematic code segments</p>
            </div>
          </div>

          {/* View Mode Toggle */}
          <div className="mb-4 flex flex-wrap items-center gap-3">
            <span className="text-sm font-medium text-gray-700">View:</span>
            <button
              onClick={() => setViewMode('student')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                isDevMode
                  ? 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                  : 'bg-purple-600 text-white shadow-md'
              }`}
            >
              🎮 Student Mode
            </button>
            <button
              onClick={() => setViewMode('dev')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
                isDevMode
                  ? 'bg-purple-600 text-white shadow-md'
                  : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
              }`}
            >
              <Sparkles className="w-4 h-4" />
              Dev Mode (Streaming)
            </button>
          </div>

          {/* Mode Toggle & Generation Controls */}
          <div className="mb-6 p-4 bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-xl">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-3">
                <span className="text-sm font-medium text-gray-700">Mode:</span>
                <button
                  onClick={() => {
                    setGenerationMode('demo');
                    setGenerationError(null);
                    setShowTopicInput(false);
                  }}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    generationMode === 'demo'
                      ? 'bg-indigo-600 text-white shadow-md'
                      : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                  }`}
                >
                  📚 Demo (10 Hardcoded)
                </button>
                <button
                  onClick={() => {
                    setGenerationMode('live');
                    setGenerationError(null);
                  }}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
                    generationMode === 'live'
                      ? 'bg-indigo-600 text-white shadow-md'
                      : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                  }`}
                >
                  <Sparkles className="w-4 h-4" />
                  Live Generation
                </button>
              </div>

              {generationMode === 'live' && (
                <div className="flex items-center gap-3">
                  {apiHealthy === false && (
                    <span className="text-xs text-red-600 bg-red-50 px-2 py-1 rounded">
                      ⚠️ API offline
                    </span>
                  )}
                  {apiHealthy === true && (
                    <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded">
                      ✓ API ready
                    </span>
                  )}
                  <button
                    onClick={() => setShowTopicInput(!showTopicInput)}
                    disabled={isGenerating || apiHealthy === false}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2 shadow-md"
                  >
                    {isGenerating ? (
                      <>
                        <Loader className="w-4 h-4 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4" />
                        Generate New Question
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>

            {/* Topic Input (Live Mode) */}
            {generationMode === 'live' && showTopicInput && !isGenerating && (
              <div className="mt-4 p-4 bg-white rounded-lg border border-purple-200">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Enter AI/ML Topic:
                </label>
                <input
                  type="text"
                  value={topicInput}
                  onChange={(e) => setTopicInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && generateNewQuestion()}
                  placeholder="e.g., RLHF with Bradley-Terry Loss, Attention Mask Broadcasting"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  autoFocus
                />
                <div className="flex gap-2 mt-3">
                  <button
                    onClick={generateNewQuestion}
                    disabled={!topicInput.trim()}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
                  >
                    Generate
                  </button>
                  <button
                    onClick={() => {
                      setShowTopicInput(false);
                      setTopicInput('');
                    }}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
                <div className="mt-2 text-xs text-gray-500">
                  💡 Example topics: Group-Relative Policy Optimization, Attention Mask Broadcasting, RLHF Reward Model Training
                </div>
              </div>
            )}

            {/* Generation Progress (Live Mode) */}
            {isGenerating && (
              <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center gap-3 mb-2">
                  <Loader className="w-5 h-5 animate-spin text-blue-600" />
                  <span className="text-sm font-medium text-blue-800">
                    Generating question from topic: "{topicInput}"
                  </span>
                </div>
                <div className="text-xs text-blue-600">
                  This may take 60-90 seconds as the 7-step pipeline runs...
                </div>
              </div>
            )}

            {/* Generation Error */}
            {generationError && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <div className="text-sm text-red-800">
                  <strong>Error:</strong> {generationError}
                </div>
                {generationError.includes('CORS') && (
                  <div className="mt-2 text-xs text-red-600">
                    Make sure CORS is enabled in the FastAPI backend for localhost:5173
                  </div>
                )}
              </div>
            )}
          </div>

          {isDevMode && generationMode === 'live' && (
            <div className="mb-6 rounded-xl border border-purple-200 bg-white p-4 shadow-inner">
              <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
                <div>
                  <h2 className="text-lg font-semibold text-purple-800">Pipeline Execution</h2>
                  <p className="text-xs text-gray-500">
                    Live stream of the 7-step pipeline from FastAPI (SSE)
                  </p>
                </div>
                {isGenerating && (
                  <span className="flex items-center gap-2 text-sm font-medium text-indigo-600">
                    <Loader className="w-4 h-4 animate-spin" />
                    Streaming…
                  </span>
                )}
              </div>

              <div className="rounded-lg border border-dashed border-purple-200 bg-purple-50/60 p-4 text-sm text-purple-700">
                {isGenerating
                  ? 'Waiting for the first pipeline step…'
                  : 'Run a live generation to stream each step of the pipeline here.'}
              </div>
            </div>
          )}

          {/* Empty State Message */}
          <div className="flex flex-col items-center justify-center py-16 px-4">
            <Sparkles className="w-16 h-16 text-indigo-400 mb-4" />
            <h2 className="text-2xl font-bold text-gray-800 mb-2">No Questions Yet</h2>
            <p className="text-gray-600 text-center max-w-md mb-6">
              {viewMode === 'dev'
                ? 'Generate a new question using the "Generate New Question" button above to see the 7-step pipeline in action.'
                : 'Generate a new question using the "Generate New Question" button above to start the assessment.'}
            </p>
            {apiHealthy === false && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg max-w-md">
                <p className="text-sm text-red-800">
                  <strong>⚠️ Backend API is offline</strong>
                </p>
                <p className="text-xs text-red-600 mt-1">
                  Make sure FastAPI is running on port 8000 before generating questions.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  const currentQ = parsedQuestions[currentQuestion];

  if (gameComplete) {
    const maxScore = parsedQuestions.length * 100;
    const percentage = Math.round((totalScore / maxScore) * 100);
    
    return (
      <div className="max-w-4xl mx-auto p-6 bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
        <div className="bg-white rounded-lg shadow-2xl p-8 text-center">
          <Trophy className="w-20 h-20 text-yellow-500 mx-auto mb-6" />
          <h2 className="text-4xl font-bold text-gray-800 mb-4">Challenge Complete!</h2>
          <div className="text-7xl font-bold text-indigo-600 mb-4">{totalScore.toFixed(0)}</div>
          <div className="text-2xl text-gray-600 mb-8">
            Final Score ({percentage}% accuracy)
          </div>
          
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 mb-8">
            <div className="text-lg font-semibold text-gray-700 mb-3">
              Your Code Review Rating:
            </div>
            <div className="text-3xl font-bold mb-2">
              {percentage >= 90 ? "🏆 Expert Code Reviewer" : 
               percentage >= 75 ? "🥈 Advanced Reviewer" : 
               percentage >= 60 ? "🥉 Competent Reviewer" : 
               percentage >= 40 ? "📚 Developing Skills" :
               "🌱 Keep Learning"}
            </div>
            <div className="text-sm text-gray-600 mt-2">
              {percentage >= 90 ? "Outstanding! You have sharp eyes for AI code issues." : 
               percentage >= 75 ? "Great work! You caught most of the critical errors." : 
               percentage >= 60 ? "Good job! You're building solid review skills." : 
               percentage >= 40 ? "Nice progress! Keep practicing to improve." :
               "Don't give up! Every expert started as a beginner."}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-8 text-sm">
            <div className="bg-green-50 border border-green-200 rounded-lg p-3">
              <div className="font-semibold text-green-700">Questions Completed</div>
              <div className="text-2xl font-bold text-green-600">{parsedQuestions.length}</div>
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <div className="font-semibold text-blue-700">Average Score</div>
              <div className="text-2xl font-bold text-blue-600">{(totalScore / parsedQuestions.length).toFixed(0)}%</div>
            </div>
          </div>
          
          <button
            onClick={resetGame}
            className="bg-indigo-600 text-white px-8 py-4 rounded-lg font-semibold hover:bg-indigo-700 transition-colors flex items-center gap-2 mx-auto text-lg"
          >
            <RotateCcw className="w-5 h-5" />
            Challenge Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
      <div className="bg-white rounded-lg shadow-2xl p-6">
        {/* Header */}
        <div className="flex justify-between items-start mb-6">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-gray-800">AI Code Review Mastery</h1>
              <Award className="w-8 h-8 text-indigo-600" />
            </div>
            <p className="text-gray-600 text-lg">Hunt down conceptual errors by clicking on problematic code segments</p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500 mb-1">Question {currentQuestion + 1} of {parsedQuestions.length}</div>
            <div className="text-2xl font-bold text-indigo-600">Score: {totalScore.toFixed(0)}</div>
            <div className="text-xs text-gray-500">Average: {(totalScore / Math.max(1, currentQuestion + (showResults ? 1 : 0))).toFixed(0)}%</div>
          </div>
        </div>

        {/* View Mode Toggle */}
        <div className="mb-4 flex flex-wrap items-center gap-3">
          <span className="text-sm font-medium text-gray-700">View:</span>
          <button
            onClick={() => setViewMode('student')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              isDevMode
                ? 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                : 'bg-purple-600 text-white shadow-md'
            }`}
          >
            🎮 Student Mode
          </button>
          <button
            onClick={() => setViewMode('dev')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
              isDevMode
                ? 'bg-purple-600 text-white shadow-md'
                : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            Dev Mode (Streaming)
          </button>
        </div>

        {viewMode === 'student' && pipelineSteps.length > 0 && (
          <div className="mb-4 rounded-lg border border-purple-200 bg-purple-50 px-4 py-2 text-xs text-purple-700">
            Latest pipeline run captured. Switch to Dev Mode to inspect step details.
          </div>
        )}

        {/* Mode Toggle & Generation Controls */}
        <div className="mb-6 p-4 bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-xl">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium text-gray-700">Mode:</span>
              <button
                onClick={() => {
                  setGenerationMode('demo');
                  setGenerationError(null);
                  setShowTopicInput(false);
                }}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  generationMode === 'demo'
                    ? 'bg-indigo-600 text-white shadow-md'
                    : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                }`}
              >
                📚 Demo (10 Hardcoded)
              </button>
              <button
                onClick={() => {
                  setGenerationMode('live');
                  setGenerationError(null);
                }}
                className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
                  generationMode === 'live'
                    ? 'bg-indigo-600 text-white shadow-md'
                    : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                }`}
              >
                <Sparkles className="w-4 h-4" />
                Live Generation
              </button>
            </div>

            {generationMode === 'live' && (
              <div className="flex items-center gap-3">
                {apiHealthy === false && (
                  <span className="text-xs text-red-600 bg-red-50 px-2 py-1 rounded">
                    ⚠️ API offline
                  </span>
                )}
                {apiHealthy === true && (
                  <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded">
                    ✓ API ready
                  </span>
                )}
                <button
                  onClick={() => setShowTopicInput(!showTopicInput)}
                  disabled={isGenerating || apiHealthy === false}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2 shadow-md"
                >
                  {isGenerating ? (
                    <>
                      <Loader className="w-4 h-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      Generate New Question
                    </>
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Topic Input (Live Mode) */}
          {generationMode === 'live' && showTopicInput && !isGenerating && (
            <div className="mt-4 p-4 bg-white rounded-lg border border-purple-200">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Enter AI/ML Topic:
              </label>
              <input
                type="text"
                value={topicInput}
                onChange={(e) => setTopicInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && generateNewQuestion()}
                placeholder="e.g., RLHF with Bradley-Terry Loss, Attention Mask Broadcasting"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                autoFocus
              />
              <div className="flex gap-2 mt-3">
                <button
                  onClick={generateNewQuestion}
                  disabled={!topicInput.trim()}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  Generate
                </button>
                <button
                  onClick={() => {
                    setShowTopicInput(false);
                    setTopicInput('');
                  }}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
              </div>
              <div className="mt-2 text-xs text-gray-500">
                💡 Example topics: Group-Relative Policy Optimization, Attention Mask Broadcasting, RLHF Reward Model Training
              </div>
            </div>
          )}

          {/* Generation Progress (Live Mode) */}
          {isGenerating && (
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center gap-3 mb-2">
                <Loader className="w-5 h-5 animate-spin text-blue-600" />
                <span className="text-sm font-medium text-blue-800">
                  Generating question from topic: "{topicInput}"
                </span>
              </div>
              <div className="text-xs text-blue-600">
                This may take 60-90 seconds as the 7-step pipeline runs...
              </div>
            </div>
          )}

          {/* Generation Error */}
          {generationError && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="text-sm text-red-800">
                <strong>Error:</strong> {generationError}
              </div>
              {generationError.includes('CORS') && (
                <div className="mt-2 text-xs text-red-600">
                  Make sure CORS is enabled in the FastAPI backend for localhost:5173
                </div>
              )}
            </div>
          )}
        </div>

        {isDevMode && (
          <div className="mb-6 rounded-xl border border-purple-200 bg-white p-4 shadow-inner">
            <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
              <div>
                <h2 className="text-lg font-semibold text-purple-800">Pipeline Execution</h2>
                <p className="text-xs text-gray-500">
                  {generationMode === 'demo'
                    ? 'Gold-standard GRPO example with full 7-step trace'
                    : 'Live stream of the 7-step pipeline from FastAPI (SSE)'}
                </p>
              </div>
              {isGenerating ? (
                <span className="flex items-center gap-2 text-sm font-medium text-indigo-600">
                  <Loader className="w-4 h-4 animate-spin" />
                  Streaming…
                </span>
              ) : pipelineFinal ? (
                <span className={`text-sm font-semibold ${pipelineFinal.success ? 'text-green-600' : 'text-red-600'}`}>
                  {pipelineFinal.success ? '✅ Last run succeeded' : '⚠️ Review last run'}
                </span>
              ) : null}
            </div>

            {pipelineSteps.length === 0 && !pipelineFinal ? (
              <div className="rounded-lg border border-dashed border-purple-200 bg-purple-50/60 p-4 text-sm text-purple-700">
                {isGenerating
                  ? 'Waiting for the first pipeline step…'
                  : 'Run a live generation to stream each step of the pipeline here.'}
              </div>
            ) : (
              <div>
                <div className="mb-4 flex flex-wrap gap-2">
                  {pipelineSteps.map((step, index) => {
                    const isActive = (activePipelineTab ?? pipelineSteps[pipelineSteps.length - 1]?._id) === step._id;
                    return (
                      <button
                        key={step._id || `${step.step_number}-${index}`}
                        onClick={() => setActivePipelineTab(step._id)}
                        className={`rounded-lg px-3 py-2 text-xs font-medium transition-colors ${
                          isActive
                            ? 'bg-purple-600 text-white shadow'
                            : 'bg-purple-50 text-purple-700 border border-purple-200 hover:bg-purple-100'
                        }`}
                      >
                        Step {step.step_number}
                      </button>
                    );
                  })}
                  {pipelineFinal && (
                    <button
                      onClick={() => setActivePipelineTab('final')}
                      className={`rounded-lg px-3 py-2 text-xs font-medium transition-colors ${
                        (activePipelineTab || (!activePipelineTab && pipelineFinal)) === 'final'
                          ? 'bg-green-600 text-white shadow'
                          : 'bg-green-50 text-green-700 border border-green-200 hover:bg-green-100'
                      }`}
                    >
                      Final Assessment
                    </button>
                  )}
                </div>

                <div className="max-h-96 overflow-y-auto rounded-lg border border-purple-100 bg-white p-4 text-sm text-gray-700">
                  {(() => {
                    const resolvedTab = (() => {
                      if (activePipelineTab) return activePipelineTab;
                      if (pipelineFinal) return 'final';
                      return pipelineSteps[pipelineSteps.length - 1]?._id || null;
                    })();

                    if (resolvedTab === 'final' && pipelineFinal) {
                      return (
                        <div>
                          <div className="flex flex-wrap items-center justify-between gap-3">
                            <div>
                              <div className="font-semibold text-gray-800">
                                Final Question: {pipelineFinal.title || 'Generated Assessment'}
                              </div>
                              <div className="text-xs text-gray-500">
                                Topic: {pipelineFinal.metadata?.topic || pipelineFinal.metadata?.topic_requested || 'N/A'} · Difficulty: {pipelineFinal.difficulty || 'Unknown'}
                              </div>
                            </div>
                            <span className={`text-sm font-semibold ${pipelineFinal.success ? 'text-green-600' : 'text-red-600'}`}>
                              {pipelineFinal.success ? '✅ Generation succeeded' : '⚠️ Generation failed'}
                            </span>
                          </div>
                          <div className="mt-3 grid gap-2 text-xs text-gray-600 sm:grid-cols-2">
                            <div>Attempts: {pipelineFinal.total_attempts ?? '—'}</div>
                            <div>Weak model failures: {pipelineFinal.metadata?.weak_model_failures ?? '—'}</div>
                            <div>Differentiation achieved: {pipelineFinal.differentiation_achieved ? 'Yes' : 'No'}</div>
                            <div>Stopped at step: {pipelineFinal.stopped_at_step ?? '—'}</div>
                          </div>
                          <div className="mt-3 text-xs text-gray-500">
                            Tip: toggle back to Student Mode to focus on the playable question.
                          </div>
                        </div>
                      );
                    }

                    const activeStep = pipelineSteps.find(step => step._id === resolvedTab) || pipelineSteps[pipelineSteps.length - 1];

                    if (!activeStep) {
                      return <div className="text-xs text-gray-500">Awaiting pipeline updates…</div>;
                    }

                    return (
                      <div>
                        <div className="flex flex-wrap items-start justify-between gap-3">
                          <div>
                            <div className="font-semibold text-gray-800">
                              Step {activeStep.step_number}: {activeStep.description || 'Unnamed step'}
                            </div>
                            <div className="mt-1 text-xs text-gray-500">
                              Model: {activeStep.model || '—'} · {formatTimestamp(activeStep.timestamp)}
                            </div>
                          </div>
                          <span className={`text-sm font-semibold ${activeStep.success ? 'text-green-600' : 'text-red-600'}`}>
                            {activeStep.success ? '✅ Success' : '⚠️ Attention'}
                          </span>
                        </div>
                        {activeStep.response_full && (
                          <pre className="mt-3 max-h-64 overflow-y-auto whitespace-pre-wrap rounded-md border border-purple-100 bg-gray-900/90 p-3 text-xs text-green-200">
                            {activeStep.response_full}
                          </pre>
                        )}
                      </div>
                    );
                  })()}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-3 mb-6 overflow-hidden">
          <div 
            className="bg-gradient-to-r from-indigo-500 to-purple-600 h-3 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${((currentQuestion + 1) / parsedQuestions.length) * 100}%` }}
          ></div>
        </div>

        {/* Question Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-semibold text-gray-800">{currentQ.title}</h2>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getDifficultyColor(currentQ.difficulty)}`}>
              {currentQ.difficulty}
            </span>
          </div>
          
          {/* Code Block */}
          <div className="bg-gray-900 text-green-400 p-6 rounded-xl font-mono text-sm relative overflow-x-auto border-2 border-gray-700" ref={codeRef}>
            <div style={{ lineHeight: '28px' }}>
              {renderCodeWithClickableSpans(currentQ.parsedCode, currentQ.errorPositions)}
            </div>
            
            {/* Click indicators */}
            {clicks.map((click, index) => {
              const isCorrect = showResults && click.isCorrect;
              return (
                <div
                  key={click.id}
                  className={`absolute w-7 h-7 rounded-full border-2 flex items-center justify-center text-xs font-bold transition-all duration-300 z-10 shadow-lg ${showResults ? (isCorrect ? 'bg-green-400 border-green-600 text-white shadow-green-500/50' : 'bg-red-400 border-red-600 text-white shadow-red-500/50') : 'bg-yellow-400 border-yellow-600 text-gray-800 shadow-yellow-500/50 animate-pulse'}`}
                  style={{ 
                    left: `${click.position.x - 14}px`, 
                    top: `${click.position.y - 14}px` 
                  }}
                >
                  {index + 1}
                </div>
              );
            })}
          </div>
        </div>

        {/* Solution Display */}
        {showSolution && (
          <div className="mb-6 p-6 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl">
            <h3 className="font-bold text-green-800 mb-4 text-lg flex items-center gap-2">
              <Target className="w-5 h-5" />
              Errors in this code:
            </h3>
            <div className="space-y-4">
              {currentQ.errors.map((error, index) => (
                <div key={index} className="flex items-start gap-4 p-3 bg-white rounded-lg border border-green-100">
                  <span className="text-green-600 font-bold text-xl mt-1">✓</span>
                  <div className="flex-1">
                    <div className="font-mono text-sm bg-gray-100 px-3 py-2 rounded-md inline-block mb-2 border">
                      "{error.id}"
                    </div>
                    <div className="text-gray-700">{error.description}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Results Display */}
        {showResults && currentResult && (
          <div className="mb-6 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl">
            <h3 className="font-semibold mb-4 text-xl text-blue-800 flex items-center gap-2">
              <CheckCircle className="w-5 h-5" />
              Question Results
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white p-4 rounded-lg border shadow-sm">
                <div className="text-3xl font-bold text-blue-600 mb-1">
                  {currentResult.score.toFixed(0)}%
                </div>
                <div className="text-sm text-gray-600">This Question</div>
                <div className="mt-2 text-xs text-gray-500">
                  {currentResult.score >= 90 ? "🏆 Excellent" : 
                   currentResult.score >= 70 ? "👍 Good" : 
                   currentResult.score >= 50 ? "👌 Fair" : "📚 Study more"}
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between items-center p-2 bg-white rounded border">
                  <span className="text-sm font-medium">Errors found:</span>
                  <span className="font-bold text-green-600 flex items-center gap-1">
                    <CheckCircle className="w-4 h-4" />
                    {currentResult.correctClicks}/{currentQ.errors.length}
                  </span>
                </div>
                <div className="flex justify-between items-center p-2 bg-white rounded border">
                  <span className="text-sm font-medium">False positives:</span>
                  <span className="font-bold text-red-600 flex items-center gap-1">
                    <XCircle className="w-4 h-4" />
                    {currentResult.falsePositives}
                  </span>
                </div>
                {currentResult.falsePositives > 0 && (
                  <div className="text-xs text-blue-600 bg-blue-50 p-2 rounded border border-blue-200">
                    Impact: {currentResult.breakdown.penalty}
                  </div>
                )}
                <div className="flex justify-between items-center p-2 bg-white rounded border">
                  <span className="text-sm font-medium">Missed errors:</span>
                  <span className="font-bold text-orange-600">
                    {currentResult.missedErrors}
                  </span>
                </div>
              </div>
            </div>
            
            {/* Performance tips */}
            {showResults && (
              <div className="mt-4 p-3 bg-white rounded-lg border">
                <div className="text-sm font-medium text-gray-700 mb-2">💡 Pro Tips:</div>
                <div className="text-xs text-gray-600 space-y-1">
                  {currentResult.score < 70 && (
                    <div>• Look for conceptual errors, not just syntax issues</div>
                  )}
                  {currentResult.falsePositives > 0 && (
                    <div>• Be more selective - only click on actual errors</div>
                  )}
                  {currentResult.missedErrors > 0 && (
                    <div>• Take time to read the code carefully before clicking</div>
                  )}
                  <div>• Focus on logic errors, API misuse, and common pitfalls</div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Instructions */}
        <div className="bg-gradient-to-r from-amber-50 to-yellow-50 border-l-4 border-amber-400 p-4 mb-6 rounded-r-lg">
          <p className="text-amber-800">
            <strong>🎯 Mission:</strong> Click directly on problematic code segments to identify conceptual errors. 
            You have up to 3 clicks before auto-submission. Look for logic bugs, API misuse, and algorithmic mistakes - not just typos!
          </p>
        </div>

        {/* Controls */}
        <div className="flex justify-between items-center">
          <div className="flex gap-3 items-center">
            <button
              onClick={() => setShowSolution(!showSolution)}
              className="bg-gray-500 text-white px-4 py-2 rounded-lg font-semibold hover:bg-gray-600 transition-colors flex items-center gap-2 shadow-md"
            >
              {showSolution ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              {showSolution ? 'Hide' : 'Show'} Solution
            </button>
            <div className="flex items-center gap-2">
              <div className="text-sm text-gray-600 font-medium">
                Clicks: {clicks.length}/3
              </div>
              <div className="flex gap-1">
                {[...Array(3)].map((_, i) => (
                  <div
                    key={i}
                    className={`w-2 h-2 rounded-full ${i < clicks.length ? 'bg-indigo-500' : 'bg-gray-300'}`}
                  />
                ))}
              </div>
            </div>
          </div>
          
          <div className="flex gap-3">
            {!showResults ? (
              <button
                onClick={submitAnswer}
                disabled={clicks.length === 0}
                className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed shadow-md flex items-center gap-2"
              >
                <Target className="w-4 h-4" />
                Submit Answer
              </button>
            ) : (
              <button
                onClick={nextQuestion}
                className="bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors shadow-md flex items-center gap-2"
              >
                {currentQuestion < parsedQuestions.length - 1 ? (
                  <>Next Question →</>
                ) : (
                  <>View Final Results <Trophy className="w-4 h-4" /></>
                )}
              </button>
            )}
          </div>
        </div>

        {/* Quick Stats Footer */}
        <div className="mt-6 pt-4 border-t border-gray-200">
          <div className="flex justify-between items-center text-sm text-gray-500">
            <div>
              Progress: {Math.round(((currentQuestion + 1) / parsedQuestions.length) * 100)}% complete
            </div>
            <div className="flex items-center gap-4">
              <span>Avg Score: {currentQuestion >= 0 ? (totalScore / Math.max(1, currentQuestion + (showResults ? 1 : 0))).toFixed(0) : 0}%</span>
              <span>•</span>
              <span>Total Points: {totalScore.toFixed(0)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
