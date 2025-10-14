import React from 'react';

const ResultsDisplay = ({ showResults }) => {
  if (!showResults) return null;

  return (
    <div className="mt-6 grid md:grid-cols-4 gap-4">
      <div className="bg-blue-900/30 border border-blue-600 rounded-lg p-4 text-center">
        <div className="text-2xl font-bold text-blue-300">{(showResults.precision * 100).toFixed(1)}%</div>
        <div className="text-sm text-blue-400">Precision</div>
      </div>
      <div className="bg-green-900/30 border border-green-600 rounded-lg p-4 text-center">
        <div className="text-2xl font-bold text-green-300">{(showResults.recall * 100).toFixed(1)}%</div>
        <div className="text-sm text-green-400">Recall</div>
      </div>
      <div className="bg-purple-900/30 border border-purple-600 rounded-lg p-4 text-center">
        <div className="text-2xl font-bold text-purple-300">{(showResults.f1 * 100).toFixed(1)}%</div>
        <div className="text-sm text-purple-400">F1 Score</div>
      </div>
      <div className="bg-yellow-900/30 border border-yellow-600 rounded-lg p-4 text-center">
        <div className="text-2xl font-bold text-yellow-300">{showResults.conceptualUnderstanding}%</div>
        <div className="text-sm text-yellow-400">Conceptual</div>
      </div>
    </div>
  );
};

export default ResultsDisplay;