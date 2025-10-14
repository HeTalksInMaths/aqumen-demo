# Gold Standard Adversarial Pipeline Examples
**Based on DeepLearning.AI 2024-2025 Course Materials**

## Example 1: LLM Post-Training Pipeline Sequencing

### Complete 7-Step Simulated Run

**Topic:** "LLM Post-Training with DPO" | **Difficulty:** Advanced

#### Step 1: Generate Difficulty Categories (Sonnet)
**API Call:** `generate_difficulty_categories("LLM Post-Training with DPO")`

**Response:**
```json
{
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
}
```

#### Step 2: Generate Error Catalog (Opus)
**API Call:** `generate_error_catalog("RLHF pipeline design", "Advanced")`

**Response:**
```json
{
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
}
```

#### Step 3: Generate Adversarial Question - Attempt 1 (Opus)
**Response:**
```json
{
  "title": "RLHF Pipeline Implementation Review",
  "code": `def implement_rlhf_pipeline(base_model_path, preference_dataset):
    model = AutoModelForCausalLM.from_pretrained(base_model_path)
    trainer = DPOTrainer(model=model, train_dataset=preference_dataset, beta=0.1)
    trainer.train()
    return model`,
  "target_error": "Applying DPO directly on base model without SFT preprocessing"
}
```

#### Step 4: Test Model - Sonnet (Strong)
**Response:**
```json
{
  "correctness": "Incorrect - Missing critical SFT preprocessing stage",
  "main_issues": ["Base model lacks instruction-following capabilities required for DPO"],
  "expertise_level": "Beginner - missed fundamental RLHF pipeline sequence"
}
```

#### Step 5: Test Model - Haiku (Weak)
**Response:**
```json
{
  "correctness": "Looks correct - implements DPO training properly",
  "main_issues": ["Beta parameter could be tuned higher"],
  "expertise_level": "Intermediate - solid understanding of DPO mechanics"
}
```

#### Step 6: Judge Responses (Opus)
**Response:**
```json
{
  "overall_success": true,
  "differentiation_quality": "excellent",
  "confidence": 0.92
}
```

#### Step 7: Student Assessment
**Response:**
```json
{
  "title": "RLHF Training Pipeline Error Detection",
  "code": `<span class="error-span tight" data-error-id="1">dpo_trainer = DPOTrainer(model=base_model)</span>`,
  "errors": [{"id": "1", "description": "Cannot apply DPO to base model - needs SFT first"}]
}
```

---

## Example 2: Knowledge Graph Agent API Discovery (IMPROVED)

### Complete 7-Step Simulated Run

**Topic:** "Knowledge Graphs for AI Agent API Discovery" | **Difficulty:** Advanced

#### Step 1: Generate Difficulty Categories (Sonnet)
**Response:**
```json
{
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
}
```

#### Step 2: Generate Error Catalog (Opus)
**Response:**
```json
{
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
    },
    {
      "mistake": "Treating API capabilities as atomic units instead of composable predicates",
      "code_pattern": "graph.add_node('weather_api', capability='get_weather')",
      "why_wrong": "Prevents agents from reasoning about parameter compatibility and data flow between APIs",
      "likelihood": 0.78,
      "impact": "Cannot discover complex multi-step workflows, limited to single-API solutions",
      "difficulty_to_spot": "hard",
      "common_in": "intermediate practitioners"
    },
    {
      "mistake": "Using bidirectional edges for API dependency relationships",
      "code_pattern": "graph.add_edge(api1, api2, weight=compatibility_score)",
      "why_wrong": "API dependencies are directional - output of A feeds input of B, not vice versa",
      "likelihood": 0.73,
      "impact": "Reasoning engine creates impossible execution orders, circular dependencies",
      "difficulty_to_spot": "medium",
      "common_in": "intermediate practitioners"
    }
  ]
}
```

#### Step 3: Generate Adversarial Question (Opus)
**Response:**
```json
{
  "title": "Agent API Composition Reasoning Engine",
  "context": "Building an agent that discovers multi-step workflows by composing financial APIs",
  "code": `class APICompositionEngine:
    def __init__(self):
        self.capability_graph = nx.DiGraph()
        
    def add_financial_api(self, api_name, input_schema, output_schema):
        # Add API with its data transformation capability
        self.capability_graph.add_node(api_name, 
                                     inputs=input_schema,
                                     outputs=output_schema)
        
    def find_workflow(self, user_query, available_apis):
        query_embedding = self.embed_query(user_query)
        
        # Find best API using semantic similarity
        best_apis = []
        for api in available_apis:
            api_embedding = self.embed_api_description(api)
            similarity = cosine_similarity(query_embedding, api_embedding)
            best_apis.append((api, similarity))
            
        # Return highest similarity APIs for composition
        return sorted(best_apis, key=lambda x: x[1], reverse=True)[:3]`,
  "target_error": "Using embedding similarity without logical constraint reasoning for API composition"
}
```

