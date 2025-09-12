// Model configuration
export const MODELS = {
  STRONG: "claude-opus-4-20250514",
  MID: "claude-sonnet-4-20250514",
  WEAK: "claude-3-5-haiku-20241022"
};

export const API_TIMEOUT = 60000;

// Sample data that demonstrates the NEW, IMPROVED pipeline output structures
export const samplePipelineData = {
  'Machine Learning - Reinforcement Learning': {
    // STEP 1: Difficulty Categories
    difficultyCategories: {
      "Beginner": {
        "subtopics": ["Q-learning basics", "Markov Decision Processes", "Reward function design"],
        "skill_level": "Recognizes patterns, applies standard methods",
        "time_to_learn": "2-6 months"
      },
      "Intermediate": {
        "subtopics": ["Policy gradient methods", "Actor-Critic architectures", "Exploration vs exploitation"],
        "skill_level": "Integrates concepts, debugs issues, adapts methods",
        "time_to_learn": "6-18 months"
      },
      "Advanced": {
        "subtopics": ["Multi-agent RL", "Hierarchical RL", "Meta-learning in RL"],
        "skill_level": "Designs novel solutions, handles edge cases, research-level",
        "time_to_learn": "2+ years"
      }
    },
    // STEP 2: Error Catalog
    conceptualErrors: [
      {
        "mistake": "Using undiscounted returns in infinite horizon problems",
        "code_pattern": "sum(rewards) instead of sum(gamma**t * rewards[t])",
        "why_wrong": "In infinite horizon tasks, undiscounted returns can diverge, making value functions meaningless.",
        "likelihood": 0.8,
        "impact": "Model fails to learn a stable policy, often leading to nonsensical actions.",
        "difficulty_to_spot": "medium",
        "common_in": "intermediate"
      },
      {
        "mistake": "Applying policy gradients without variance reduction",
        "code_pattern": "Gradients calculated directly from raw episode returns.",
        "why_wrong": "High variance in gradient estimates leads to unstable and slow convergence.",
        "likelihood": 0.7,
        "impact": "Training is extremely slow or fails to converge entirely.",
        "difficulty_to_spot": "easy",
        "common_in": "beginner"
      }
    ],
    // STEP 3: Adversarial Question
    adversarialQuestion: {
      "question": "Review the following code for an infinite-horizon robotic navigation task. Is the reward calculation optimal for ensuring long-term goal achievement?"
    },
    // STEP 4/5: Model Responses (for simulation)
    sonnetResponse: {
      "correctness": "Incorrect",
      "main_issues": "The reward calculation uses undiscounted returns, which is unsuitable for an infinite horizon problem.",
      "production_impact": "The agent will likely fail to learn a stable, long-term policy.",
      "recommendations": "Implement discounted returns using a gamma factor (e.g., 0.99).",
      "expertise_level": "Beginner"
    },
    haikuResponse: {
      "correctness": "Correct",
      "main_issues": "The code seems fine, it correctly sums up the rewards.",
      "production_impact": "None apparent.",
      "recommendations": "No changes needed.",
      "expertise_level": "Beginner"
    },
    // STEP 6: Judgment
    judgment: {
      "sonnet_analysis": { "correct": true, "domain_expertise_shown": true, "confidence": 0.95, "reasoning": "Sonnet correctly identified the core flaw of using undiscounted returns." },
      "haiku_analysis": { "made_expected_error": true, "error_type": "Missed conceptual flaw", "error_severity": "critical", "generic_vs_domain": "domain-specific" },
      "differentiation_quality": "excellent",
      "assessment_effectiveness": { "tests_domain_knowledge": true, "appropriate_difficulty": true },
      "overall_success": true,
      "improvement_suggestions": "The question could be more subtle by hiding the reward calculation inside a helper function.",
      "confidence": 0.98
    },
    // STEP 7: Final Student Question
    finalQuestion: {
      "title": "Reinforcement Learning: Reward Calculation Error",
      "learning_objective": "Identify and correct the use of undiscounted returns in an infinite horizon problem.",
      "difficulty_level": "Intermediate",
      "code": "def calculate_return(rewards):\n  # Calculate the total return for an episode\n  total_return = <span class=\"error-span tight\" data-error-id=\"1\" data-concept=\"undiscounted_returns\">sum(rewards)</span>\n  return total_return",
      "errors": [
        {
          "id": "1",
          "description": "This calculates an undiscounted return. For infinite horizon problems, returns must be discounted with gamma to ensure convergence. The correct calculation is sum(gamma**t * r_t).",
          "severity": "high",
          "concept": "undiscounted_returns",
          "span_tightness": "tight",
          "inspired_by_haiku": true,
          "learning_value": "Understand why discounting is critical in RL for ensuring stable learning."
        }
      ],
      "total_errors": 1,
      "estimated_time": "5 minutes"
    }
  }
};