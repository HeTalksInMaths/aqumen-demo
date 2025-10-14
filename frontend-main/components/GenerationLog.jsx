import React from 'react';
import { Settings, RefreshCw, Eye, EyeOff } from 'lucide-react';

const GenerationLog = ({ 
  generationLog, 
  retryCount, 
  showDevMode, 
  setShowDevMode 
}) => {
  if (generationLog.length === 0) return null;

  return (
    <div className="bg-gray-800/50 backdrop-blur rounded-lg shadow-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold flex items-center gap-2">
          <Settings className="w-5 h-5" />
          Pipeline Execution Log
        </h3>
        <div className="flex items-center gap-4 text-sm text-gray-400">
          {retryCount > 0 && (
            <div className="flex items-center gap-1">
              <RefreshCw className="w-4 h-4" />
              <span>Retry: {retryCount}/5</span>
            </div>
          )}
          <button
            onClick={() => setShowDevMode(!showDevMode)}
            className="flex items-center gap-1 px-2 py-1 bg-gray-700 rounded text-xs hover:bg-gray-600"
          >
            {showDevMode ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
            Dev Mode
          </button>
        </div>
      </div>
      
      <div className={`space-y-2 ${showDevMode ? 'max-h-96 overflow-y-auto' : 'max-h-32 overflow-hidden'}`}>
        {generationLog.map((log, index) => (
          <div key={index} className="flex items-start gap-3 text-sm">
            <span className="text-gray-500 font-mono text-xs">{log.timestamp}</span>
            <span className="text-gray-300">{log.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GenerationLog;