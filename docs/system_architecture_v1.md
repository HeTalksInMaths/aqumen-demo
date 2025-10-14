# 🏗️ System Architecture & Data Flow Diagrams v1.0

## 1. 🎯 **High-Level System Architecture**

```mermaid
graph TB
    User[👤 User Input<br/>Topic Selection] --> Router{🔀 Topic Router}
    
    Router --> Demo[📱 Demo Mode<br/>Hardcoded Examples]
    Router --> Live[🚀 Live Generation<br/>7-Step Pipeline]
    
    Demo --> Frontend[🖥️ Frontend Display]
    Live --> Pipeline[⚙️ 7-Step Pipeline Engine]
    
    Pipeline --> DB[(🗄️ Results Database)]
    Pipeline --> Frontend
    
    DB --> Analytics[📊 Analytics Dashboard]
    Frontend --> Student[👨‍🎓 Student Assessment Interface]
```

## 2. 🔄 **7-Step Pipeline Data Flow**

```mermaid
graph TD
    A[📝 Topic Input] --> B[🏷️ Step 1: Difficulty Categories]
    B --> C[⚠️ Step 2: Error Catalog]
    C --> D[🎯 Step 3: Strategic Question]
    D --> E[💪 Step 4: Strong Model Implementation]
    D --> F[😔 Step 5: Weak Model Implementation]
    E --> G[⚖️ Step 6: Judge Differentiation]
    F --> G
    G --> H{✅ Differentiation?}
    H -->|YES| I[🎓 Step 7: Student Assessment]
    H -->|NO| J[🔄 Retry with Feedback]
    J --> D
    I --> K[💾 Save to Database]
    K --> L[📊 Rubric Scoring]
    L --> M[🎯 Final Output]

    subgraph "🤖 Model Assignments"
        N[Sonnet 3.5 v2<br/>Steps 1,2,3,6,7]
        O[Haiku 3.5<br/>Step 4 - Mid-tier]
        P[Haiku 3<br/>Step 5 - Weak-tier]
    end
```

## 3. 🧠 **Agent Architecture Pattern**

```mermaid
graph LR
    subgraph "🎯 Strategic Agent (Sonnet 3.5 v2)"
        A1[Question Designer]
        A2[Error Cataloger]
        A3[Judge Evaluator]
        A4[Assessment Creator]
    end
    
    subgraph "🛠️ Implementation Agents"
        B1[Strong Implementer<br/>Haiku 3.5]
        B2[Weak Implementer<br/>Haiku 3]
    end
    
    subgraph "📊 System Agents"
        C1[Rubric Scorer]
        C2[Database Manager]
        C3[Analytics Engine]
    end
    
    A1 --> B1
    A1 --> B2
    B1 --> A3
    B2 --> A3
    A3 --> A4
    A4 --> C1
    C1 --> C2
    C2 --> C3
```

## 4. 🗃️ **Data Storage Architecture**

```mermaid
erDiagram
    PIPELINE_RESULTS {
        int id PK
        string timestamp
        string topic
        string subtopic
        string difficulty
        boolean differentiation_achieved
        int stopped_at_step
        int total_attempts
        json weak_model_failures
        boolean step_6_success
        string pipeline_version
    }
    
    RUBRIC_SCORES {
        int id PK
        int pipeline_result_id FK
        string timestamp
        string topic
        float output_quality_total
        float pipeline_demonstration_total
        float base_final_score
        float bonus_penalty_score
        float final_score
        string score_classification
        float conceptual_depth
        float strategic_design
        float production_impact
        float expert_differentiation
        float educational_value
        float realistic_context
    }
    
    HARDCODED_EXAMPLES {
        int id PK
        string topic_category
        string audience_type
        json full_pipeline_result
        float rubric_score
        string demo_priority
        timestamp created_at
    }
    
    USER_SESSIONS {
        int id PK
        string session_id
        string user_type
        json topics_generated
        timestamp started_at
        int total_assessments
    }
    
    PIPELINE_RESULTS ||--o{ RUBRIC_SCORES : "has scores"
    PIPELINE_RESULTS ||--o{ USER_SESSIONS : "belongs to session"
```

