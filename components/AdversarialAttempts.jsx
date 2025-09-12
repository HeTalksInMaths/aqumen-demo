import React from 'react';
import { Target } from 'lucide-react';

const AdversarialAttempts = ({ adversarialAttempts }) => {
  if (adversarialAttempts.length === 0) return null;

  return (
    <div className="bg-gradient-to-r from-purple-800/30 to-red-800/30 rounded-lg p-6">
      <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
        <Target className="w-5 h-5" />
        Live Adversarial Loop (Task 1A)
      </h3>
      <div className="space-y-4">
        {adversarialAttempts.map((attempt) => (
          <div key={attempt.attempt} className="bg-gray-800/50 rounded-lg p-4 border-l-4 border-purple-500">
            <div className="flex justify-between items-center mb-3">
              <span className="font-medium">Attempt {attempt.attempt}/5</span>
              <span className={`px-2 py-1 rounded text-xs ${
                attempt.status === 'success' ? 'bg-green-600 text-green-100' : 
                attempt.status === 'failed' ? 'bg-red-600 text-red-100' :
                'bg-yellow-600 text-yellow-100'
              }`}>
                {attempt.status.toUpperCase()}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="bg-blue-900/30 p-3 rounded">
                <div className="font-medium text-blue-300 mb-1">Sonnet Response:</div>
                <div className="text-gray-300">{attempt.sonnetResponse}</div>
              </div>
              <div className="bg-red-900/30 p-3 rounded">
                <div className="font-medium text-red-300 mb-1">Haiku Response:</div>
                <div className="text-gray-300">{attempt.haikuResponse}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AdversarialAttempts;