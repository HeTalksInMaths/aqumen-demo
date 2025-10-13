import React, { useState, useRef, useEffect, useMemo } from 'react';
import { fetchQuestionStreaming, checkAPIHealth, fetchPrompts, fetchStep1Categories } from './api';
import HeaderSection from './components/HeaderSection';
import PipelinePanel from './components/PipelinePanel';
import LiveEmptyState from './components/LiveEmptyState';
import QuestionPlayground from './components/QuestionPlayground';
import FinalResults from './components/FinalResults';
import { studentModeQuestions } from './demoData.student';
import { demoAssessments, demoPipelineSteps } from './demoData.dev';
import { pipelineBlueprint, pipelineDemoCopy } from './pipelineBlueprint';
import { parseQuestion } from './utils/parseQuestion.js';

const DemoLoadingScreen = () => (
  <div className="flex justify-center items-center h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
      <div className="text-gray-600">Loading AI Code Review Challenge...</div>
    </div>
  </div>
);

const App = () => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [gameComplete, setGameComplete] = useState(false);
  const [totalScore, setTotalScore] = useState(0);
  const [parsedQuestions, setParsedQuestions] = useState([]);
  const [generationMode, setGenerationMode] = useState('demo');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationError, setGenerationError] = useState(null);
  const [showTopicInput, setShowTopicInput] = useState(false);
  const [topicInput, setTopicInput] = useState('');
  const [viewMode, setViewMode] = useState('student');
  const [pipelineSteps, setPipelineSteps] = useState([]);
  const [pipelineFinal, setPipelineFinal] = useState(null);
  const [streamingCleanup, setStreamingCleanup] = useState(null);
  const [apiHealthy, setApiHealthy] = useState(null);
  const [activePipelineTab, setActivePipelineTab] = useState(null);
  const [devPassword, setDevPassword] = useState('');
  const [showPasswordPrompt, setShowPasswordPrompt] = useState(false);
  const [isDevUnlocked, setIsDevUnlocked] = useState(false);
  const [backendPrompts, setBackendPrompts] = useState(null);
  const [step1Result, setStep1Result] = useState(null);
  const [showCategoryPicker, setShowCategoryPicker] = useState(false);
  const [selectedDifficulty, setSelectedDifficulty] = useState('');
  const [selectedSubtopic, setSelectedSubtopic] = useState('');
  const [isStep1Loading, setIsStep1Loading] = useState(false);
  const [currentDevAssessmentIndex, setCurrentDevAssessmentIndex] = useState(0);

  const blueprintSteps = useMemo(() => {
    if (!backendPrompts) {
      // Use placeholder prompts if backend prompts not yet loaded
      return pipelineBlueprint.map((step) => ({ ...step, isPlaceholder: true }));
    }

    // Map backend prompts to blueprint steps
    const promptMapping = {
      1: 'step1_difficulty_categories',
      2: 'step2_error_catalog',
      3: 'step3_strategic_question',
      4: 'step4_test_sonnet',
      5: 'step5_test_haiku',
      6: 'step6_judge_responses',
      7: 'step7_student_assessment',
    };

    return pipelineBlueprint.map((step) => {
      const promptKey = promptMapping[step.step_number];
      const backendPrompt = backendPrompts[promptKey];

      return {
        ...step,
        prompt: backendPrompt?.template || step.prompt,
        title: backendPrompt?.description || step.title,
        isPlaceholder: !backendPrompt,
      };
    });
  }, [backendPrompts]);

  // Student mode demo questions - imported from demoData.student.js
  const rawQuestions = useMemo(() => studentModeQuestions, []);

  const isDevMode = viewMode === 'dev';

  useEffect(() => {
    if (!activePipelineTab && blueprintSteps.length > 0) {
      setActivePipelineTab(blueprintSteps[0]._id);
    }
  }, [activePipelineTab, blueprintSteps]);

  useEffect(() => {
    if (generationMode === 'demo') {
      if (viewMode === 'dev') {
        // Load all available assessments (no cap)
        if (demoAssessments.length > 0) {
          // Ensure index is within bounds
          const safeIndex = Math.min(currentDevAssessmentIndex, demoAssessments.length - 1);
          if (safeIndex !== currentDevAssessmentIndex) {
            setCurrentDevAssessmentIndex(safeIndex);
          }
          const currentAssessment = demoAssessments[safeIndex];

          // Convert demoAssessment to question format
          const demoQuestion = {
            title: currentAssessment.title,
            topic: currentAssessment.topic,
            subtopic: currentAssessment.subtopic,
            difficulty: currentAssessment.difficulty,
            code: currentAssessment.content,
            errors: currentAssessment.errors,
          };

          const parsed = parseQuestion(demoQuestion);
          setParsedQuestions([parsed]);
          setCurrentQuestion(0);
          setGameComplete(false);
          setTotalScore(0);
          // Load the corresponding pipeline steps for this assessment
          const assessmentPipelineSteps = demoPipelineSteps.filter(
            step => step._id.includes(`demo-${safeIndex + 1}-step-`)
          );
          setPipelineSteps(assessmentPipelineSteps);
          setPipelineFinal({
            title: currentAssessment.title,
            difficulty: currentAssessment.difficulty,
            success: true,
            differentiation_achieved: true,
            total_attempts: 1,
            stopped_at_step: 7,
            metadata: {
              topic: currentAssessment.topic,
              topic_requested: currentAssessment.topic,
              subtopic: currentAssessment.subtopic,
              run_timestamp: currentAssessment.run_timestamp,
              weak_model_failures: currentAssessment.errors?.length || 0,
            },
          });
          setActivePipelineTab('final');
        } else {
          setParsedQuestions([]);
          setCurrentQuestion(0);
          setGameComplete(false);
          setTotalScore(0);
          setPipelineSteps([]);
          setPipelineFinal(null);
          setActivePipelineTab(blueprintSteps[0]?._id || null);
        }
      } else {
        setParsedQuestions(rawQuestions.map((question) => parseQuestion(question)));
        setPipelineSteps([]);
        setPipelineFinal(null);
        setActivePipelineTab(blueprintSteps[0]?._id || null);
      }
    } else {
      setParsedQuestions([]);
      setCurrentQuestion(0);
      setPipelineSteps([]);
      setPipelineFinal(null);
      setActivePipelineTab(blueprintSteps[0]?._id || null);

      checkAPIHealth().then((healthy) => {
        setApiHealthy(healthy);
        if (!healthy) {
          setGenerationError('Backend API is not reachable. Make sure FastAPI is running on port 8000.');
        }
      });
    }
  }, [blueprintSteps, generationMode, rawQuestions, viewMode, currentDevAssessmentIndex]);

  useEffect(() => {
    return () => {
      if (streamingCleanup) {
        streamingCleanup();
      }
    };
  }, [streamingCleanup]);

  // Fetch real prompts from backend on mount
  useEffect(() => {
    const loadPrompts = async () => {
      try {
        const prompts = await fetchPrompts();
        setBackendPrompts(prompts);
        console.log('Backend prompts loaded successfully');
      } catch (error) {
        console.error('Failed to load backend prompts, using placeholders:', error);
        // Keep using placeholder prompts if fetch fails
      }
    };

    loadPrompts();
  }, []);


  const registerGeneratedQuestion = (parsedQuestion) => {
    setParsedQuestions((prev) => {
      const updated = [...prev, parsedQuestion];
      setCurrentQuestion(updated.length - 1);
      return updated;
    });
    setGameComplete(false);
  };

  const resetLiveState = () => {
    setPipelineSteps([]);
    setPipelineFinal(null);
    setParsedQuestions([]);
    setCurrentQuestion(0);
    setActivePipelineTab(blueprintSteps[0]?._id || null);
    setTotalScore(0);
    setGameComplete(false);
    setStep1Result(null);
    setShowCategoryPicker(false);
    setSelectedDifficulty('');
    setSelectedSubtopic('');
  };

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

    resetLiveState();

    setGenerationError(null);
    setIsStep1Loading(true);

    try {
      const result = await fetchStep1Categories(normalizedTopic);
      setStep1Result(result);

      const difficulties = Object.keys(result.categories || {});
      const defaultDifficulty = difficulties[0] || '';
      const defaultSubtopic =
        (defaultDifficulty && result.categories[defaultDifficulty]?.[0]) || '';

      setSelectedDifficulty(defaultDifficulty);
      setSelectedSubtopic(defaultSubtopic);
      setShowCategoryPicker(true);
    } catch (error) {
      console.error('Step 1 generation failed:', error);
      setGenerationError(error.message || 'Failed to generate difficulty categories.');
    } finally {
      setIsStep1Loading(false);
    }
  };

  const startLiveGeneration = (difficulty, subtopic) => {
    if (!topicInput.trim()) {
      return;
    }

    if (streamingCleanup) {
      streamingCleanup();
      setStreamingCleanup(null);
    }

    resetLiveState();

    setIsGenerating(true);
    setGenerationError(null);
    setShowCategoryPicker(false);
    setStep1Result(null);
    setShowTopicInput(false);

    const normalizedTopic = topicInput.trim();

    const handleStepUpdate = (stepData) => {
      const enrichedStep = {
        ...stepData,
        _id: `${stepData.step_number}-${Date.now()}-${Math.random().toString(16).slice(2)}`,
      };
      setPipelineSteps((prev) => {
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
        difficulty: question.difficulty,
      });
      setActivePipelineTab('final');
      setIsGenerating(false);
      setTopicInput('');
      setShowTopicInput(false);
      setStreamingCleanup(null);
      setSelectedDifficulty('');
      setSelectedSubtopic('');
    };

    const handleError = (error) => {
      console.error('Streaming generation error:', error);
      setGenerationError(error.message || 'Failed to generate question. Please try again.');
      setIsGenerating(false);
      setStreamingCleanup(null);
      setActivePipelineTab(blueprintSteps[0]?._id || null);
    };

    try {
      const cleanup = fetchQuestionStreaming(
        normalizedTopic,
        3,
        handleStepUpdate,
        handleComplete,
        handleError,
        difficulty,
        subtopic
      );
      setStreamingCleanup(() => cleanup);
    } catch (error) {
      console.error('Streaming initialization error:', error);
      setGenerationError(error.message || 'Failed to start streaming generation. Please try again.');
      setIsGenerating(false);
    }
  };

  const cancelCategorySelection = () => {
    setShowCategoryPicker(false);
    setStep1Result(null);
    setSelectedDifficulty('');
    setSelectedSubtopic('');
  };

  const confirmCategorySelection = () => {
    if (!selectedDifficulty || !selectedSubtopic) {
      alert('Select a difficulty and subtopic to continue.');
      return;
    }
    startLiveGeneration(selectedDifficulty, selectedSubtopic);
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
    switch (difficulty) {
      case 'Beginner':
        return 'bg-green-100 text-green-800';
      case 'Intermediate':
        return 'bg-yellow-100 text-yellow-800';
      case 'Advanced':
        return 'bg-orange-100 text-orange-800';
      case 'Expert':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const submitAnswer = () => {
    // This function is now called by the QuestionPlayground component
    // when the user clicks "Show answers". We can add scoring logic here
    // in the future if needed, but for now, it's just a placeholder.
  };

  const nextQuestion = () => {
    if (currentQuestion < parsedQuestions.length - 1) {
      setCurrentQuestion((prev) => prev + 1);
    } else {
      setGameComplete(true);
    }
  };

  const resetGame = () => {
    setCurrentQuestion(0);
    setGameComplete(false);
    setTotalScore(0);
  };

  const handleDevModeClick = () => {
    if (!isDevUnlocked) {
      setShowPasswordPrompt(true);
    } else {
      setViewMode('dev');
    }
  };

  const checkDevPassword = () => {
    const correctPassword = import.meta.env.VITE_DEV_PASSWORD || 'menaqu';
    if (devPassword === correctPassword) {
      setIsDevUnlocked(true);
      setViewMode('dev');
      setShowPasswordPrompt(false);
      setDevPassword('');
    } else {
      alert('Incorrect password');
      setDevPassword('');
    }
  };

  const cancelPasswordPrompt = () => {
    setShowPasswordPrompt(false);
    setDevPassword('');
  };

  if (!isDevMode && parsedQuestions.length === 0 && generationMode === 'demo') {
    return <DemoLoadingScreen />;
  }

  if (gameComplete) {
    const maxScore = parsedQuestions.length * 100;
    const percentage = parsedQuestions.length > 0 ? Math.round((totalScore / maxScore) * 100) : 0;

    return (
      <FinalResults
        totalScore={totalScore}
        percentage={percentage}
        parsedQuestionsLength={parsedQuestions.length}
        resetGame={resetGame}
      />
    );
  }

  const currentQ = parsedQuestions[currentQuestion];
  const hasQuestions = parsedQuestions.length > 0;
  const progressPercent = hasQuestions
    ? ((currentQuestion + 1) / parsedQuestions.length) * 100
    : 0;

  return (
    <div className="max-w-7xl mx-auto p-6 bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
      <div className="bg-white rounded-lg shadow-2xl p-6">
        <HeaderSection
          isDevMode={isDevMode}
          viewMode={viewMode}
          setViewMode={setViewMode}
          handleDevModeClick={handleDevModeClick}
          showPasswordPrompt={showPasswordPrompt}
          devPassword={devPassword}
          setDevPassword={setDevPassword}
          checkDevPassword={checkDevPassword}
          cancelPasswordPrompt={cancelPasswordPrompt}
          pipelineSteps={pipelineSteps}
          generationMode={generationMode}
          setGenerationMode={setGenerationMode}
          setGenerationError={setGenerationError}
          setShowTopicInput={setShowTopicInput}
          showTopicInput={showTopicInput}
          topicInput={topicInput}
          setTopicInput={setTopicInput}
          generateNewQuestion={generateNewQuestion}
          isGenerating={isGenerating}
          isStep1Loading={isStep1Loading}
          apiHealthy={apiHealthy}
          generationError={generationError}
          currentQuestionIndex={currentQuestion}
          totalQuestions={parsedQuestions.length}
          totalScore={totalScore}
        />

        {isDevMode && generationMode === 'demo' && demoAssessments.length > 0 && (
          <div className="mb-4 border-b border-gray-200">
            <div className="flex items-center gap-4 pb-3">
              <label className="text-sm font-medium text-gray-700">Select Assessment:</label>
              <select
                value={currentDevAssessmentIndex}
                onChange={(e) => setCurrentDevAssessmentIndex(parseInt(e.target.value))}
                className="px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white"
              >
                {demoAssessments.map((assessment, index) => (
                  <option key={assessment.id} value={index}>
                    {assessment.topic} ({assessment.difficulty} • {assessment.errors?.length || 0} errors)
                  </option>
                ))}
              </select>
              <span className="text-xs text-gray-500">
                {currentDevAssessmentIndex + 1} of {demoAssessments.length} assessments
              </span>
            </div>
          </div>
        )}

        {isDevMode && (
          <PipelinePanel
            pipelineSteps={pipelineSteps}
            pipelineFinal={pipelineFinal}
            activePipelineTab={activePipelineTab}
            setActivePipelineTab={setActivePipelineTab}
            isGenerating={isGenerating}
            generationMode={generationMode}
            formatTimestamp={formatTimestamp}
            preloadedSteps={blueprintSteps}
            demoDescription={pipelineDemoCopy}
          />
        )}

        {!hasQuestions ? (
          <LiveEmptyState isDevMode={isDevMode} apiHealthy={apiHealthy} />
        ) : (
          <QuestionPlayground
            currentQuestion={currentQ}
            progressPercent={progressPercent}
            difficultyClass={getDifficultyColor(currentQ.difficulty)}
            onSubmit={submitAnswer}
            onNext={nextQuestion}
            hasMoreQuestions={currentQuestion < parsedQuestions.length - 1}
          />
        )}
      </div>
      {showCategoryPicker && step1Result && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="w-full max-w-3xl rounded-xl bg-white p-6 shadow-2xl">
            <h2 className="text-xl font-semibold text-gray-800">Select Focus Area</h2>
            <p className="mt-1 text-sm text-gray-600">
              Step 1 generated difficulty buckets for “{step1Result.topic}”. Choose where to focus before
              the pipeline continues.
            </p>
            <div className="mt-4 grid gap-3 md:grid-cols-3">
              {Object.entries(step1Result.categories || {}).map(([difficulty, subtopics]) => (
                <div
                  key={difficulty}
                  className={`rounded-lg border p-3 transition-colors ${
                    selectedDifficulty === difficulty
                      ? 'border-indigo-500 bg-indigo-50'
                      : 'border-gray-200 bg-white'
                  }`}
                >
                  <button
                    type="button"
                    className="w-full text-left text-sm font-semibold text-indigo-700"
                    onClick={() => {
                      setSelectedDifficulty(difficulty);
                      setSelectedSubtopic(subtopics?.[0] || '');
                    }}
                  >
                    {difficulty}
                  </button>
                  <ul className="mt-2 space-y-1 text-xs text-gray-600">
                    {subtopics.map((subtopic) => (
                      <li key={subtopic}>
                        <label className="flex cursor-pointer items-center gap-2">
                          <input
                            type="radio"
                            name={`subtopic-${difficulty}`}
                            className="text-indigo-600 focus:ring-indigo-500"
                            checked={selectedDifficulty === difficulty && selectedSubtopic === subtopic}
                            onChange={() => {
                              setSelectedDifficulty(difficulty);
                              setSelectedSubtopic(subtopic);
                            }}
                          />
                          <span>{subtopic}</span>
                        </label>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                className="rounded-lg bg-gray-200 px-4 py-2 text-sm text-gray-700 hover:bg-gray-300"
                onClick={cancelCategorySelection}
              >
                Cancel
              </button>
              <button
                type="button"
                className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-700 disabled:bg-gray-400"
                disabled={!selectedDifficulty || !selectedSubtopic}
                onClick={confirmCategorySelection}
              >
                Continue to Step 2
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