## 5. 🌐 **System Integration Flow**

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant Frontend as 🖥️ Frontend
    participant API as 🔌 API Gateway
    participant Pipeline as ⚙️ Pipeline Engine
    participant Models as 🤖 Claude Models (AWS Bedrock)
    participant DB as 🗄️ Database
    participant Scorer as 📊 Rubric Scorer
    
    User->>Frontend: Select Topic
    Frontend->>API: POST /generate-assessment
    API->>Pipeline: Initialize 7-step process
    
    loop Steps 1-7
        Pipeline->>Models: API call with structured schema
        Models-->>Pipeline: Structured JSON response
        Pipeline->>DB: Log step result
    end
    
    Pipeline->>Scorer: Score completed pipeline
    Scorer->>DB: Save rubric scores
    Pipeline-->>API: Return final result
    API-->>Frontend: Assessment + metadata
    Frontend-->>User: Display interactive assessment
```

## 6. 🎪 **Demo Mode Architecture**

```mermaid
graph TD
    A[🎯 Topic Selection] --> B{🔍 Topic Matcher}
    B --> C[📚 Hardcoded Examples DB]
    C --> D[🏆 Gold Standard Examples]
    D --> E[📱 Instant Display]
    
    B --> F[🚀 Live Generation Fallback]
    F --> G[⚙️ 7-Step Pipeline]
    G --> H[⏱️ 5-min timeout]
    H --> I[💾 Cache Result]
    
    subgraph "🎭 Demo Categories"
        J[🔧 Technical<br/>DPO, Multi-Agent, etc.]
        K[💼 Business<br/>Executive Assistant, etc.]
        L[📊 Data Science<br/>Analytics, ML, etc.]
    end
```

## 7. 🎨 **Frontend Component Architecture**

```mermaid
graph TB
    subgraph "📱 Main App"
        A[🏠 Home/Topic Selection]
        B[⚙️ Generation Progress]
        C[🎯 Assessment Display]
        D[📊 Results Dashboard]
    end
    
    subgraph "🧩 Reusable Components"
        E[🎪 Demo Mode Toggle]
        F[📋 Topic Categories]
        G[🔄 Progress Indicator]
        H[💬 Error Span Highlighter]
        I[📈 Score Visualizer]
    end
    
    subgraph "🎓 Student Interface"
        J[📝 Interactive Code View]
        K[🖱️ Clickable Error Spans]
        L[💡 Learning Objectives]
        M[📚 Concept Explanations]
    end
    
    A --> E
    A --> F
    B --> G
    C --> H
    C --> J
    D --> I
    J --> K
    K --> L
    L --> M
```

## 8. 🚀 **Deployment Architecture**

```mermaid
graph TB
    subgraph "☁️ Cloud Infrastructure"
        A[🌐 Load Balancer]
        B[🖥️ Frontend Servers<br/>React/Next.js]
        C[⚙️ API Servers<br/>Python/FastAPI]
        D[🗄️ Database<br/>PostgreSQL/SQLite]
    end
    
    subgraph "🤖 External Services"
        E[🔗 AWS Bedrock<br/>Claude Models]
        F[📊 Analytics Service]
        G[🔐 Auth Provider]
    end
    
    A --> B
    A --> C
    C --> D
    C --> E
    B --> F
    B --> G
    
    subgraph "🔧 Development"
        H[🐳 Docker Containers]
        I[🚀 CI/CD Pipeline]
        J[📋 Environment Configs]
    end
