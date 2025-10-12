import React from 'react';
import { Trophy, RotateCcw } from 'lucide-react';

const FinalResults = ({ totalScore, percentage, parsedQuestionsLength, resetGame }) => (
  <div className="max-w-4xl mx-auto p-6 bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
    <div className="bg-white rounded-lg shadow-2xl p-8 text-center">
      <Trophy className="w-20 h-20 text-yellow-500 mx-auto mb-6" />
      <h2 className="text-4xl font-bold text-gray-800 mb-4">Challenge Complete!</h2>
      <div className="text-7xl font-bold text-indigo-600 mb-4">{totalScore.toFixed(0)}</div>
      <div className="text-2xl text-gray-600 mb-8">Final Score ({percentage}% accuracy)</div>

      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 mb-8">
        <div className="text-lg font-semibold text-gray-700 mb-3">Your Code Review Rating:</div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg shadow-sm p-4 border border-indigo-100">
            <div className="text-sm text-gray-500 mb-1">Total Score</div>
            <div className="text-2xl font-bold text-indigo-600">{totalScore.toFixed(0)}</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-4 border border-blue-100">
            <div className="text-sm text-gray-500 mb-1">Accuracy</div>
            <div className="text-2xl font-bold text-blue-600">{percentage}%</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-4 border border-purple-100">
            <div className="text-sm text-gray-500 mb-1">Questions</div>
            <div className="text-2xl font-bold text-purple-600">{parsedQuestionsLength}</div>
          </div>
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

export default FinalResults;
