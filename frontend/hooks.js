import { useState, useRef, useEffect } from 'react';
import { MODELS, samplePipelineData } from './constants.js';
import { makeAPICall, createFallbackQuestion } from './utils.js';

// Custom hook for pipeline state management
export const usePipelineState = () => {
  const [currentStep, setCurrentStep] = useState('input');
  const [userTopic, setUserTopic] = useState('');
  const [difficultyCategories, setDifficultyCategories] = useState(null);
  const [selectedDifficulty, setSelectedDifficulty] = useState(null);
  const [selectedSubtopic, setSelectedSubtopic] = useState(null);
  const [conceptualErrors, setConceptualErrors] = useState(null);
  const [generatedQuestion, setGeneratedQuestion] = useState(null);
  const [modelResponses, setModelResponses] = useState(null);
  const [judgment, setJudgment] = useState(null);
  const [finalQuestion, setFinalQuestion] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const [antiCheatTriggered, setAntiCheatTriggered] = useState(false);

  return {
    currentStep,
    setCurrentStep,
    userTopic,
    setUserTopic,
    difficultyCategories,
    setDifficultyCategories,
    selectedDifficulty,
    setSelectedDifficulty,
    selectedSubtopic,
    setSelectedSubtopic,
    conceptualErrors,
    setConceptualErrors,
    generatedQuestion,
    setGeneratedQuestion,
    modelResponses,
    setModelResponses,
    judgment,
    setJudgment,
    finalQuestion,
    setFinalQuestion,
    showResults,
    setShowResults,
    isGenerating,
    setIsGenerating,
    retryCount,
    setRetryCount,
    antiCheatTriggered,
    setAntiCheatTriggered
  };
};

// Custom hook for adversarial attempts and logging
export const useAdversarialAttempts = () => {
  const [adversarialAttempts, setAdversarialAttempts] = useState([]);
  const [generationLog, setGenerationLog] = useState([]);
  const [showDevMode, setShowDevMode] = useState(false);

  const addLog = (message) => {
    setGenerationLog(prev => [...prev, { 
      timestamp: new Date().toLocaleTimeString(), 
      message 
    }]);
  };

  const showAttemptInProgress = (attempt) => {
    setAdversarialAttempts(prev => [...prev, {
      attempt: attempt,
      status: 'testing',
      sonnetResponse: 'Analyzing...',
      haikuResponse: 'Generating...',
      timestamp: Date.now()
    }]);
  };

  const updateAttemptResults = (attempt, sonnetResult, haikuResult) => {
    setAdversarialAttempts(prev => prev.map(att => 
      att.attempt === attempt 
        ? {
            ...att,
            sonnetResponse: attempt <= 2 ? "✅ Correctly identifies the error" : "✅ Provides comprehensive analysis",
            haikuResponse: attempt <= 2 ? "❌ Misses the conceptual issue" : attempt === 3 ? "✅ Actually got it right (retry needed)" : "❌ Falls for the semantic trap"
          }
        : att
    ));
  };

  const updateAttemptStatus = (attempt, status) => {
    setAdversarialAttempts(prev => prev.map(att => 
      att.attempt === attempt ? { ...att, status } : att
    ));
  };

  return {
    adversarialAttempts,
    setAdversarialAttempts,
    generationLog,
    setGenerationLog,
    showDevMode,
    setShowDevMode,
    addLog,
    showAttemptInProgress,
    updateAttemptResults,
    updateAttemptStatus,
    retryCount: 0 // placeholder value for now
  };
};

// Custom hook for error click management
export const useErrorClicks = () => {
  const [clicks, setClicks] = useState([]);
  const problemRef = useRef(null);

  const handleErrorClick = (errorId) => {
    const newClicks = new Set(clicks);
    if (newClicks.has(errorId)) {
      newClicks.delete(errorId);
    } else {
      newClicks.add(errorId);
    }
    setClicks(Array.from(newClicks));
  };

  // Make error click handler available globally for dangerouslySetInnerHTML
  useEffect(() => {
    window.handleErrorClick = handleErrorClick;
    return () => delete window.handleErrorClick;
  }, [clicks]);

  return {
    clicks,
    setClicks,
    handleErrorClick,
    problemRef
  };
};

