import React from 'react';
import { Brain, Target, Zap } from 'lucide-react';

const Header = () => {
  return (
    <div className="text-center mb-8">
      <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent mb-4">
        Aqumen.ai Advanced Demo
      </h1>
      <p className="text-xl text-gray-300 mb-4">
        Multi-Model Adversarial Pipeline for Intelligent Error Detection
      </p>
      <div className="flex justify-center items-center gap-4 text-sm text-gray-400">
        <div className="flex items-center gap-1">
          <Brain className="w-4 h-4" />
          <span>Opus: Analysis & Judgment</span>
        </div>
        <div className="flex items-center gap-1">
          <Target className="w-4 h-4" />
          <span>Sonnet: Sweet Spot Validation</span>
        </div>
        <div className="flex items-center gap-1">
          <Zap className="w-4 h-4" />
          <span>Haiku: Authentic Weak Errors</span>
        </div>
      </div>
    </div>
  );
};

export default Header;