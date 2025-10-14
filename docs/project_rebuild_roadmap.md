# 🎯 Aqumen.ai Project Rebuild Roadmap

**Date**: 2025-09-14  
**Current State**: Core AI logic needs rebuild, demos built on broken foundation  
**Goal**: Build MVP with 5 core components as separate repos

---

## 🔍 **Token Optimization & CLAUDE.md Insights**

### **Tool Use vs Content Copying (2024)**
- **Tool use tokens**: 14-70% reduction with Claude's token-efficient feature
- **File copying**: Wastes tokens, should use Read/Edit tools instead of LLM copying
- **CLAUDE.md effectiveness**: Should include "use code snippets when possible" directive
- **Context management**: Keep CLAUDE.md lean, focus on task patterns not detailed instructions

### **Recommended CLAUDE.md Addition**
```markdown
# Code Efficiency Guidelines
- Use Read/Edit tools instead of copying file contents in conversation
- Generate code snippets for file operations when possible
- Leverage tool schemas for structured outputs to reduce parsing tokens
- Use batch tool calls for multiple file operations
```

---

## 🏗️ **5-Repo Architecture Based on Big Vision**

### **Repo 1: 🧠 Adversarial Pipeline Engine**
```
aqumen-adversarial-pipeline/
├── domain_classification/
├── prompt_templates/
├── model_orchestration/
└── differentiation_logic/
```
**Purpose**: Core AI that generates questions to stump weak models  
**Hard Problem**: Making questions that reliably differentiate model capabilities across domains

### **Repo 2: 🎯 Assessment Generation Engine** 
```
aqumen-assessment-generator/
├── error_span_detection/
├── pedagogical_optimization/
├── quality_validation/
└── multi_error_integration/
```
**Purpose**: Convert differentiated responses into tight, unambiguous educational assessments  
**Hard Problem**: Generating pedagogically valuable error spans with clear learning objectives

### **Repo 3: 🖥️ Frontend Presentation Layer**
```
aqumen-frontend-presentation/
├── flow_visualization/
├── demo_interface/
├── stakeholder_views/
└── progress_tracking/
```
**Purpose**: Overall presentation of the 7-step flow and system capabilities  
**Challenge**: Explaining complex AI system to non-technical stakeholders

### **Repo 4: 🎮 Interactive Assessment UI**
```
aqumen-interactive-assessment/
├── clickable_spans/
├── error_feedback/
├── learning_progress/
└── assessment_player/
```
**Purpose**: The actual student-facing assessment experience with clickable functionality  
**Challenge**: Making error detection engaging and educational

### **Repo 5: 🛡️ Anti-Cheat Infrastructure**
```
aqumen-anti-cheat/
├── hidden_signals/
├── multimodal_detection/
├── behavioral_monitoring/
└── refusal_triggers/
```
**Purpose**: Hidden masks to stump AI multimodal models and trigger refusal behavior  
**Hard Problem**: Embedding undetectable signals that fool AI assistance while remaining invisible to humans

---

## 📅 **High-Level Roadmap**

### **Phase 1: Foundation (Month 1)**
**Priority**: Fix Repo 1 (Adversarial Pipeline) - everything else depends on this

**Week 1-2: Core Logic Rebuild**
- [ ] Domain classification system (math vs business vs technical)
- [ ] Domain-aware prompt templates 
- [ ] Reliable differentiation across topic types

**Week 3-4: Quality Control**
- [ ] Output validation per domain
- [ ] Success rate >70% across diverse topics
- [ ] Mathematical correctness validation

### **Phase 2: Assessment Quality (Month 2)**
**Priority**: Build Repo 2 (Assessment Generator) 

**Week 1-2: Error Span System**
- [ ] Consistent error marker generation (comment-based: `# [E1]`)
- [ ] 1:1 mapping between spans and explanations
- [ ] Syntax-safe error marking across all domains

**Week 3-4: Pedagogical Optimization**
- [ ] Multi-error assessments (3-5 errors per assessment)
- [ ] Learning objective alignment
- [ ] Domain expert validation (math PhD, business expert)

