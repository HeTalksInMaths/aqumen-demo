import React from 'react';
import { Brain, Target, AlertTriangle } from 'lucide-react';
import { evaluateResponse } from '../utils.js';

const AssessmentQuestion = ({ 
  finalQuestion, 
  selectedSubtopic, 
  clicks, 
  handleErrorClick,
  setShowResults,
  setCurrentStep 
}) => {
  if (!finalQuestion) return null;

  const renderCodeWithErrors = (code) => {
    return (
      <div 
        dangerouslySetInnerHTML={{
          __html: code.replace(
            /<span class="error-span ([^"]*)" data-error-id="([^"]*)" data-concept="([^"]*)">(.*?)<\/span>/g,
            (match, classes, errorId, concept, content) => {
              const isSelected = clicks.includes(errorId);
              const error = finalQuestion.errors.find(e => e.id === errorId);
              const tightnessClass = classes.includes('tight') ? 'border-2' : 'border';
              const selectedClass = isSelected ? 'bg-red-100 border-red-500' : 'bg-yellow-100 border-yellow-500';
              
              return `<span 
                class="error-span-interactive ${tightnessClass} ${selectedClass} px-1 rounded cursor-pointer hover:bg-red-50 transition-colors" 
                onclick="window.handleErrorClick?.('${errorId}')"
                title="Concept: ${concept} | Severity: ${error?.severity || 'unknown'} | Inspired by ${error?.inspired_by_haiku ? 'Haiku' : 'designed'} errors"
              >${content}</span>`;
            }
          )
        }}
      />
    );
  };

  const handleEvaluateResponse = () => {
    const results = evaluateResponse(finalQuestion, clicks);
    setShowResults(results);
  };

  return (
    <div className="space-y-6">
      {/* Question Header */}
      <div className="bg-gradient-to-r from-purple-800/50 to-blue-800/50 rounded-lg p-6">
        <h2 className="text-3xl font-bold mb-2">{finalQuestion.title}</h2>
        <p className="text-gray-300 mb-4">
          Find conceptual errors in this {selectedSubtopic} implementation. 
          {finalQuestion.errors.filter(e => e.severity === 'trick').length > 0 && 
            " Note: Some code may be intentionally correct."}
        </p>
        
        <div className="flex items-center gap-4 text-sm text-gray-400">
          <div className="flex items-center gap-1">
            <Brain className="w-4 h-4" />
            <span>Haiku-inspired errors: {finalQuestion.errors.filter(e => e.inspired_by_haiku).length}</span>
          </div>
          <div className="flex items-center gap-1">
            <Target className="w-4 h-4" />
            <span>Tight spans: {finalQuestion.errors.filter(e => e.span_tightness === 'tight').length}</span>
          </div>
          <div className="flex items-center gap-1">
            <AlertTriangle className="w-4 h-4" />
            <span>Trick questions: {finalQuestion.errors.filter(e => e.severity === 'trick').length}</span>
          </div>
        </div>
      </div>

      {/* Code Display */}
      <div className="bg-gray-800/50 backdrop-blur rounded-lg p-6">
        <h3 className="text-xl font-bold mb-4">Code/Reasoning to Review:</h3>
        <pre className="bg-gray-900 p-6 rounded-lg overflow-x-auto text-sm">
          <code>{renderCodeWithErrors(finalQuestion.code)}</code>
        </pre>
      </div>

      {/* Evaluation Controls */}
      <div className="bg-gray-800/50 backdrop-blur rounded-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold">Assessment Evaluation</h3>
          <div className="flex gap-3">
            <button
              onClick={handleEvaluateResponse}
              className="px-6 py-2 bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-lg font-medium hover:from-green-700 hover:to-blue-700 transition-all"
            >
              Evaluate Response
            </button>
            <button
              onClick={() => setCurrentStep('input')}
              className="px-6 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium transition-colors"
            >
              New Assessment
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssessmentQuestion;