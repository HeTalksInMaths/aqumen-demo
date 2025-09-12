import React, { useState, useRef, useEffect } from 'react';
import { Brain, Zap, Target, AlertTriangle, CheckCircle, RefreshCw, Lightbulb, Settings, Search, Cpu, Eye, EyeOff, Clock, Award } from 'lucide-react';

// API interaction layer - replace with actual API calls
const api = {
  generateDifficultyLevels: async (topic) => {
    // In a real app, this would be:
    // const response = await fetch('/api/generate_difficulty_levels', { method: 'POST', body: JSON.stringify({ topic }) });
    // return response.json();
    console.log("API CALL: generateDifficultyLevels", { topic });
    const { samplePipelineData } = await import('../constants.js');
    return new Promise(res => setTimeout(() => res(samplePipelineData[topic]?.difficultyCategories), 1500));
  },
  generateErrorCatalog: async (subtopic, difficulty) => {
    console.log("API CALL: generateErrorCatalog", { subtopic, difficulty });
    const { samplePipelineData } = await import('../constants.js');
    return new Promise(res => setTimeout(() => res(samplePipelineData['Machine Learning - Reinforcement Learning']?.conceptualErrors), 1500));
  },
  runAdversarialLoop: async (subtopic, difficulty, error) => {
    // This would be a complex backend process
    console.log("API CALL: runAdversarialLoop", { subtopic, difficulty, error });
    const { samplePipelineData } = await import('../constants.js');
    return new Promise(res => setTimeout(() => res({
        judgment: samplePipelineData['Machine Learning - Reinforcement Learning']?.judgment,
        sonnetResponse: samplePipelineData['Machine Learning - Reinforcement Learning']?.sonnetResponse,
        haikuResponse: samplePipelineData['Machine Learning - Reinforcement Learning']?.haikuResponse,
        adversarialQuestion: samplePipelineData['Machine Learning - Reinforcement Learning']?.adversarialQuestion,
    }), 3000));
  },
  createStudentAssessment: async (subtopic, difficulty, question, haikuError) => {
    console.log("API CALL: createStudentAssessment", { subtopic, difficulty, question, haikuError });
    const { samplePipelineData } = await import('../constants.js');
    return new Promise(res => setTimeout(() => res(samplePipelineData['Machine Learning - Reinforcement Learning']?.finalQuestion), 1500));
  }
};


