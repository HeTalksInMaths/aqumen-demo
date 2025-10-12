import React from 'react';
import { Sparkles } from 'lucide-react';

const LiveEmptyState = ({ isDevMode, apiHealthy }) => (
  <div className="flex flex-col items-center justify-center py-16 px-4">
    <Sparkles className="w-16 h-16 text-indigo-400 mb-4" />
    <h2 className="text-2xl font-bold text-gray-800 mb-2">No Questions Yet</h2>
    <p className="text-gray-600 text-center max-w-md mb-6">
      {isDevMode
        ? 'Generate a new question using the "Generate New Question" button above to see the 7-step pipeline in action.'
        : 'Generate a new question using the "Generate New Question" button above to start the assessment.'}
    </p>
    {apiHealthy === false && (
      <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg max-w-md">
        <p className="text-sm text-red-800">
          <strong>⚠️ Backend API is offline</strong>
        </p>
        <p className="text-xs text-red-600 mt-1">
          Make sure FastAPI is running on port 8000 before generating questions.
        </p>
      </div>
    )}
  </div>
);

export default LiveEmptyState;
