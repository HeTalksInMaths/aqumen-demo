import React from 'react';

const DifficultySelection = ({ 
  difficultyCategories, 
  isGenerating, 
  onSelectSubtopic 
}) => {
  if (!difficultyCategories) return null;

  return (
    <div className="bg-gray-800/50 backdrop-blur rounded-lg shadow-xl p-8 mb-6">
      <h2 className="text-3xl font-bold mb-6">Select Difficulty & Subtopic</h2>
      
      {Object.entries(difficultyCategories).map(([difficulty, subtopics]) => (
        <div key={difficulty} className="mb-8">
          <h3 className="text-2xl font-semibold mb-4 text-blue-300">{difficulty} Level</h3>
          <div className="grid md:grid-cols-3 gap-4">
            {subtopics.map((subtopic) => (
              <button
                key={subtopic}
                onClick={() => onSelectSubtopic(difficulty, subtopic)}
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
  );
};

export default DifficultySelection;