#### Step 4: Test Model - Sonnet (Strong)
**Response:**
```json
{
  "correctness": "Incorrect - Missing logical constraint reasoning for API composition",
  "main_issues": [
    "Semantic similarity alone doesn't guarantee API compatibility",
    "No validation of input/output schema alignment between APIs",
    "Cannot detect logical contradictions or impossible data flows"
  ],
  "production_impact": "Agent composes incompatible APIs, runtime failures, poor user experience",
  "recommendations": [
    "Add constraint satisfaction solver for API parameter compatibility",
    "Implement logical reasoning over input/output schemas",
    "Validate data flow consistency in proposed compositions"
  ],
  "expertise_level": "Beginner - confused semantic similarity with logical compatibility"
}
```

#### Step 5: Test Model - Haiku (Weak)
**Response:**
```json
{
  "correctness": "Looks good - uses semantic similarity for intelligent API matching",
  "main_issues": [
    "Could add more sophisticated ranking beyond cosine similarity",
    "Might want to consider API performance metrics in selection"
  ],
  "production_impact": "Should work well for finding relevant APIs",
  "recommendations": [
    "Consider adding API reliability scores to selection criteria",
    "Maybe use transformer-based embeddings instead of basic cosine"
  ],
  "expertise_level": "Intermediate - good understanding of semantic matching approaches"
}
```

#### Step 6: Judge Responses (Opus)
**Response:**
```json
{
  "sonnet_analysis": {
    "correct": true,
    "domain_expertise_shown": true,
    "confidence": 0.93,
    "reasoning": "Correctly identified that semantic similarity ≠ logical compatibility in API composition"
  },
  "haiku_analysis": {
    "made_expected_error": true,
    "error_type": "conflated_similarity_with_compatibility",
    "error_severity": "critical",
    "generic_vs_domain": "domain-specific"
  },
  "differentiation_quality": "excellent",
  "assessment_effectiveness": {
    "tests_domain_knowledge": true,
    "appropriate_difficulty": true,
    "clear_success_criteria": true
  },
  "overall_success": true,
  "confidence": 0.91
}
```

#### Step 4-7: [Similar pattern with model testing, judgment, and student assessment]

---

## Example 3: Multi-Agent Communication Patterns (IMPROVED)

### Complete 7-Step Simulated Run

**Topic:** "Multi AI Agent Systems with crewAI" | **Difficulty:** Advanced

#### Step 1: Generate Difficulty Categories (Sonnet)
**Response:**
```json
{
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
}
```

#### Step 2: Generate Error Catalog (Opus)
**Response:**
```json
{
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
    },
    {
      "mistake": "Implementing agent communication through shared mutable state without conflict resolution",
      "code_pattern": "shared_state = {'data': {}} # All agents read/write directly",
      "why_wrong": "Race conditions cause lost updates, inconsistent reads, non-deterministic behavior",
      "likelihood": 0.78,
      "impact": "Agents make decisions on stale data, coordination failures, unpredictable outcomes",
      "difficulty_to_spot": "hard", 
      "common_in": "intermediate practitioners"
    },
    {
      "mistake": "No exponential backoff for agent retry mechanisms in distributed failures",
      "code_pattern": "while not success: retry_immediately()",
      "why_wrong": "Creates thundering herd problem, amplifies system load during failures",
      "likelihood": 0.71,
      "impact": "System collapse under load, cascading failures across agent network",
      "difficulty_to_spot": "medium",
      "common_in": "intermediate practitioners"
    }
  ]
}
```

#### Step 3: Generate Adversarial Question (Opus)
**Response:**
```json
{
  "title": "High-Throughput Multi-Agent Content Pipeline",
  "context": "Building a content creation system with 50+ concurrent agent crews processing user requests",
  "code": `from crewai import Crew, Agent, Task
import asyncio

class ContentPipelineOrchestrator:
    def __init__(self):
        self.active_crews = []
        
    async def process_content_requests(self, user_requests):
        results = []
        
        for request in user_requests:
            # Create crew for each request
            researcher = Agent(role='Researcher', goal='Gather information')
            writer = Agent(role='Writer', goal='Create content')
            editor = Agent(role='Editor', goal='Polish content')
            
            crew = Crew(
                agents=[researcher, writer, editor],
                tasks=[
                    Task(description=f'Research {request.topic}', agent=researcher),
                    Task(description='Write article', agent=writer),
                    Task(description='Edit final content', agent=editor)
                ]
            )
            
            # Process crew synchronously to ensure quality
            result = crew.kickoff(inputs={'topic': request.topic}, wait=True)
            results.append(result)
            
        return results`,
  "target_error": "Using synchronous blocking coordination for parallel agent execution"
}
```

#### Step 4: Test Model - Sonnet (Strong)
**Response:**
```json
{
  "correctness": "Incorrect - Synchronous processing defeats parallelism in high-throughput scenario", 
  "main_issues": [
    "Sequential crew.kickoff() processing eliminates concurrency benefits",
    "No async/await pattern for parallel crew execution",
    "Single failure can block entire pipeline processing",
    "Poor resource utilization - agents idle while others work"
  ],
  "production_impact": "Terrible scalability, high latency, resource waste, system bottlenecks",
  "recommendations": [
    "Use asyncio.gather() for concurrent crew execution",
    "Implement async crew.kickoff_async() pattern",
    "Add circuit breakers for failure isolation",
    "Monitor and limit concurrent crew count"
  ],
  "expertise_level": "Beginner - doesn't understand distributed system coordination"
}
```

