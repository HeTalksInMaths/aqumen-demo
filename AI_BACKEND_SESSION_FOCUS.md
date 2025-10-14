# 🧠 AI Backend Session Focus: Question Generation Pipeline

## 🎯 **Session Objective**
Optimize the 7-step adversarial AI pipeline for **intelligent question generation** that creates assessments where **Sonnet succeeds but Haiku fails**.

---

## 🔬 **Core AI Innovation Focus**

### **1. Primary Goal: Sonnet vs Haiku Differentiation**
- **Success Criteria**: Generate questions where Claude 3.5 Sonnet answers correctly but Claude 3 Haiku makes errors
- **Reward Signal**: Questions only pass to users when this differentiation occurs
- **Quality Gate**: No differentiation = Question rejected, pipeline retries

### **2. Multi-Model Orchestration Pipeline**
```
Claude Opus 4.1 → Question Design & Error Catalog Generation
Claude 3.5 Sonnet → Validation & "Correct" Response Generation  
Claude 3 Haiku → Error Response Generation (Target for Failure)
```

### **3. Prompt Engineering Optimization**
- Implement sophisticated prompts from `docs/prompt_improvements.md`
- Focus on domain-specific error patterns (DPO, RLHF, Constitutional AI)
- Adaptive prompt refinement based on differentiation success rates

---

## 🛠 **Technical Implementation Areas**

### **Backend Infrastructure**
- **File**: `backend/clients/bedrock.py` - Core AWS Bedrock integration
- **API Flow**: 7-step pipeline with real Claude model calls
- **Caching**: Store successful question patterns for learning
- **Database**: Track differentiation success rates and error patterns

### **Agentic Workflow**
- **Retry Logic**: Auto-retry when differentiation fails
- **Quality Scoring**: Precision/Recall metrics for question effectiveness  
- **Adaptive Learning**: Improve prompts based on success patterns

### **Testing & Validation**
- **Gold Standard**: Use hardcoded DPO examples as benchmarks
- **Automated Testing**: Validate differentiation across topic domains
- **Performance Metrics**: Track model response accuracy and error rates

---

## 📊 **Key Performance Indicators**

### **Differentiation Success Rate**
- **Target**: >80% of generated questions show clear Sonnet success / Haiku failure
- **Measure**: `correct_sonnet_responses / total_questions`
- **Quality Gate**: Questions with <80% differentiation get discarded

### **Domain Coverage**
- **ML/AI Topics**: DPO, RLHF, Constitutional AI, Multi-agent systems
- **Error Categories**: Conceptual, procedural, semantic, implementation
- **Difficulty Scaling**: Beginner → Advanced progression

### **Model Performance Tracking**
```
Opus: Question Generation Quality Score
Sonnet: Validation Accuracy Rate  
Haiku: Expected Error Rate & Pattern Analysis
```

---

## 🚀 **Immediate Next Steps**

### **Phase 1: Core Pipeline Testing**
1. **Test Current Differentiation**: Run existing DPO examples through Sonnet/Haiku
2. **Measure Baseline**: Document current success/failure patterns
3. **Identify Gaps**: Where is differentiation failing?

### **Phase 2: Prompt Optimization** 
1. **Implement Advanced Prompts**: From prompt_improvements.md
2. **A/B Test Variations**: Compare prompt effectiveness
3. **Refine Based on Results**: Optimize for maximum differentiation

### **Phase 3: Agentic Enhancements**
1. **Automated Retry Logic**: When differentiation fails
2. **Learning System**: Improve prompts from successful patterns
3. **Quality Scoring**: Real-time assessment of question effectiveness

---

## 📁 **Key Files for This Session**

### **Core Backend**
- `backend/clients/bedrock.py` - Main AWS integration & pipeline logic
- `backend/requirements.txt` - Dependencies (boto3, etc.)

### **Reference Materials**
- `docs/prompt_improvements.md` - Advanced prompt strategies
- `frontend/constants.js` - Gold standard DPO examples for testing
- `examples/gold_standard_examples.md` - Complete pipeline examples

### **Configuration**
- `.streamlit/secrets.toml` - AWS credentials (secure, local only)
- `.gitignore` - Ensures no secrets pushed to GitHub

---

## 🎪 **Success Definition**

**Session Complete When:**
- ✅ Consistent 80%+ Sonnet/Haiku differentiation rate
- ✅ Automated pipeline with retry logic working
- ✅ Advanced prompts implemented and tested
- ✅ Database integration for caching and learning
- ✅ Automated testing suite for quality validation

**Ready for Production When:**
- Questions reliably challenge humans while differentiating AI models
- System learns and improves from successful patterns
- Full backend API ready for React frontend integration