```

## 9. 📊 **Analytics & Monitoring Flow**

```mermaid
graph LR
    A[📈 Pipeline Metrics] --> B[📊 Analytics Engine]
    C[👤 User Interactions] --> B
    D[🤖 Model Performance] --> B
    
    B --> E[📋 Success Rate Dashboard]
    B --> F[🎯 Topic Performance Analysis]
    B --> G[⚠️ Failure Pattern Detection]
    B --> H[🔔 Alert System]
    
    E --> I[💼 Business Intelligence]
    F --> I
    G --> J[🛠️ System Optimization]
    H --> K[📞 Support Notifications]
```

## 10. 🔄 **Feedback & Improvement Loop**

```mermaid
graph TD
    A[📊 System Metrics] --> B[🧠 Analysis Engine]
    C[👤 User Feedback] --> B
    D[📈 Success Rates] --> B
    
    B --> E{📉 Performance Issues?}
    E -->|YES| F[🛠️ Prompt Engineering]
    E -->|YES| G[🔧 Model Retraining]
    E -->|NO| H[✅ System Healthy]
    
    F --> I[🧪 A/B Testing]
    G --> I
    I --> J[📊 Validation]
    J --> K[🚀 Deployment]
    K --> A
```

## 11. 🔧 **Structured Output Flow**

```mermaid
graph TD
    A[📝 Model Prompt] --> B[🛠️ Tool Schema Definition]
    B --> C[🤖 Claude API Call]
    C --> D[📊 Structured JSON Response]
    D --> E{✅ Valid Structure?}
    E -->|YES| F[✅ Process Data]
    E -->|NO| G[🔄 Retry with Fallback]
    G --> C
    F --> H[💾 Store in Database]
    
    subgraph "🎯 Tool Schema Types"
        I[📋 Difficulty Categories]
        J[⚠️ Error Catalog]
        K[🎯 Strategic Question]
        L[🎓 Student Assessment]
    end
    
    B --> I
    B --> J
    B --> K
    B --> L
```

## 12. 🎯 **Topic Routing Logic**

```mermaid
graph TD
    A[👤 User Topic Input] --> B[🔍 Topic Analyzer]
    B --> C{📚 Existing Example?}
    C -->|YES| D[🏆 Gold Standard Match]
    C -->|NO| E[🎯 Domain Classifier]
    
    D --> F[📱 Instant Demo Display]
    
    E --> G{🔧 Technical Domain?}
    E --> H{💼 Business Domain?}
    E --> I{📊 Data Science Domain?}
    
    G -->|YES| J[⚙️ Technical Pipeline Config]
    H -->|YES| K[💼 Business Pipeline Config]
    I -->|YES| L[📊 Analytics Pipeline Config]
    
    G -->|NO| M[🌐 General Pipeline Config]
    H -->|NO| M
    I -->|NO| M
    
    J --> N[🚀 Live Generation]
    K --> N
    L --> N
    M --> N
    
    N --> O[📊 Results + Caching]
```

## 13. 🎪 **Demo vs Live Generation**

```mermaid
graph LR
    subgraph "🎪 Demo Mode (Fast)"
        A[⚡ Instant Response]
        B[🏆 Pre-validated Quality]
        C[📚 Curated Examples]
    end
    
    subgraph "🚀 Live Generation (Thorough)"
        D[⏱️ 3-5 Minutes]
        E[🎯 Custom Topic]
        F[🔄 Real-time Pipeline]
    end
    
    subgraph "🔀 Hybrid Strategy"
        G[🎯 Topic Match Algorithm]
        H[⚡ Progressive Enhancement]
        I[💾 Smart Caching]
    end
    
    A --> G
    D --> G
    B --> H
    E --> H
    C --> I
    F --> I
