import { MODELS, samplePipelineData } from './constants.js';

// API integration utility
export const makeAPICall = async (model, prompt, operation, addLog) => {
  addLog(`🧠 ${operation} with ${model}...`);
  
  // Simulate API call for demo (replace with actual fetch in production)
  await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
  
  if (operation.includes("Sonnet") && Math.random() < 0.1) {
    throw new Error("Model differentiation failed - retry needed");
  }
  
  return "Sample API response for demo";
};

// Fallback question creator
export const createFallbackQuestion = () => ({
  title: "Error Detection Exercise",
  code: "Sample code with potential errors...",
  errors: [],
  watermark: "🔒AQUMEN-DEMO-2024🔒",
  anti_cheat_elements: ["Demo version"]
});

// Anti-cheat detection
export const checkAntiCheat = (text, setAntiCheatTriggered, addLog) => {
  const watermarks = ['🔒AQUMEN', 'EVAL-2024', 'Academic integrity notice'];
  if (watermarks.some(w => text.includes(w))) {
    setAntiCheatTriggered(true);
    addLog("🚨 Anti-cheat triggered: Watermark detected");
    return true;
  }
  return false;
};

// Evaluation metrics calculations
export const calculateConceptualScore = (selected, correct) => {
  return Math.max(0, 100 - Math.abs(selected.size - correct.size) * 25);
};

export const calculateSpanTightness = (finalQuestion) => {
  if (!finalQuestion) return 0;
  const tightSpans = finalQuestion.errors.filter(e => e.span_tightness === 'tight').length;
  const totalSpans = finalQuestion.errors.length;
  return totalSpans > 0 ? (tightSpans / totalSpans) * 100 : 0;
};

// Evaluation function
export const evaluateResponse = (finalQuestion, clicks) => {
  if (!finalQuestion) return null;

  const correctErrors = new Set(
    finalQuestion.errors
      .filter(e => e.severity !== 'trick')
      .map(e => e.id)
  );
  const selectedErrors = new Set(clicks);
  const trickErrors = finalQuestion.errors.filter(e => e.severity === 'trick');

  // Advanced metrics
  const intersection = new Set([...selectedErrors].filter(x => correctErrors.has(x)));
  const precision = selectedErrors.size > 0 ? intersection.size / selectedErrors.size : 0;
  const recall = correctErrors.size > 0 ? intersection.size / correctErrors.size : 0;
  const f1 = precision + recall > 0 ? 2 * (precision * recall) / (precision + recall) : 0;
  
  // Pedagogical scoring
  const conceptualUnderstanding = calculateConceptualScore(selectedErrors, correctErrors);
  const spanTightness = calculateSpanTightness(finalQuestion);
  
  return {
    precision,
    recall,
    f1,
    conceptualUnderstanding,
    spanTightness,
    correctErrors,
    selectedErrors,
    trickErrors,
    haiku_inspired_errors: finalQuestion.errors.filter(e => e.inspired_by_haiku).length
  };
};

// Pipeline execution utilities
export const generateDifficultyCategories = async (topic, setDifficultyCategories, setCurrentStep, addLog, setIsGenerating) => {
  setIsGenerating(true);
  addLog(`📊 Starting pipeline for: ${topic}`);
  
  try {
    const prompt = `For the topic "${topic}", create exactly 3 difficulty levels with specific subtopic examples.
    
    Focus on creating a progression from basic concepts to advanced domain-specific knowledge.
    Ensure each level has concrete, assessable subtopics that can differentiate between skill levels.
    
    Return JSON format:
    {
      "Beginner": ["subtopic1", "subtopic2", "subtopic3"],
      "Intermediate": ["subtopic1", "subtopic2", "subtopic3"], 
      "Advanced": ["subtopic1", "subtopic2", "subtopic3"]
    }`;

    await makeAPICall(MODELS.MID, prompt, "Generating difficulty categories (Sonnet)", addLog);
    
    // Use sample data for demo
    const categories = samplePipelineData[topic]?.difficultyCategories || {
      "Beginner": ["Basic concepts", "Fundamentals", "Introduction"],
      "Intermediate": ["Applied knowledge", "Problem solving", "Integration"],
      "Advanced": ["Complex scenarios", "Optimization", "Research-level"]
    };
    
    setDifficultyCategories(categories);
    setCurrentStep('difficulty');
    addLog("✅ Difficulty categories generated");
    
  } catch (error) {
    addLog(`❌ Error: ${error.message}`);
  } finally {
    setIsGenerating(false);
  }
};