/**
 * API Module for Adversarial Pipeline Integration
 * Connects React frontend to FastAPI backend
 */

const API_BASE_URL = (() => {
  if (typeof import.meta !== 'undefined' && import.meta?.env?.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  if (typeof process !== 'undefined' && process?.env?.VITE_API_URL) {
    return process.env.VITE_API_URL;
  }
  return 'http://localhost:8000';
})();

/**
 * Fetch a question from the pipeline (blocking - waits for complete result)
 * @param {string} topic - The AI/ML topic to generate a question about
 * @param {number} maxRetries - Maximum retry attempts for differentiation
 * @returns {Promise<Object>} - Question in React format
 */
export const fetchQuestionBlocking = async (
  topic,
  maxRetries = 3,
  { selectedDifficulty, selectedSubtopic } = {}
) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        topic,
        max_retries: maxRetries,
        selected_difficulty: selectedDifficulty,
        selected_subtopic: selectedSubtopic
      })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `API Error: ${response.status}`);
    }

    const data = await response.json();

    if (!data.success) {
      throw new Error(data.error || 'Pipeline failed to generate question');
    }

    return transformStep7ToReact(data.assessment);
  } catch (error) {
    console.error('Failed to fetch question:', error);
    throw error;
  }
};

/**
 * Fetch question using SSE streaming (real-time updates)
 * @param {string} topic - The AI/ML topic
 * @param {number} maxRetries - Maximum retry attempts
 * @param {Function} onStepUpdate - Callback for each step update (stepData) => void
 * @param {Function} onComplete - Callback when complete (question) => void
 * @param {Function} onError - Callback for errors (error) => void
 * @returns {Function} - Cleanup function to close the connection
 */
export const fetchQuestionStreaming = (
  topic,
  maxRetries,
  onStepUpdate,
  onComplete,
  onError,
  selectedDifficulty,
  selectedSubtopic
) => {
  const params = new URLSearchParams({
    topic,
    max_retries: String(maxRetries)
  });

  if (selectedDifficulty) {
    params.append('selected_difficulty', selectedDifficulty);
  }
  if (selectedSubtopic) {
    params.append('selected_subtopic', selectedSubtopic);
  }

  const url = `${API_BASE_URL}/api/generate-stream?${params.toString()}`;

  const eventSource = new EventSource(url);
  let completed = false;

  eventSource.addEventListener('start', (event) => {
    const data = JSON.parse(event.data);
    console.log('Pipeline started:', data.timestamp);
  });

  eventSource.addEventListener('step', (event) => {
    const data = JSON.parse(event.data);

    if (data.type === 'step') {
      onStepUpdate?.(data);
    } else if (data.type === 'final') {
      completed = true;
      eventSource.close();

      if (data.success && data.assessment) {
        const question = transformStep7ToReact(data.assessment);
        onComplete?.(question, data);
      } else {
        onError?.(new Error(data.error || 'Pipeline completed but no assessment generated'));
      }
    }
  });

  eventSource.addEventListener('error', (event) => {
    if (!completed) {
      eventSource.close();

      // Try to get error details
      let errorMsg = 'Connection to pipeline failed';
      if (event.data) {
        try {
          const data = JSON.parse(event.data);
          errorMsg = data.error || errorMsg;
        } catch (e) {
          // Ignore parse errors
        }
      }

      onError?.(new Error(errorMsg));
    }
  });

  eventSource.addEventListener('done', (event) => {
    const data = JSON.parse(event.data);
    console.log(`Pipeline completed in ${data.total_duration_seconds}s`);
    if (!completed) {
      eventSource.close();
    }
  });

  // Return cleanup function
  return () => {
    if (eventSource.readyState !== EventSource.CLOSED) {
      eventSource.close();
    }
  };
};

/**
 * Transform Step 7 output to React format
 * Step 7 already has delimiters in code, so minimal transformation needed
 * @param {Object} step7Data - Assessment from Step 7
 * @returns {Object} - Question in React format
 */
export const transformStep7ToReact = (step7Data) => {
  if (!step7Data || !step7Data.code || !step7Data.errors) {
    throw new Error('Invalid assessment format from pipeline');
  }

  return {
    title: step7Data.title || 'Generated Assessment',
    difficulty: step7Data.difficulty || 'Intermediate',
    code: step7Data.code, // Already has <<delimiters>>
    errors: step7Data.errors.map(err => ({
      id: err.id,
      description: err.description
      // Note: line_number not needed - React parseQuestion() finds it from delimiters
    })),
    // Optional: preserve metadata for debugging
    _metadata: step7Data.metadata || null
  };
};

/**
 * Check if the API is reachable
 * @returns {Promise<boolean>}
 */
export const checkAPIHealth = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/models`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    });
    return response.ok;
  } catch (error) {
    console.error('API health check failed:', error);
    return false;
  }
};

/**
 * Fetch all pipeline prompts from the backend
 * @returns {Promise<Object>} - Object containing all step prompts
 */
export const fetchPrompts = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/get-prompts`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch prompts: ${response.status}`);
    }

    const data = await response.json();
    return data.prompts;
  } catch (error) {
    console.error('Failed to fetch prompts:', error);
    throw error;
  }
};

export const fetchStep1Categories = async (topic) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/step1`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ topic })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to run Step 1: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch Step 1 categories:', error);
    throw error;
  }
};