```

## 14. 📱 **Mobile-First Architecture**

```mermaid
graph TB
    subgraph "📱 Mobile Interface"
        A[📋 Simplified Topic Selection]
        B[👆 Touch-Optimized Error Spans]
        C[📊 Condensed Progress View]
    end
    
    subgraph "💻 Desktop Interface"
        D[🖱️ Advanced Topic Filtering]
        E[⌨️ Keyboard Shortcuts]
        F[📈 Detailed Analytics]
    end
    
    subgraph "🔄 Responsive Core"
        G[📐 Adaptive Layouts]
        H[🎯 Progressive Disclosure]
        I[⚡ Performance Optimization]
    end
    
    A --> G
    B --> H
    C --> I
    D --> G
    E --> H
    F --> I
```

## 15. 🛡️ **Error Handling & Resilience**

```mermaid
graph TD
    A[🎯 Pipeline Step] --> B{⚠️ Error Occurred?}
    B -->|NO| C[✅ Continue Pipeline]
    B -->|YES| D[🔍 Error Classification]
    
    D --> E{🤖 API Error?}
    D --> F{📊 Parsing Error?}
    D --> G{⏱️ Timeout?}
    
    E -->|YES| H[🔄 Exponential Backoff]
    F -->|YES| I[🛠️ Structured Output Retry]
    G -->|YES| J[⏭️ Skip to Demo Mode]
    
    H --> K[🔢 Max Retries?]
    I --> K
    K -->|NO| A
    K -->|YES| L[🎪 Fallback to Demo]
    
    J --> L
    L --> M[📝 Log Failure]
    M --> N[🔔 Alert System]
```

---

## 🎯 **Key Architectural Decisions**

### **1. Multi-Agent Orchestration**
- **Strategic Agent** (Sonnet 3.5 v2) handles complex reasoning tasks (Steps 1,2,3,6,7)
- **Implementation Agents** (Haiku 3.5, Haiku 3) provide differentiated responses (Steps 4,5)
- **System Agents** handle scoring, storage, and analytics

### **2. Structured Data Flow**
- Tool schemas enforce consistent JSON structure across all pipeline steps
- Pipeline results stored with full audit trail for analysis
- Automated rubric scoring with detailed breakdowns

### **3. Hybrid Demo Architecture**
- Hardcoded gold standard examples for reliable, fast demos
- Live generation with comprehensive fallback mechanisms
- Topic-specific caching for performance optimization

### **4. Scalable Storage Design**
- Relational database for structured queries and analytics
- JSON storage for flexible pipeline data and configurations
- Analytics-optimized data models for performance insights

### **5. Fail-Safe Mechanisms**
- Multiple retry attempts with intelligent backoff strategies
- Timeout handling with graceful degradation to cached examples
- Comprehensive error logging and alerting systems

### **6. Performance Optimization**
- Structured outputs reduce parsing failures
- Caching strategy balances freshness with speed
- Progressive enhancement for different user contexts

### **7. Domain Flexibility**
- Pipeline configuration adapts to technical, business, or general domains
- Rubric system works across different knowledge areas
- Topic routing optimizes experience based on content type

---

## 🚀 **Implementation Priorities**

### **Phase 1: Core Stability**
1. ✅ Structured outputs for all JSON parsing steps
2. ✅ Database integration with comprehensive logging
3. ✅ Gold standard examples for demo mode
4. 🔄 Error handling and retry mechanisms

### **Phase 2: User Experience**
1. 🎯 Frontend interface with interactive error spans
2. 📊 Real-time progress indicators
3. 🎪 Demo vs live mode switching
4. 📱 Mobile-responsive design

### **Phase 3: Intelligence & Analytics**
1. 📈 Analytics dashboard for success metrics
2. 🧠 Topic performance analysis
3. 🔄 Automated prompt optimization
4. 💡 Intelligent topic suggestions

### **Phase 4: Advanced Features**
1. 🎓 Multi-user session management
2. 🛡️ Anti-cheating integration
3. 🌐 API for third-party integrations
4. 🤖 Advanced AI orchestration

This architecture provides a solid foundation for both the current system and future enhancements aligned with the big vision.