### **Phase 3: Frontend MVP (Month 3)**
**Priority**: Build Repos 3 & 4 (Frontend + Interactive Assessment)

**Week 1-2: Presentation Layer**
- [ ] Clean 7-step flow visualization
- [ ] Real-time progress tracking
- [ ] Stakeholder-friendly explanations

**Week 3-4: Interactive Assessment**
- [ ] Clickable error spans
- [ ] Progressive hint system
- [ ] Assessment completion tracking

### **Phase 4: Anti-Cheat Research (Month 4)**
**Priority**: Research & prototype Repo 5 (Anti-Cheat)

**Week 1-2: Hidden Signal Research**
- [ ] Literature review on AI detection methods
- [ ] Prototype embedding techniques
- [ ] Test against multimodal models

**Week 3-4: Behavioral Detection**
- [ ] Timing pattern analysis
- [ ] Response pattern detection
- [ ] Integration with assessment flow

---

## 🎯 **MVP Success Criteria**

### **Technical Metrics**
- [ ] **Pipeline Success Rate**: >70% across 50+ diverse topics
- [ ] **Assessment Quality**: >4.0/5.0 average rating from domain experts  
- [ ] **Error Span Reliability**: 100% parseable, 1:1 explanation mapping
- [ ] **Response Time**: <60 seconds end-to-end assessment generation
- [ ] **Cost Efficiency**: <$0.50 per assessment including all API calls

### **Business Metrics** 
- [ ] **Stakeholder Buy-in**: "This actually works!" feedback from 3+ VCs/hiring managers
- [ ] **Domain Coverage**: Proven effectiveness in technical, business, and mathematical domains
- [ ] **User Experience**: Students can complete assessments without confusion
- [ ] **Differentiation Proof**: Clear evidence that assessments distinguish skill levels

---

## 💡 **Repository Integration Strategy**

### **API Gateway Pattern**
```
aqumen-api-gateway/
├── repo_orchestration/
├── authentication/
├── rate_limiting/
└── result_aggregation/
```

### **Shared Dependencies**
```
aqumen-shared/
├── domain_types/
├── scoring_rubrics/
├── quality_metrics/
└── data_schemas/
```

### **Development Workflow**
1. **Independent Development**: Each repo can be worked on separately
2. **Integration Testing**: Weekly integration tests across repos
3. **Staged Deployment**: Repo 1 → Repo 2 → Repos 3&4 → Repo 5
4. **Shared Standards**: Common TypeScript/Python interfaces

---

## 🚨 **Critical Dependencies**

### **Repo 1 → Everything** 
If adversarial pipeline doesn't work, nothing else matters

### **Repo 2 → Frontend (Repos 3&4)**
Assessment generation must produce reliable spans before building UI

### **Repo 5 → Independent**
Anti-cheat can be developed in parallel, integrated later

---

## 📊 **Resource Allocation**

### **Development Time** (Full-time equivalent)
- **Repo 1**: 60% of effort (most critical, hardest problems)
- **Repo 2**: 25% of effort (dependent on Repo 1 success)  
- **Repos 3&4**: 10% of effort (standard frontend development)
- **Repo 5**: 5% of effort (research phase, limited implementation)

### **Expertise Required**
- **AI/ML Engineer**: Repos 1, 2, 5
- **Frontend Developer**: Repos 3, 4
- **Domain Experts**: Validation across all repos
- **DevOps Engineer**: Integration and deployment

---

## 🎯 **Immediate Next Steps**

### **This Week**
1. **Create Repo 1** (aqumen-adversarial-pipeline)
2. **Build domain classification** (rule-based + keyword detection)
3. **Test with 10 topics** across math/business/technical domains

### **Success Gate**
Before moving to Repo 2, must achieve:
- [ ] 80% correct domain classification on test set
- [ ] 70% differentiation success rate 
- [ ] Zero critical errors (syntax breaks, mathematical incorrectness)

**The foundation must work before building the experience layer.**