const AqumenAdvancedDemo = () => {
  // State Management
  const [currentStep, setCurrentStep] = useState('input');
  const [userTopic, setUserTopic] = useState('Machine Learning - Reinforcement Learning');
  const [difficultyLevels, setDifficultyLevels] = useState(null);
  const [selectedDifficulty, setSelectedDifficulty] = useState(null);
  const [selectedSubtopic, setSelectedSubtopic] = useState(null);
  const [errorCatalog, setErrorCatalog] = useState(null);
  const [adversarialResult, setAdversarialResult] = useState(null);
  const [finalQuestion, setFinalQuestion] = useState(null);
  const [clicks, setClicks] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationLog, setGenerationLog] = useState([]);
  const [showDevMode, setShowDevMode] = useState(false);
  const [antiCheatTriggered, setAntiCheatTriggered] = useState(false);
  const [adversarialAttempts, setAdversarialAttempts] = useState([]);

  // Log utility
  const addLog = (message) => {
    setGenerationLog(prev => [...prev, { timestamp: new Date().toLocaleTimeString(), message }]);
  };

  // Step 1: Generate Difficulty Levels
  const handleGenerateDifficultyLevels = async () => {
    if (!userTopic.trim()) return;
    setIsGenerating(true);
    addLog(`📊 Starting pipeline for: ${userTopic}`);
    try {
      const data = await api.generateDifficultyLevels(userTopic);
      setDifficultyLevels(data);
      setCurrentStep('difficulty');
      addLog("✅ Difficulty levels generated with skill indicators.");
    } catch (error) {
      addLog(`❌ Error: ${error.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  // Step 2: Generate Error Catalog
  const handleSelectSubtopic = async (difficulty, subtopic) => {
    setSelectedDifficulty(difficulty);
    setSelectedSubtopic(subtopic);
    setIsGenerating(true);
    addLog(`🧠 Generating conceptual error catalog for ${subtopic} (${difficulty})`);
    try {
      const data = await api.generateErrorCatalog(subtopic, difficulty);
      setErrorCatalog(data);
      setCurrentStep('errors');
      addLog(`✅ Found ${data.length} common conceptual errors.`);
    } catch (error) {
      addLog(`❌ Error: ${error.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  // Steps 3-6: Adversarial Loop
  const handleRunAdversarialLoop = async (error) => {
    setIsGenerating(true);
    setCurrentStep('adversarial');
    addLog(`🎯 Running adversarial loop targeting error: "${error.mistake}"`);

    // This simulates the complex multi-step process on the backend
    try {
      // In a real app, you might get streaming updates for the loop
      const result = await api.runAdversarialLoop(selectedSubtopic, selectedDifficulty, error);
      setAdversarialResult(result);
      addLog("✅ Adversarial loop complete. Judgment received.");
    } catch (e) {
      addLog(`❌ Error in adversarial loop: ${e.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  // Step 7: Create Final Assessment
  const handleCreateAssessment = async () => {
    setIsGenerating(true);
    addLog(`📝 Creating final student assessment...`);
    try {
      const question = await api.createStudentAssessment(
        selectedSubtopic,
        selectedDifficulty,
        adversarialResult.adversarialQuestion,
        adversarialResult.haikuResponse
      );
      setFinalQuestion(question);
      setCurrentStep('assessment');
      addLog("✅ Student assessment created with embedded, clickable errors.");
    } catch(e) {
      addLog(`❌ Error creating assessment: ${e.message}`);
    } finally {
      setIsGenerating(false);
    }
  };


  // UI Interaction Handlers
  const handleErrorClick = (errorId) => {
    const newClicks = new Set(clicks);
    if (newClicks.has(errorId)) newClicks.delete(errorId);
    else newClicks.add(errorId);
    setClicks(Array.from(newClicks));
  };

  const evaluateResponse = () => {
    if (!finalQuestion) return;
    const correctErrors = new Set(finalQuestion.errors.filter(e => e.severity !== 'trick').map(e => e.id));
    const selectedErrors = new Set(clicks);
    const intersection = new Set([...selectedErrors].filter(x => correctErrors.has(x)));
    const precision = selectedErrors.size > 0 ? intersection.size / selectedErrors.size : 0;
    const recall = correctErrors.size > 0 ? intersection.size / correctErrors.size : 0;
    const f1 = precision + recall > 0 ? 2 * (precision * recall) / (precision + recall) : 0;
    setShowResults({ precision, recall, f1, correctErrors, selectedErrors });
  };

  // Reset flow
  const reset = () => {
      setCurrentStep('input');
      setDifficultyLevels(null);
      setErrorCatalog(null);
      setAdversarialResult(null);
      setFinalQuestion(null);
      setClicks([]);
      setShowResults(false);
      setGenerationLog([]);
  }

  // Make error click handler available globally for dangerouslySetInnerHTML
  useEffect(() => {
    window.handleErrorClick = handleErrorClick;
    return () => delete window.handleErrorClick;
  }, [clicks]);

  // Main Render
  return (
    <div className="max-w-7xl mx-auto p-6 bg-gradient-to-br from-gray-900 to-blue-900 min-h-screen text-white">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent mb-4">
          Aqumen.ai Advanced Demo
        </h1>
        <p className="text-xl text-gray-300 mb-4">
          Multi-Model Adversarial Pipeline for Intelligent Error Detection
        </p>
      </div>

      {/* Step 1: Topic Input */}
      {currentStep === 'input' && (
        <div className="bg-gray-800/50 backdrop-blur rounded-lg shadow-xl p-8 mb-6">
          <h2 className="text-3xl font-bold mb-6 text-center">Enter Assessment Topic</h2>
          <div className="max-w-2xl mx-auto">
            <div className="mb-6">
              <label className="block text-lg font-medium mb-2">Domain/Subject:</label>
              <input
                type="text"
                value={userTopic}
                onChange={(e) => setUserTopic(e.target.value)}
                placeholder="e.g., Machine Learning - Reinforcement Learning"
                className="w-full p-4 text-lg bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
              />
            </div>
            <div className="text-center">
              <button
                onClick={handleGenerateDifficultyLevels}
                disabled={!userTopic.trim() || isGenerating}
                className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold disabled:opacity-50 hover:from-blue-700 hover:to-purple-700 transition-all"
              >
                {isGenerating ? "Analyzing Topic..." : "Start Pipeline Analysis"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Step 2: Difficulty & Subtopic Selection */}
      {currentStep === 'difficulty' && difficultyLevels && (
        <div className="bg-gray-800/50 backdrop-blur rounded-lg shadow-xl p-8 mb-6">
          <h2 className="text-3xl font-bold mb-6">Select Difficulty & Subtopic</h2>
          {Object.entries(difficultyLevels).map(([difficulty, data]) => (
            <div key={difficulty} className="mb-8">
              <h3 className="text-2xl font-semibold mb-4 text-blue-300">{difficulty} Level</h3>
              <p className="text-sm text-gray-400 italic mb-1">Skill: {data.skill_level}</p>
              <p className="text-sm text-gray-400 italic mb-4">Est. Time to Learn: {data.time_to_learn}</p>
              <div className="grid md:grid-cols-3 gap-4">
                {data.subtopics.map((subtopic) => (
                  <button
                    key={subtopic}
                    onClick={() => handleSelectSubtopic(difficulty, subtopic)}
                    disabled={isGenerating}
                    className="p-4 bg-gray-700 border border-gray-600 rounded-lg hover:border-blue-500 hover:bg-gray-600 transition-all text-left disabled:opacity-50"
                  >
                    <div className="font-medium text-gray-200">{subtopic}</div>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Step 3: Error Catalog */}
      {currentStep === 'errors' && errorCatalog && (
          <div className="bg-gray-800/50 backdrop-blur rounded-lg shadow-xl p-8 mb-6">
              <h2 className="text-3xl font-bold mb-6">Select Target Error</h2>
              <p className="text-lg text-gray-300 mb-4">Select a common conceptual error to build a question around.</p>
                <div className="space-y-4">
                    {errorCatalog.map((error, idx) => (
                        <button key={idx} onClick={() => handleRunAdversarialLoop(error)} disabled={isGenerating}
                        className="w-full text-left p-4 bg-gray-700 border border-gray-600 rounded-lg hover:border-purple-500 hover:bg-gray-600 transition-all disabled:opacity-50">
                            <p className="font-semibold text-purple-300">{error.mistake}</p>
                            <p className="text-sm text-gray-400 mt-1">{error.why_wrong}</p>
                            <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                                <span>Likelihood: {(error.likelihood * 100).toFixed(0)}%</span>
                                <span>Impact: {error.impact}</span>
                                <span>Difficulty to Spot: {error.difficulty_to_spot}</span>
                            </div>
                        </button>
                    ))}
                </div>
          </div>
      )}

      {/* Step 4: Adversarial Loop Result */}
      {currentStep === 'adversarial' && (
           <div className="bg-gray-800/50 backdrop-blur rounded-lg shadow-xl p-8 mb-6">
              <h2 className="text-3xl font-bold mb-6">Adversarial Loop Judgment</h2>
              {isGenerating && <p>Running models... this may take a moment.</p>}
              {adversarialResult && (
                  <div>
                      <p className="text-lg text-gray-300 mb-4">Opus has judged the model responses. Differentiation quality: <span className="font-bold text-green-400">{adversarialResult.judgment.differentiation_quality.toUpperCase()}</span></p>
                       <div className="text-center mt-8">
                           <button onClick={handleCreateAssessment} disabled={isGenerating}
                           className="px-8 py-4 bg-gradient-to-r from-purple-600 to-red-600 text-white rounded-lg font-semibold disabled:opacity-50 hover:from-purple-700 hover:to-red-700 transition-all">
                               {isGenerating ? "Generating..." : "Create Student Assessment"}
                           </button>
                       </div>
                  </div>
              )}
          </div>
      )}

      {/* Step 5: Assessment Question */}
      {currentStep === 'assessment' && finalQuestion && (
        <div className="space-y-6">
          <div className="bg-gradient-to-r from-purple-800/50 to-blue-800/50 rounded-lg p-6">
            <h2 className="text-3xl font-bold mb-2">{finalQuestion.title}</h2>
            <p className="text-gray-300 mb-4">{finalQuestion.learning_objective}</p>
          </div>
          <div className="bg-gray-800/50 backdrop-blur rounded-lg p-6">
            <h3 className="text-xl font-bold mb-4">Code/Reasoning to Review:</h3>
            <pre className="bg-gray-900 p-6 rounded-lg overflow-x-auto text-sm">
              <code dangerouslySetInnerHTML={{ __html: finalQuestion.code.replace(/<span class="error-span.*?"/g, (match) => `${match} onclick="window.handleErrorClick(this.dataset.errorId)"`) }} />
            </pre>
          </div>
          <div className="bg-gray-800/50 backdrop-blur rounded-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold">Assessment Evaluation</h3>
              <div className="flex gap-3">
                <button onClick={evaluateResponse} className="px-6 py-2 bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-lg font-medium">
                  Evaluate Response
                </button>
                <button onClick={reset} className="px-6 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium">
                  New Assessment
                </button>
              </div>
            </div>
            {showResults && (
              <div className="mt-6 grid md:grid-cols-3 gap-4">
                <div className="bg-blue-900/30 p-4 text-center rounded-lg"><div className="text-2xl font-bold">{(showResults.precision * 100).toFixed(1)}%</div><div className="text-sm">Precision</div></div>
                <div className="bg-green-900/30 p-4 text-center rounded-lg"><div className="text-2xl font-bold">{(showResults.recall * 100).toFixed(1)}%</div><div className="text-sm">Recall</div></div>
                <div className="bg-purple-900/30 p-4 text-center rounded-lg"><div className="text-2xl font-bold">{(showResults.f1 * 100).toFixed(1)}%</div><div className="text-sm">F1 Score</div></div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Generation Log */}
      {generationLog.length > 0 && (
        <div className="bg-gray-800/50 backdrop-blur rounded-lg shadow-xl p-6 mt-6">
           <h3 className="text-xl font-bold flex items-center gap-2 mb-4"><Settings className="w-5 h-5" />Pipeline Execution Log</h3>
           <div className="space-y-2 max-h-48 overflow-y-auto">
              {generationLog.map((log, index) => (
                <div key={index} className="flex items-start gap-3 text-sm">
                  <span className="text-gray-500 font-mono text-xs">{log.timestamp}</span>
                  <span className="text-gray-300">{log.message}</span>
                </div>
              ))}
            </div>
        </div>
      )}
    </div>
  );
};

export default AqumenAdvancedDemo;