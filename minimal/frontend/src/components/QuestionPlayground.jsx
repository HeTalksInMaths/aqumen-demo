import React from 'react';
import {
  CheckCircle,
  XCircle,
  Eye,
  EyeOff,
  Target,
} from 'lucide-react';

const spanBaseStyle = { whiteSpace: 'pre' };

const QuestionPlayground = ({
  currentQuestion,
  progressPercent,
  difficultyClass,
  codeRef,
  clicks,
  showResults,
  currentResult,
  showSolution,
  setShowSolution,
  submitAnswer,
  nextQuestion,
  hasMoreQuestions,
  currentQuestionIndex,
  totalQuestions,
  totalScore,
  handleErrorClick,
  handleLineClick,
}) => {
  const renderCodeWithClickableSpans = () =>
    currentQuestion.parsedCode.map((line, lineIndex) => {
      const lineErrors = currentQuestion.errorPositions.filter(
        (error) => error.line === lineIndex
      );

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

      const sortedErrors = [...lineErrors].sort((a, b) => a.startPos - b.startPos);

      const segments = [];
      let lastPos = 0;

      sortedErrors.forEach((error) => {
        if (error.startPos > lastPos) {
          segments.push({
            text: line.substring(lastPos, error.startPos),
            isError: false,
            lineIndex,
          });
        }

        segments.push({
          text: error.text,
          isError: true,
          errorId: error.id,
          lineIndex,
        });

        lastPos = error.endPos;
      });

      if (lastPos < line.length) {
        segments.push({
          text: line.substring(lastPos),
          isError: false,
          lineIndex,
        });
      }

      return (
        <div
          key={lineIndex}
          className="relative group"
          data-line={lineIndex}
          onClick={(event) => {
            if (event.target === event.currentTarget) {
              handleLineClick(event, lineIndex);
            }
          }}
        >
          <span className="text-gray-500 mr-4 select-none text-right inline-block w-8 text-xs">
            {lineIndex + 1}
          </span>
          {segments.map((segment, segIndex) => (
            <span
              key={segIndex}
              className="cursor-pointer transition-all duration-200 rounded px-1 hover:bg-gray-700 hover:bg-opacity-50"
              style={spanBaseStyle}
              onClick={(e) =>
                segment.isError
                  ? handleErrorClick(e, segment.errorId, segment.lineIndex)
                  : handleLineClick(e, segment.lineIndex)
              }
              title={segment.isError ? 'Click to identify this error' : ''}
            >
              {segment.text}
            </span>
          ))}
        </div>
      );
    });

  return (
    <>
      <div className="w-full bg-gray-200 rounded-full h-3 mb-6 overflow-hidden">
        <div
          className="bg-gradient-to-r from-indigo-500 to-purple-600 h-3 rounded-full transition-all duration-500 ease-out"
          style={{ width: `${progressPercent}%` }}
        ></div>
      </div>

      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-semibold text-gray-800">{currentQuestion.title}</h2>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${difficultyClass}`}>
            {currentQuestion.difficulty}
          </span>
        </div>

        <div
          className="bg-gray-900 text-green-400 p-6 rounded-xl font-mono text-sm relative overflow-x-auto border-2 border-gray-700"
          ref={codeRef}
          onClick={(event) => {
            if (showResults || clicks.length >= 3) {
              return;
            }
            const lineElement = event.target.closest('[data-line]');
            if (lineElement) {
              return;
            }
            handleLineClick(event, 0);
          }}
        >
          <div style={{ lineHeight: '28px' }}>{renderCodeWithClickableSpans()}</div>

          {clicks.map((click) => {
            const isCorrect = showResults && click.isCorrect;
            return (
              <div
                key={click.id}
                className={`absolute w-7 h-7 rounded-full border-2 flex items-center justify-center text-xs font-bold transition-all duration-300 z-10 shadow-lg ${
                  showResults
                    ? isCorrect
                      ? 'bg-green-400 border-green-600 text-white shadow-green-500/50'
                      : 'bg-red-400 border-red-600 text-white shadow-red-500/50'
                    : 'bg-yellow-400 border-yellow-600 text-gray-800 shadow-yellow-500/50 animate-pulse'
                }`}
                style={{
                  left: `${click.position.x - 14}px`,
                  top: `${click.position.y - 14}px`,
                }}
              >
                {clicks.indexOf(click) + 1}
              </div>
            );
          })}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
        <div className="bg-indigo-50 rounded-xl border border-indigo-100 p-4 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-indigo-700 font-medium">Your Score</span>
            <CheckCircle className="w-4 h-4 text-indigo-500" />
          </div>
          <div className="text-3xl font-bold text-indigo-600">
            {showResults ? currentResult.score.toFixed(0) : '—'}%
          </div>
          <div className="text-xs text-indigo-500 mt-1">
            {totalQuestions > 0
              ? `Question ${currentQuestionIndex + 1} of ${totalQuestions}`
              : 'No questions yet'}
          </div>
        </div>

        <div className="bg-emerald-50 rounded-xl border border-emerald-100 p-4 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-emerald-700 font-medium">Correctly Identified</span>
            <CheckCircle className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-3xl font-bold text-emerald-600">
            {showResults ? currentResult.correctClicks : '—'}
          </div>
          <div className="text-xs text-emerald-500 mt-1">True positives</div>
        </div>

        <div className="bg-rose-50 rounded-xl border border-rose-100 p-4 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-rose-700 font-medium">Misfires</span>
            <XCircle className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-3xl font-bold text-rose-600">
            {showResults ? currentResult.falsePositives : '—'}
          </div>
          <div className="text-xs text-rose-500 mt-1">False positives</div>
        </div>
      </div>

      {showResults && currentResult && (
        <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white rounded-lg border shadow-sm p-4">
            <div className="flex justify-between items-center p-2 bg-white rounded border">
              <span className="text-sm font-medium text-gray-700">Correct errors:</span>
              <span className="font-bold text-green-600">{currentResult.correctClicks}</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-white rounded border">
              <span className="text-sm font-medium text-gray-700">False positives:</span>
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
              <span className="text-sm font-medium text-gray-700">Missed errors:</span>
              <span className="font-bold text-orange-600">{currentResult.missedErrors}</span>
            </div>
          </div>

          <div className="bg-white rounded-lg border shadow-sm p-4">
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
        </div>
      )}

      <div className="bg-gradient-to-r from-amber-50 to-yellow-50 border-l-4 border-amber-400 p-4 mb-6 rounded-r-lg">
        <p className="text-amber-800">
          <strong>🎯 Mission:</strong> Click directly on problematic code segments to identify conceptual
          errors. You have up to 3 clicks before auto-submission. Look for logic bugs, API misuse, and
          algorithmic mistakes - not just typos!
        </p>
      </div>

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
                  className={`w-2 h-2 rounded-full ${
                    i < clicks.length ? 'bg-indigo-500' : 'bg-gray-300'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>

        <div className="flex gap-3">
          {!showResults ? (
            <button
              onClick={submitAnswer}
              className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors shadow-md flex items-center gap-2"
            >
              <Target className="w-4 h-4" />
              Submit Answer
            </button>
          ) : (
            <button
              onClick={nextQuestion}
              className="bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors shadow-md flex items-center gap-2"
            >
              {hasMoreQuestions ? (
                <>Next Question →</>
              ) : (
                <>View Final Results</>
              )}
            </button>
          )}
        </div>
      </div>

      {showSolution && (
        <div className="mt-6 mb-6 bg-blue-50 border border-blue-200 rounded-xl p-6 shadow-md">
          <div className="flex items-center gap-2 mb-4">
            <Eye className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-semibold text-blue-900">Solution: All Errors</h3>
          </div>
          <div className="space-y-3">
            {currentQuestion.errors && currentQuestion.errors.length > 0 ? (
              currentQuestion.errors.map((error, index) => (
                <div
                  key={index}
                  className="bg-white rounded-lg border border-blue-200 p-4 shadow-sm"
                >
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-bold">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <div className="font-mono text-sm text-red-600 bg-red-50 px-2 py-1 rounded mb-2 inline-block">
                        {error.id}
                      </div>
                      <p className="text-sm text-gray-700">{error.description}</p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-sm text-gray-600 italic">No errors defined for this question.</div>
            )}
          </div>
        </div>
      )}

      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex justify-between items-center text-sm text-gray-500">
          <div>Progress: {Math.round(progressPercent)}% complete</div>
          <div className="flex items-center gap-4">
            <span>
              Avg Score:{' '}
              {currentQuestionIndex >= 0
                ? (totalScore / Math.max(1, currentQuestionIndex + (showResults ? 1 : 0))).toFixed(0)
                : 0}
              %
            </span>
            <span>•</span>
            <span>Total Points: {totalScore.toFixed(0)}</span>
          </div>
        </div>
      </div>
    </>
  );
};

export default QuestionPlayground;