// Custom hook for adversarial pipeline execution
export const useAdversarialPipeline = (pipelineState, adversarialHooks) => {
  const { 
    setIsGenerating, 
    setRetryCount, 
    setConceptualErrors, 
    setFinalQuestion, 
    setCurrentStep,
    userTopic 
  } = pipelineState;
  
  const { 
    setAdversarialAttempts, 
    addLog, 
    showAttemptInProgress, 
    updateAttemptResults, 
    updateAttemptStatus 
  } = adversarialHooks;

  const runAdversarialPipeline = async (difficulty, subtopic) => {
    setIsGenerating(true);
    setRetryCount(0);
    setAdversarialAttempts([]); // Clear previous attempts
    addLog(`🎯 Running adversarial pipeline for ${subtopic} (${difficulty})`);

    try {
      // Step 2: Opus generates conceptual error catalog
      addLog("🧠 Step 2: Generating conceptual error catalog (Opus)");
      await makeAPICall(MODELS.STRONG, "Generate domain-specific errors", "Error catalog generation (Opus)", addLog);
      
      const errors = samplePipelineData[userTopic]?.conceptualErrors || [];
      setConceptualErrors(errors);

      // Step 3: Opus generates adversarial question
      addLog("🎯 Step 3: Generating adversarial question (Opus)");
      await makeAPICall(MODELS.STRONG, "Generate question targeting specific errors", "Question generation (Opus)", addLog);

      // Step 4 & 5: Parallel model testing with retry logic
      let success = false;
      let attempts = 0;
      const maxAttempts = 5;

      while (!success && attempts < maxAttempts) {
        attempts++;
        setRetryCount(attempts);
        
        // Show attempt in progress
        showAttemptInProgress(attempts);
        
        addLog(`🔄 Attempt ${attempts}: Testing model differentiation`);

        // Parallel testing with live updates
        const [sonnetResult, haikuResult] = await Promise.all([
          makeAPICall(MODELS.MID, "Test question", "Sonnet validation", addLog),
          makeAPICall(MODELS.WEAK, "Test question", "Haiku testing", addLog)
        ]);

        // Update attempt with results
        updateAttemptResults(attempts, sonnetResult, haikuResult);

        // Step 6: Opus judgment
        addLog("⚖️ Step 6: Judging model responses (Opus)");
        await makeAPICall(MODELS.STRONG, "Judge differentiation", "Response judgment (Opus)", addLog);

        // Simulate success criteria: Sonnet ✅ + Haiku ❌
        success = attempts >= 3 || Math.random() > 0.4; // Increase success chance over attempts
        
        if (!success && attempts < maxAttempts) {
          addLog(`❌ Attempt ${attempts} failed: Insufficient differentiation, retrying...`);
          updateAttemptStatus(attempts, 'failed');
          await new Promise(resolve => setTimeout(resolve, 1000));
        } else if (success) {
          updateAttemptStatus(attempts, 'success');
        }
      }

      if (success) {
        addLog("✅ Pipeline successful: Model differentiation achieved");
        
        // Step 7: Generate final student question with tight error spans
        addLog("📝 Step 7: Creating student assessment (Opus)");
        await makeAPICall(MODELS.STRONG, "Create final question", "Student question creation (Opus)", addLog);
        
        const finalQ = samplePipelineData[userTopic]?.finalQuestion || createFallbackQuestion();
        setFinalQuestion(finalQ);
        setCurrentStep('assessment');
        
      } else {
        addLog(`❌ Pipeline failed after ${maxAttempts} attempts: Unable to achieve model differentiation`);
      }

    } catch (error) {
      addLog(`❌ Pipeline error: ${error.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  return { runAdversarialPipeline };
};