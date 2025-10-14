// Model configuration
export const MODELS = {
  STRONG: "claude-opus-4-20250514",    // For error analysis, question generation, judgment
  MID: "claude-sonnet-4-20250514",    // For "sweet spot" validation 
  WEAK: "claude-3-5-haiku-20241022"   // For authentic weak model errors
};

export const API_TIMEOUT = 60000;

// Gold Standard Examples from 2024-2025 DeepLearning.AI Courses
export const samplePipelineData = {
  // GOLD STANDARD #1: LLM Post-Training Pipeline (Score: 5.36)
  'LLM Post-Training with DPO': {
    difficultyCategories: {
      "Beginner": ["Basic fine-tuning concepts", "Supervised fine-tuning (SFT)", "Dataset preparation"],
      "Intermediate": ["RLHF pipeline design", "DPO vs PPO trade-offs", "Preference data curation"],
      "Advanced": ["Multi-stage optimization", "Constitutional AI", "RLAIF and iterative refinement"]
    },
    conceptualErrors: [
      {
        id: "missing_sft",
        description: "Applying DPO directly on base model without SFT preprocessing",
        likelihood: 0.85,
        domain_specific: true
      }
    ],
    adversarialQuestion: {
      prompt: "Implement RLHF pipeline for code generation model using DPO",
      sonnet_response: "Correctly identifies missing SFT step - 'Cannot apply DPO to base model without instruction-following capability'",
      haiku_response: "Falls for the trap - 'Looks correct, implements DPO training properly with good parameters'",
      judgment_success: true
    },
    finalQuestion: {
      title: "RLHF Training Pipeline Error Detection",
      code: `from transformers import AutoModelForCausalLM
from trl import DPOTrainer

def implement_rlhf_pipeline(base_model_path, preference_dataset):
    # Load foundation model  
    model = AutoModelForCausalLM.from_pretrained(base_model_path)
    
    # Configure DPO training directly on base model
    <span class="error-span tight" data-error-id="1" data-concept="training_sequence">trainer = DPOTrainer(
        model=model,
        train_dataset=preference_dataset,
        beta=0.1,
        learning_rate=5e-7
    )</span>
    
    # Start preference training
    trainer.train()
    return model`,
      errors: [
        {
          id: "1",
          description: "Cannot apply DPO to base model - needs SFT first to learn instruction following",
          severity: "high",
          concept: "training_sequence",
          correct: true,
          span_tightness: "tight",
          inspired_by_haiku: true
        }
      ]
    }
  },

  // GOLD STANDARD #2: Knowledge Graph API Discovery (Score: 5.56)
  'Knowledge Graphs for AI Agent API Discovery': {
    difficultyCategories: {
      "Beginner": ["Basic RDF/OWL concepts", "Simple SPARQL queries", "API schema extraction"],
      "Intermediate": ["Semantic reasoning with entailment", "Graph embedding spaces", "Dynamic API capability mapping"],
      "Advanced": ["Multi-hop logical reasoning", "Compositional API orchestration", "Self-evolving ontologies"]
    },
    conceptualErrors: [
      {
        id: "similarity_vs_compatibility",
        description: "Using embedding similarity without logical constraint reasoning for API composition",
        likelihood: 0.82,
        domain_specific: true
      }
    ],
    adversarialQuestion: {
      prompt: "Build agent API composition system using semantic similarity",
      sonnet_response: "Identifies logical flaw - 'Semantic similarity ≠ logical compatibility for API composition'",
      haiku_response: "Misses the issue - 'Good use of semantic similarity for intelligent API matching'",
      judgment_success: true
    },
    finalQuestion: {
      title: "Agent API Composition Reasoning Engine",
      code: `class APICompositionEngine:
    def find_workflow(self, user_query, available_apis):
        query_embedding = self.embed_query(user_query)
        
        # Find best API using semantic similarity
        best_apis = []
        for api in available_apis:
            api_embedding = self.embed_api_description(api)
            <span class="error-span tight" data-error-id="1" data-concept="logical_reasoning">similarity = cosine_similarity(query_embedding, api_embedding)</span>
            best_apis.append((api, similarity))
            
        # Return highest similarity APIs for composition
        return sorted(best_apis, key=lambda x: x[1], reverse=True)[:3]`,
      errors: [
        {
          id: "1",
          description: "Semantic similarity doesn't guarantee logical compatibility - need constraint reasoning",
          severity: "high",
          concept: "logical_reasoning",
          correct: true,
          span_tightness: "tight",
          inspired_by_haiku: true
        }
      ]
    }
  },

  // GOLD STANDARD #3: Multi-Agent Coordination (Score: 5.56)
  'Multi AI Agent Systems with crewAI': {
    difficultyCategories: {
      "Beginner": ["Basic agent roles", "Sequential task execution", "Simple memory sharing"],
      "Intermediate": ["Parallel agent coordination", "State synchronization", "Error propagation handling"],
      "Advanced": ["Byzantine fault tolerance", "Distributed consensus mechanisms", "Self-organizing agent hierarchies"]
    },
    conceptualErrors: [
      {
        id: "sync_blocking",
        description: "Using synchronous blocking coordination for parallel agent execution",
        likelihood: 0.85,
        domain_specific: true
      }
    ],
    adversarialQuestion: {
      prompt: "Build high-throughput multi-agent content pipeline",
      sonnet_response: "Spots scalability issue - 'Synchronous processing defeats parallelism in high-throughput scenario'",
      haiku_response: "Misses the problem - 'Good approach, ensures quality by processing crews sequentially'",
      judgment_success: true
    },
    finalQuestion: {
      title: "High-Throughput Multi-Agent Content Pipeline",
      code: `class ContentPipelineOrchestrator:
    async def process_content_requests(self, user_requests):
        results = []
        
        for request in user_requests:
            crew = Crew(agents=[researcher, writer, editor], tasks=tasks)
            
            # Process crew synchronously to ensure quality
            <span class="error-span tight" data-error-id="1" data-concept="async_coordination">result = crew.kickoff(inputs={'topic': request.topic}, wait=True)</span>
            results.append(result)
            
        return results`,
      errors: [
        {
          id: "1",
          description: "Synchronous kickoff blocks pipeline - should use async for production scale",
          severity: "high",
          concept: "async_coordination",
          correct: true,
          span_tightness: "tight", 
          inspired_by_haiku: true
        }
      ]
    }
  },

  // Legacy example for backward compatibility
  'Machine Learning - Reinforcement Learning': {
    difficultyCategories: {
      "Beginner": ["Q-learning basics", "Markov Decision Processes", "Reward function design"],
      "Intermediate": ["Policy gradient methods", "Actor-Critic architectures", "Exploration vs exploitation"],
      "Advanced": ["Multi-agent RL", "Hierarchical RL", "Meta-learning in RL"]
    },
    conceptualErrors: [
      { 
        id: "exploration_exploit", 
        description: "Confusing exploration strategies with exploitation in epsilon-greedy",
        likelihood: 0.85,
        domain_specific: true
      }
    ],
    adversarialQuestion: {
      prompt: "Implement an epsilon-greedy policy for a multi-armed bandit problem with 3 arms.",
      sonnet_response: "Correctly implements epsilon-greedy with proper exploration/exploitation balance",
      haiku_response: "Makes exploration_exploit error - uses epsilon for exploitation instead of exploration",
      judgment_success: true
    },
    finalQuestion: {
      title: "Q-Learning Implementation Error Detection",
      code: `def epsilon_greedy_policy(Q_values, epsilon=0.1):
    """Select action using epsilon-greedy strategy"""
    if np.random.random() < epsilon:
        # Exploration: choose random action
        return <span class="error-span tight" data-error-id="1" data-concept="exploration_exploit">np.argmax(Q_values)</span>
    else:
        # Exploitation: choose best action
        return <span class="error-span loose" data-error-id="2" data-concept="bellman_update">np.random.choice(len(Q_values))</span>`,
      errors: [
        {
          id: "1",
          description: "Should use np.random.choice() for exploration, not np.argmax()",
          severity: "high",
          concept: "exploration_exploit",
          correct: true,
          span_tightness: "tight",
          inspired_by_haiku: true
        },
        {
          id: "2", 
          description: "Should use np.argmax() for exploitation, not random choice",
          severity: "high",
          concept: "exploration_exploit",
          correct: true,
          span_tightness: "loose",
          inspired_by_haiku: true
        }
      ]
    }
  }
};