#### Step 5: Test Model - Haiku (Weak)
**Response:**
```json
{
  "correctness": "Looks good - ensures quality by processing crews sequentially",
  "main_issues": [
    "Could add some error handling around crew.kickoff()",
    "Might want to add logging for monitoring crew performance"
  ],
  "production_impact": "Should work reliably by processing requests in order",
  "recommendations": [
    "Add try/catch around crew operations for robustness", 
    "Consider adding progress tracking for long-running crews",
    "Maybe add some metrics collection for performance monitoring"
  ],
  "expertise_level": "Intermediate - good focus on reliability over speed"
}
```

#### Step 6: Judge Responses (Opus)
**Response:**
```json
{
  "sonnet_analysis": {
    "correct": true,
    "domain_expertise_shown": true,
    "confidence": 0.94,
    "reasoning": "Correctly identified synchronous bottleneck in parallel processing context"
  },
  "haiku_analysis": {
    "made_expected_error": true,
    "error_type": "confused_sequential_reliability_with_parallel_performance",
    "error_severity": "critical",
    "generic_vs_domain": "domain-specific"
  },
  "differentiation_quality": "excellent",
  "assessment_effectiveness": {
    "tests_domain_knowledge": true,
    "appropriate_difficulty": true,
    "clear_success_criteria": true
  },
  "overall_success": true,
  "confidence": 0.92
}
```

---

## Example 4: Pydantic Schema Design for LLM Parsing

### Complete 7-Step Simulated Run

**Topic:** "Pydantic for LLM Workflows" | **Difficulty:** Intermediate

#### Step 2: Generate Error Catalog (Opus)
**Response:**
```json
{
  "errors": [
    {
      "mistake": "Using complex nested Union types that create parsing ambiguity for LLMs",
      "code_pattern": "field: Union[Dict[str, Union[str, int]], List[Union[str, Dict[str, Any]]]]",
      "why_wrong": "LLMs struggle with deeply nested type ambiguity, causing high validation failure rates",
      "likelihood": 0.77,
      "impact": "40-60% of structured outputs fail validation in production",
      "difficulty_to_spot": "medium",
      "common_in": "intermediate practitioners"
    }
  ]
}
```

#### Step 3: Generate Adversarial Question (Opus)
**Response:**
```json
{
  "title": "LLM-Optimized Pydantic Schema Design",
  "code": `from pydantic import BaseModel, Field
from typing import Union, List, Dict, Any

class DocumentEntity(BaseModel):
    # Flexible entity representation for different document types
    entity_data: Union[
        Dict[str, Union[str, int]], 
        List[Union[str, Dict[str, Any]]],
        Union[str, int, bool]
    ] = Field(description="Entity information in various formats")
    
    confidence: float = Field(ge=0.0, le=1.0)

class DocumentAnalysis(BaseModel):
    entities: List[DocumentEntity]
    
# Usage with OpenAI structured outputs
completion = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    response_format=DocumentAnalysis,
    messages=[{"role": "user", "content": document_text}]
)`,
  "target_error": "Using complex nested Union types that create parsing ambiguity for LLMs"
}
```

---

## Example 5: AI Browser Agent State Management

### Complete 7-Step Simulated Run

**Topic:** "Building AI Browser Agents" | **Difficulty:** Advanced

#### Step 2: Generate Error Catalog (Opus)
**Response:**
```json
{
  "errors": [
    {
      "mistake": "Treating browser interactions as stateless operations without preserving context",
      "code_pattern": "browser.new_page() # Fresh page for each action",
      "why_wrong": "Loses authentication state, form data, and session context needed for complex workflows",
      "likelihood": 0.73,
      "impact": "Agent cannot complete multi-step workflows, fails at login-required tasks",
      "difficulty_to_spot": "medium",
      "common_in": "intermediate practitioners"
    }
  ]
}
```

#### Step 3: Generate Adversarial Question (Opus)
**Response:**
```json
{
  "title": "Browser Agent Workflow Implementation",
  "code": `from playwright import async_api

class BrowserAgent:
    def __init__(self):
        self.browser = None
        
    async def execute_workflow(self, steps):
        self.browser = await async_api.async_playwright().start()
        
        for step in steps:
            # Create fresh page for each step to avoid conflicts
            page = await self.browser.chromium.launch().new_page()
            
            if step['action'] == 'login':
                await self.login(page, step['credentials'])
            elif step['action'] == 'navigate':
                await self.navigate(page, step['url'])
            elif step['action'] == 'extract_data':
                data = await self.extract_data(page, step['selector'])
                
            # Close page after each step
            await page.close()
            
        await self.browser.close()`,
  "target_error": "Treating browser interactions as stateless operations without preserving context"
}
```