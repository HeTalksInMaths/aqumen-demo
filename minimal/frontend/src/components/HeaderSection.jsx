import React from 'react';
import { Award, Loader, Sparkles } from 'lucide-react';
import PasswordModal from './PasswordModal';

const HeaderSection = ({
  isDevMode,
  viewMode,
  setViewMode,
  handleDevModeClick,
  showPasswordPrompt,
  devPassword,
  setDevPassword,
  checkDevPassword,
  cancelPasswordPrompt,
  pipelineSteps,
  generationMode,
  setGenerationMode,
  setGenerationError,
  setShowTopicInput,
  showTopicInput,
  topicInput,
  setTopicInput,
  generateNewQuestion,
  isGenerating,
  isStep1Loading,
  apiHealthy,
  generationError,
  currentQuestionIndex,
  totalQuestions,
  totalScore,
  showResults,
}) => {
  const averageScore =
    totalQuestions > 0
      ? (totalScore / Math.max(1, currentQuestionIndex + (showResults ? 1 : 0))).toFixed(0)
      : '0';

  return (
    <>
      <div className="flex justify-between items-start mb-6">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-3xl font-bold text-gray-800">AI Code Review Mastery</h1>
            <Award className="w-8 h-8 text-indigo-600" />
          </div>
          <p className="text-gray-600 text-lg">
            Hunt down conceptual errors by clicking on problematic code segments
          </p>
        </div>
        <div className="text-right">
          {totalQuestions > 0 ? (
            <div className="text-sm text-gray-500 mb-1">
              Question {currentQuestionIndex + 1} of {totalQuestions}
            </div>
          ) : (
            <div className="text-sm text-gray-500 mb-1">
              No questions yet
            </div>
          )}
          <div className="text-2xl font-bold text-indigo-600">
            Score: {totalScore.toFixed(0)}
          </div>
          <div className="text-xs text-gray-500">Average: {averageScore}%</div>
        </div>
      </div>

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
          onClick={handleDevModeClick}
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

      <PasswordModal
        isOpen={showPasswordPrompt}
        password={devPassword}
        setPassword={setDevPassword}
        onSubmit={checkDevPassword}
        onCancel={cancelPasswordPrompt}
        hint="Password is shared in internal docs."
      />


      {viewMode === 'student' && pipelineSteps.length > 0 && (
        <div className="mb-4 rounded-lg border border-purple-200 bg-purple-50 px-4 py-2 text-xs text-purple-700">
          Latest pipeline run captured. Switch to Dev Mode to inspect step details.
        </div>
      )}

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
                disabled={isGenerating || isStep1Loading || apiHealthy === false}
                className="px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2 shadow-md"
              >
                {isStep1Loading ? (
                  <>
                    <Loader className="w-4 h-4 animate-spin" />
                    Preparing categories...
                  </>
                ) : isGenerating ? (
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

        {generationMode === 'live' && showTopicInput && !isGenerating && !isStep1Loading && (
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

        {(isGenerating || isStep1Loading) && (
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center gap-3 mb-2">
              <Loader className="w-5 h-5 animate-spin text-blue-600" />
              <span className="text-sm font-medium text-blue-800">
                {isStep1Loading
                  ? `Generating difficulty categories for "${topicInput}"...`
                  : `Generating question from topic: "${topicInput}"`}
              </span>
            </div>
            <div className="text-xs text-blue-600">
              This may take 60-90 seconds as the 7-step pipeline runs...
            </div>
          </div>
        )}

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
    </>
  );
};

export default HeaderSection;
