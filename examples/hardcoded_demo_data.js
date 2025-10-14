/**
 * Gold Standard Hardcoded Examples for Demo
 * Based on DeepLearning.AI 2024-2025 course materials
 * Use when API is not available or for consistent demo experience
 */

export const GOLD_STANDARD_EXAMPLES = {
  
  // GOLD STANDARD #1: LLM Post-Training Pipeline (Score: 5.36)
  'LLM Post-Training with DPO': {
    difficulty_categories: {
      "Beginner": {
        "subtopics": ["Basic fine-tuning concepts", "Supervised fine-tuning (SFT)", "Dataset preparation"],
        "skill_level": "Recognizes training stages, applies standard methods",
        "time_to_learn": "3-6 months"
      },
      "Intermediate": {
        "subtopics": ["RLHF pipeline design", "DPO vs PPO trade-offs", "Preference data curation"],
        "skill_level": "Integrates training stages, debugs convergence issues",
        "time_to_learn": "8-18 months"
      },
      "Advanced": {
        "subtopics": ["Multi-stage optimization", "Constitutional AI", "RLAIF and iterative refinement"],
        "skill_level": "Designs novel training pipelines, handles edge cases",
        "time_to_learn": "2+ years"
      }
    },
    error_catalog: {
      "domain": "RLHF pipeline design",
      "difficulty": "Advanced",
      "errors": [
        {
          "mistake": "Applying DPO directly on base model without SFT preprocessing",
          "code_pattern": "trainer = DPOTrainer(model=base_model, preference_data=dataset)",
          "why_wrong": "DPO requires instruction-following capability that base models lack",
          "likelihood": 0.85,
          "impact": "Training diverges, model learns to ignore preferences",
          "difficulty_to_spot": "hard",
          "common_in": "intermediate practitioners"
        }
      ]
    },
    adversarial_attempts: [
      {
        attempt: 1,
        status: 'success',
        sonnet_response: '✅ Correctly identifies missing SFT step - "Cannot apply DPO to base model without instruction-following capability"',
        haiku_response: '❌ Falls for the trap - "Looks correct, implements DPO training properly with good parameters"',
        quality_score: 0.92
      }
    ],
    final_question: {
      title: "RLHF Training Pipeline Error Detection",
      context: "Implementing preference learning for a code generation model using DPO",
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
          inspired_by_haiku: true,
          learning_value: "Understanding RLHF pipeline requires SFT → DPO sequence"
        }
      ]
    },
    pipeline_metrics: {
      conceptual_depth: 5.0,
      subtlety_score: 5.0,
      production_impact: 5.0,
      expert_differentiation: 5.0,
      educational_value: 5.0
    }
  },

  // GOLD STANDARD #2: Knowledge Graph API Discovery (Score: 5.56)
  'Knowledge Graphs for AI Agent API Discovery': {
    difficulty_categories: {
      "Beginner": {
        "subtopics": ["Basic RDF/OWL concepts", "Simple SPARQL queries", "API schema extraction"],
        "skill_level": "Creates static knowledge graphs, understands semantic triples",
        "time_to_learn": "3-5 months"
      },
      "Intermediate": {
        "subtopics": ["Semantic reasoning with entailment", "Graph embedding spaces", "Dynamic API capability mapping"],
        "skill_level": "Implements semantic similarity and basic reasoning chains",
        "time_to_learn": "8-15 months"
      },
      "Advanced": {
        "subtopics": ["Multi-hop logical reasoning", "Compositional API orchestration", "Self-evolving ontologies"],
        "skill_level": "Designs reasoning systems that discover novel API compositions",
        "time_to_learn": "2+ years"
      }
    },
    error_catalog: {
      "domain": "Semantic reasoning with entailment",
      "difficulty": "Advanced", 
      "errors": [
        {
          "mistake": "Using embedding similarity without logical constraint reasoning for API composition",
          "code_pattern": "best_api = max(apis, key=lambda x: cosine_similarity(query_embedding, x.embedding))",
          "why_wrong": "High similarity doesn't guarantee logical compatibility or constraint satisfaction",
          "likelihood": 0.82,
          "impact": "Agents compose incompatible APIs, workflow execution fails at runtime",
          "difficulty_to_spot": "hard",
          "common_in": "intermediate practitioners"
        }
      ]
    },
    adversarial_attempts: [
      {
        attempt: 1,
        status: 'success', 
        sonnet_response: '✅ Identifies logical flaw - "Semantic similarity ≠ logical compatibility for API composition"',
        haiku_response: '❌ Misses the issue - "Good use of semantic similarity for intelligent API matching"',
        quality_score: 0.91
      }
    ],
    final_question: {
      title: "Agent API Composition Reasoning Engine",
      context: "Building an agent that discovers multi-step workflows by composing financial APIs",
      code: `class APICompositionEngine:
    def __init__(self):
        self.capability_graph = nx.DiGraph()
        
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
          inspired_by_haiku: true,
          learning_value: "API composition requires logical constraint satisfaction, not just similarity"
        }
      ]
    },
    pipeline_metrics: {
      conceptual_depth: 5.0,
      subtlety_score: 5.0,
      production_impact: 5.0,
      expert_differentiation: 5.0,
      educational_value: 5.0
    }
  },

  // GOLD STANDARD #3: Multi-Agent Coordination (Score: 5.56)
  'Multi AI Agent Systems with crewAI': {
    difficulty_categories: {
      "Beginner": {
        "subtopics": ["Basic agent roles", "Sequential task execution", "Simple memory sharing"],
        "skill_level": "Creates agents with defined roles, handles linear workflows",
        "time_to_learn": "2-4 months"
      },
      "Intermediate": {
        "subtopics": ["Parallel agent coordination", "State synchronization", "Error propagation handling"],
        "skill_level": "Manages concurrent agents, implements basic coordination patterns",
        "time_to_learn": "6-12 months"
      },
      "Advanced": {
        "subtopics": ["Byzantine fault tolerance", "Distributed consensus mechanisms", "Self-organizing agent hierarchies"],
        "skill_level": "Designs fault-tolerant multi-agent systems with dynamic reorganization",
        "time_to_learn": "18+ months"
      }
    },
    error_catalog: {
      "domain": "Parallel agent coordination",
      "difficulty": "Advanced",
      "errors": [
        {
          "mistake": "Using synchronous blocking coordination for parallel agent execution",
          "code_pattern": "result = crew.kickoff(inputs, wait=True)",
          "why_wrong": "Creates artificial bottlenecks, prevents true parallelism, causes cascading failures",
          "likelihood": 0.85,
          "impact": "System becomes sequential instead of parallel, poor scalability, single point of failure",
          "difficulty_to_spot": "hard",
          "common_in": "intermediate practitioners"
        }
      ]
    },
    adversarial_attempts: [
      {
        attempt: 1,
        status: 'success',
        sonnet_response: '✅ Spots scalability issue - "Synchronous processing defeats parallelism in high-throughput scenario"',
        haiku_response: '❌ Misses the problem - "Good approach, ensures quality by processing crews sequentially"',
        quality_score: 0.92
      }
    ],
    final_question: {
      title: "High-Throughput Multi-Agent Content Pipeline",
      context: "Building a content creation system with 50+ concurrent agent crews processing user requests",
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
          inspired_by_haiku: true,
          learning_value: "High-throughput systems require async coordination, not sequential processing"
        }
      ]
    },
    pipeline_metrics: {
      conceptual_depth: 5.0,
      subtlety_score: 5.0,
      production_impact: 5.0,
      expert_differentiation: 5.0,
      educational_value: 5.0
    }
  }
};

// Helper function to get example by topic
export function getExampleByTopic(topic) {
  return GOLD_STANDARD_EXAMPLES[topic] || null;
}

// Helper function to simulate pipeline execution with realistic delays
export function simulatePipelineExecution(topic, onProgress) {
  const example = getExampleByTopic(topic);
  if (!example) return null;

  const steps = [
    { name: "Generating difficulty categories", delay: 2000, data: example.difficulty_categories },
    { name: "Creating error catalog", delay: 1500, data: example.error_catalog },
    { name: "Generating adversarial question", delay: 2500, data: example.final_question },
    { name: "Testing model responses", delay: 3000, data: example.adversarial_attempts },
    { name: "Evaluating results", delay: 1000, data: example.pipeline_metrics }
  ];

  return new Promise((resolve) => {
    let currentStep = 0;
    
    function executeStep() {
      if (currentStep >= steps.length) {
        resolve(example);
        return;
      }
      
      const step = steps[currentStep];
      onProgress?.(step.name, currentStep, steps.length);
      
      setTimeout(() => {
        currentStep++;
        executeStep();
      }, step.delay);
    }
    
    executeStep();
  });
}

// Available topics for demo
export const AVAILABLE_TOPICS = Object.keys(GOLD_STANDARD_EXAMPLES);

// Quick access to pipeline metrics for all examples
export const PIPELINE_COMPARISON = Object.entries(GOLD_STANDARD_EXAMPLES).map(([topic, data]) => ({
  topic,
  score: Object.values(data.pipeline_metrics).reduce((a, b) => a + b, 0) / 5,
  metrics: data.pipeline_metrics
})).sort((a, b) => b.score - a.score);