import React, { useState } from 'react';
import { Loader, ChevronDown, ChevronRight, Edit, Save } from 'lucide-react';

const PipelinePanel = ({
  pipelineSteps,
  pipelineFinal,
  activePipelineTab,
  setActivePipelineTab,
  isGenerating,
  generationMode,
  formatTimestamp,
  preloadedSteps = [],
  demoDescription = 'Gold-standard pipeline walkthrough',
}) => {
  const [expandedSteps, setExpandedSteps] = useState({});
  const [editingPrompts, setEditingPrompts] = useState({});
  const [promptOverrides, setPromptOverrides] = useState({});

  const toggleStepExpanded = (stepId) => {
    setExpandedSteps(prev => ({
      ...prev,
      [stepId]: !prev[stepId]
    }));
  };

  const handlePromptEdit = (stepId, newPrompt) => {
    setPromptOverrides(prev => ({
      ...prev,
      [stepId]: newPrompt
    }));
  };

  const toggleEditMode = (stepId) => {
    setEditingPrompts(prev => ({
      ...prev,
      [stepId]: !prev[stepId]
    }));
  };

  const savePromptToFile = async (stepId) => {
    const prompt = promptOverrides[stepId];
    if (!prompt) return;

    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    try {
      const response = await fetch(`${API_BASE_URL}/api/update-prompt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          step: stepId,
          new_prompt: prompt
        })
      });

      if (response.ok) {
        alert('Prompt saved to pipeline!');
        setEditingPrompts(prev => ({ ...prev, [stepId]: false }));
      } else {
        alert('Failed to save prompt');
      }
    } catch (error) {
      console.error('Error saving prompt:', error);
      alert('Error saving prompt');
    }
  };

  const hasRuntimeSteps = pipelineSteps.length > 0;
  // In demo mode, only show actual pipeline steps, not blueprint placeholders
  const stepsToRender = generationMode === 'demo' ? pipelineSteps : (hasRuntimeSteps ? pipelineSteps : preloadedSteps);
  const showPlaceholderSteps = generationMode !== 'demo' && !hasRuntimeSteps && stepsToRender.length > 0;
  const showPromptEditor = generationMode !== 'demo'; // Only show prompt editor in live generation mode

  const getStatusBadge = (success) => {
    if (success === true) {
      return { text: '✅ Success', className: 'bg-green-100 text-green-800' };
    }
    if (success === false) {
      return { text: '⚠️ Attention', className: 'bg-red-100 text-red-800' };
    }
    return { text: '⏳ Pending', className: 'bg-gray-200 text-gray-700' };
  };

  return (
    <div className="mb-6 rounded-xl border border-purple-200 bg-white p-4 shadow-inner">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div>
          <h2 className="text-lg font-semibold text-purple-800">Pipeline Execution</h2>
          <p className="text-xs text-gray-500">
            {generationMode === 'demo'
              ? demoDescription
              : 'Live stream of the 7-step pipeline from FastAPI (SSE)'}
          </p>
        </div>
        {isGenerating ? (
          <span className="flex items-center gap-2 text-sm font-medium text-indigo-600">
            <Loader className="w-4 h-4 animate-spin" />
            Streaming…
          </span>
        ) : pipelineFinal ? (
          <span
            className={`text-xs font-semibold px-2 py-1 rounded ${
              pipelineFinal.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}
          >
            {pipelineFinal.success ? '✅ Last run succeeded' : '⚠️ Review last run'}
          </span>
        ) : null}
      </div>

      {stepsToRender.length === 0 && !pipelineFinal ? (
        <div className="rounded-lg border border-dashed border-purple-200 bg-purple-50/60 p-4 text-sm text-purple-700">
          {isGenerating
            ? 'Waiting for the first pipeline step…'
            : 'Run a live generation to stream each step of the pipeline here.'}
        </div>
      ) : (
        <div>
          {/* Step Tabs */}
          <div className="mb-4 flex flex-wrap gap-2">
            {stepsToRender.map((step, index) => {
              const fallbackTab = hasRuntimeSteps
                ? pipelineSteps[pipelineSteps.length - 1]?._id
                : stepsToRender[0]?._id;
              const isActive = (activePipelineTab ?? fallbackTab) === step._id;
              return (
                <button
                  key={step._id || `${step.step_number}-${index}`}
                  onClick={() => setActivePipelineTab(step._id)}
                  className={`rounded-lg px-3 py-2 text-xs font-medium transition-colors ${
                    isActive
                      ? 'bg-purple-600 text-white shadow'
                      : 'bg-purple-50 text-purple-700 border border-purple-200 hover:bg-purple-100'
                  }`}
                >
                  Step {step.step_number}
                </button>
              );
            })}
            {pipelineFinal && (
              <button
                onClick={() => setActivePipelineTab('final')}
                className={`rounded-lg px-3 py-2 text-xs font-medium transition-colors ${
                  (activePipelineTab || (!activePipelineTab && pipelineFinal)) === 'final'
                    ? 'bg-green-600 text-white shadow'
                    : 'bg-green-50 text-green-700 border border-green-200 hover:bg-green-100'
                }`}
              >
                Final Assessment
              </button>
            )}
          </div>

          {/* Step Content */}
          <div className="rounded-lg border border-purple-100 bg-white p-4 text-sm text-gray-700">
            {(() => {
              const resolvedTab = (() => {
                if (activePipelineTab) return activePipelineTab;
                if (pipelineFinal && hasRuntimeSteps) return 'final';
                if (hasRuntimeSteps) {
                  return pipelineSteps[pipelineSteps.length - 1]?._id || null;
                }
                return stepsToRender[0]?._id || null;
              })();

              if (resolvedTab === 'final' && pipelineFinal && hasRuntimeSteps) {
                return (
                  <div>
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div>
                        <div className="font-semibold text-gray-800">
                          Final Question: {pipelineFinal.title || 'Generated Assessment'}
                        </div>
                        <div className="text-xs text-gray-500">
                          Topic: {pipelineFinal.metadata?.topic || pipelineFinal.metadata?.topic_requested || 'N/A'} · Difficulty: {pipelineFinal.difficulty || 'Unknown'}
                        </div>
                      </div>
                      <span className={`text-sm font-semibold ${pipelineFinal.success ? 'text-green-600' : 'text-red-600'}`}>
                        {pipelineFinal.success ? '✅ Generation succeeded' : '⚠️ Generation failed'}
                      </span>
                    </div>
                    <div className="mt-3 grid gap-2 text-xs text-gray-600 sm:grid-cols-2">
                      <div>Attempts: {pipelineFinal.total_attempts ?? '—'}</div>
                      <div>Weak model failures: {pipelineFinal.metadata?.weak_model_failures ?? '—'}</div>
                      <div>Differentiation achieved: {pipelineFinal.differentiation_achieved ? 'Yes' : 'No'}</div>
                      <div>Stopped at step: {pipelineFinal.stopped_at_step ?? '—'}</div>
                    </div>
                    <div className="mt-3 text-xs text-gray-500">
                      Tip: toggle back to Student Mode to focus on the playable question.
                    </div>
                  </div>
                );
              }

              const activeStep =
                stepsToRender.find(step => step._id === resolvedTab) ||
                (hasRuntimeSteps
                  ? pipelineSteps[pipelineSteps.length - 1]
                  : stepsToRender[0]);

              if (!activeStep) {
                return <div className="text-xs text-gray-500">Awaiting pipeline updates…</div>;
              }

              const stepKey = activeStep._id || `step-${activeStep.step_number}`;
              const isExpanded = expandedSteps[stepKey];
              const isEditing = editingPrompts[stepKey];
              const editingDisabled = false; // Editing is always enabled when prompt editor is visible
              const currentPrompt =
                promptOverrides[stepKey] || activeStep.prompt || 'No prompt available';
              const statusBadge = getStatusBadge(activeStep.success);

              return (
                <div>
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div className="flex-1">
                      <div className="font-semibold text-gray-800">
                        Step {activeStep.step_number}: {activeStep.title || activeStep.description || 'Unnamed step'}
                      </div>
                      <div className="mt-1 text-xs text-gray-500">
                        Model: {activeStep.model || '—'} · {formatTimestamp(activeStep.timestamp)}
                      </div>
                    </div>
                    <span className={`text-xs font-semibold px-2 py-1 rounded ${statusBadge.className}`}>
                      {statusBadge.text}
                    </span>
                  </div>

                  {/* Expandable Prompt Editor - Only show in live generation mode */}
                  {showPromptEditor && (
                    <div className="mt-4">
                      <button
                        onClick={() => toggleStepExpanded(stepKey)}
                        className="flex items-center gap-2 text-sm font-medium text-purple-700 hover:text-purple-900"
                      >
                        {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                        View/Edit Prompt
                      </button>

                      {isExpanded && (
                        <div className="mt-3 border border-purple-200 rounded-lg p-3 bg-purple-50">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-medium text-gray-700">Step {activeStep.step_number} Prompt</span>
                            <div className="flex gap-2">
                              {!isEditing ? (
                                <button
                                  onClick={() => toggleEditMode(stepKey)}
                                  disabled={editingDisabled}
                                  className={`flex items-center gap-1 px-2 py-1 text-xs rounded ${
                                    editingDisabled
                                      ? 'bg-purple-200 text-purple-400 cursor-not-allowed'
                                      : 'bg-purple-600 text-white hover:bg-purple-700'
                                  }`}
                                >
                                  <Edit className="w-3 h-3" />
                                  Edit
                                </button>
                              ) : (
                                <>
                                  <button
                                    onClick={() => savePromptToFile(stepKey)}
                                    disabled={editingDisabled}
                                    className={`flex items-center gap-1 px-2 py-1 text-xs rounded ${
                                      editingDisabled
                                        ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                                        : 'bg-green-600 text-white hover:bg-green-700'
                                    }`}
                                  >
                                    <Save className="w-3 h-3" />
                                    Update in Pipeline
                                  </button>
                                  <button
                                    onClick={() => toggleEditMode(stepKey)}
                                    className="px-2 py-1 text-xs bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
                                  >
                                    Cancel
                                  </button>
                                </>
                              )}
                            </div>
                          </div>

                          {isEditing ? (
                            <textarea
                              value={currentPrompt}
                              onChange={(e) => handlePromptEdit(stepKey, e.target.value)}
                              className="w-full h-48 p-2 text-xs font-mono bg-white border border-purple-300 rounded focus:outline-none focus:ring-2 focus:ring-purple-500"
                              placeholder="Enter prompt..."
                            />
                          ) : (
                            <pre className="whitespace-pre-wrap text-xs font-mono bg-white p-3 rounded border border-purple-200 max-h-48 overflow-y-auto">
                              {currentPrompt}
                            </pre>
                          )}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Response Output */}
                  {activeStep.response_full && (
                    <div className="mt-4">
                      <div className="text-xs font-medium text-gray-700 mb-2">Response:</div>
                      <pre className="max-h-64 overflow-y-auto whitespace-pre-wrap rounded-md border border-purple-100 bg-gray-900/90 p-3 text-xs text-green-200">
                        {activeStep.response_full}
                      </pre>
                    </div>
                  )}

                  {showPlaceholderSteps && !activeStep.response_full && (
                    <div className="mt-4 rounded-lg border border-dashed border-purple-200 bg-purple-50/60 p-3 text-xs text-purple-700">
                      Run a live generation to stream the full responses for each step.
                    </div>
                  )}
                </div>
              );
            })()}
          </div>
        </div>
      )}
    </div>
  );
};

export default PipelinePanel;
