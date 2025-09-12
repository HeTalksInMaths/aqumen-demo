import React from 'react';
import { usePipelineState, useAdversarialAttempts, useErrorClicks, useAdversarialPipeline } from './hooks.js';
import { generateDifficultyCategories } from './utils.js';
import Header from './components/Header.jsx';
import AntiCheatAlert from './components/AntiCheatAlert.jsx';
import TopicInput from './components/TopicInput.jsx';
import DifficultySelection from './components/DifficultySelection.jsx';
import GenerationLog from './components/GenerationLog.jsx';
import AdversarialAttempts from './components/AdversarialAttempts.jsx';
import AssessmentQuestion from './components/AssessmentQuestion.jsx';
import ResultsDisplay from './components/ResultsDisplay.jsx';
import Footer from './components/Footer.jsx';

const AqumenAdvancedDemoModular = () => {
  // Custom hooks for state management
  const pipelineState = usePipelineState();
  const adversarialHooks = useAdversarialAttempts();
  const errorClickHooks = useErrorClicks();
  const { runAdversarialPipeline } = useAdversarialPipeline(pipelineState, adversarialHooks);

  // Destructure states for easier access
  const { 
    currentStep, 
    userTopic, 
    difficultyCategories, 
    selectedSubtopic, 
    finalQuestion, 
    showResults, 
    isGenerating, 
    antiCheatTriggered,
    setCurrentStep,
    setUserTopic,
    setDifficultyCategories,
    setSelectedDifficulty,
    setSelectedSubtopic,
    setShowResults,
    setIsGenerating
  } = pipelineState;

  const { 
    adversarialAttempts, 
    generationLog, 
    showDevMode, 
    setShowDevMode, 
    addLog, 
    retryCount 
  } = adversarialHooks;

  const { clicks, handleErrorClick } = errorClickHooks;

  // Handler functions
  const handleGenerateDifficulties = async (topic) => {
    await generateDifficultyCategories(
      topic, 
      setDifficultyCategories, 
      setCurrentStep, 
      addLog, 
      setIsGenerating
    );
  };

  const handleSelectSubtopic = (difficulty, subtopic) => {
    setSelectedDifficulty(difficulty);
    setSelectedSubtopic(subtopic);
    runAdversarialPipeline(difficulty, subtopic);
  };

  return (
    <div className="max-w-7xl mx-auto p-6 bg-gradient-to-br from-gray-900 to-blue-900 min-h-screen text-white">
      <Header />
      
      <AntiCheatAlert antiCheatTriggered={antiCheatTriggered} />

      {/* Step 1: Topic Input */}
      {currentStep === 'input' && (
        <TopicInput
          userTopic={userTopic}
          setUserTopic={setUserTopic}
          isGenerating={isGenerating}
          onGenerateDifficulties={handleGenerateDifficulties}
        />
      )}

      {/* Step 2: Difficulty & Subtopic Selection */}
      {currentStep === 'difficulty' && (
        <DifficultySelection
          difficultyCategories={difficultyCategories}
          isGenerating={isGenerating}
          onSelectSubtopic={handleSelectSubtopic}
        />
      )}

      {/* Generation Log and Adversarial Attempts */}
      {generationLog.length > 0 && (
        <div className="space-y-6">
          <GenerationLog
            generationLog={generationLog}
            retryCount={retryCount}
            showDevMode={showDevMode}
            setShowDevMode={setShowDevMode}
          />
          
          <AdversarialAttempts adversarialAttempts={adversarialAttempts} />
        </div>
      )}

      {/* Step 3: Assessment Question */}
      {currentStep === 'assessment' && (
        <div>
          <AssessmentQuestion
            finalQuestion={finalQuestion}
            selectedSubtopic={selectedSubtopic}
            clicks={clicks}
            handleErrorClick={handleErrorClick}
            setShowResults={setShowResults}
            setCurrentStep={setCurrentStep}
          />
          <ResultsDisplay showResults={showResults} />
        </div>
      )}

      <Footer />
    </div>
  );
};

export default AqumenAdvancedDemoModular;