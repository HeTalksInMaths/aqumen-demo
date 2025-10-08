import React, { useState, useRef, useEffect } from 'react';
import { CheckCircle, XCircle, RotateCcw, Trophy, Eye, EyeOff, Target, Award } from 'lucide-react';

const App = () => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [clicks, setClicks] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const [gameComplete, setGameComplete] = useState(false);
  const [totalScore, setTotalScore] = useState(0);
  const [showSolution, setShowSolution] = useState(false);
  const [currentResult, setCurrentResult] = useState(null);
  const [parsedQuestions, setParsedQuestions] = useState([]);
  const codeRef = useRef(null);

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

  // Parse questions with delimiters on component mount
  useEffect(() => {
    const parsed = rawQuestions.map(question => parseQuestion(question));
    setParsedQuestions(parsed);
  }, []);

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

  if (parsedQuestions.length === 0) {
    return (
      <div className="flex justify-center items-center h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <div className="text-gray-600">Loading AI Code Review Challenge...</div>
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