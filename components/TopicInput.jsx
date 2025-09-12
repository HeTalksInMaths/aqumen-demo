import React from 'react';
import { RefreshCw } from 'lucide-react';

const TopicInput = ({ 
  userTopic, 
  setUserTopic, 
  isGenerating, 
  onGenerateDifficulties 
}) => {
  return (
    <div className="bg-gray-800/50 backdrop-blur rounded-lg shadow-xl p-8 mb-6">
      <h2 className="text-3xl font-bold mb-6 text-center">Enter Assessment Topic</h2>
      <div className="max-w-2xl mx-auto">
        <div className="mb-6">
          <label className="block text-lg font-medium mb-2">Domain/Subject:</label>
          <input
            type="text"
            value={userTopic}
            onChange={(e) => setUserTopic(e.target.value)}
            placeholder="e.g., Machine Learning - Reinforcement Learning, Data Structures - Trees, Computer Vision - CNNs"
            className="w-full p-4 text-lg bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
          />
        </div>
        <div className="text-center">
          <button
            onClick={() => onGenerateDifficulties(userTopic)}
            disabled={!userTopic.trim() || isGenerating}
            className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold disabled:opacity-50 hover:from-blue-700 hover:to-purple-700 transition-all"
          >
            {isGenerating ? (
              <div className="flex items-center gap-2">
                <RefreshCw className="w-5 h-5 animate-spin" />
                Analyzing Topic...
              </div>
            ) : (
              'Start Pipeline Analysis'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default TopicInput;