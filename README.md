# 🧠 Aqumen.ai Adversarial Assessment System

A sophisticated multi-model adversarial pipeline for testing domain expertise in AI/ML development, featuring real-time error detection and interactive assessments.

## 🏗️ Project Structure

```
📁 adversarial demo/
├── 📁 frontend/           # React components and assets
│   ├── 📁 components/     # Modular React components  
│   ├── 📁 src/           # Main React application
│   ├── constants.js      # Sample data and configurations
│   ├── hooks.js          # Custom React hooks
│   ├── utils.js          # Utility functions
│   └── package.json      # Frontend dependencies
├── 📁 backend/           # Python backend and API
│   ├── corrected_7step_pipeline.py  # Core 7-step pipeline orchestrator
│   ├── api_server.py     # FastAPI service with streaming support
│   ├── aqumen_pipeline/  # Shared prompts, tools, validators, datatypes
│   ├── analytics/        # Reward telemetry calculations
│   ├── clients/          # Bedrock runtime wrapper
│   ├── config/           # Prompt/tool configuration loaders
│   ├── persistence/      # SQLite repository for pipeline runs
│   ├── services/         # Invocation helpers
│   ├── prompts.json      # Canonical prompt templates
│   ├── tools.json        # JSON schemas exposed to LLM tools
│   ├── streamlit_app.py  # Streamlit demo application
│   └── requirements.txt  # Python dependencies  
├── 📁 examples/          # Gold standard examples and evaluations
│   ├── gold_standard_examples.md      # Complete pipeline examples
│   ├── hardcoded_demo_data.js        # Demo data for frontend
│   ├── adversarial_example_rubric.md # Evaluation framework
│   └── improved_example_evaluations.md # Score analysis
├── 📁 docs/             # Documentation and setup guides
│   ├── AWS_BEDROCK_SETUP.md          # AWS integration guide
│   ├── prompt_improvements.md        # Prompt engineering details
│   └── *.md                          # Various documentation files
└── README.md            # This file
```

## ✨ Features

### 🎯 7-Step Adversarial Pipeline
1. **Difficulty Categories** - Generate skill-based progression with time indicators
2. **Error Catalog** - Create domain-specific conceptual error database  
3. **Adversarial Question** - Generate questions targeting specific knowledge gaps
4. **Model Testing** - Test strong vs weak models on the question
5. **Response Judgment** - Evaluate model differentiation with confidence scoring
6. **Student Assessment** - Transform into educational interactive exercises
7. **Pipeline Analytics** - Track quality metrics and success rates

### 🏆 Gold Standard Examples (Scores 5.3-5.6/5.8)
Based on **DeepLearning.AI 2024-2025 course materials**:

1. **LLM Post-Training Pipeline** (5.36) - Tests RLHF sequence understanding
2. **Knowledge Graph API Discovery** (5.56) - Tests semantic reasoning vs logical compatibility  
3. **Multi-Agent Coordination** (5.56) - Tests distributed systems expertise

### 🚀 Demo Modes
- **React Frontend** - Interactive error detection with clickable spans
- **Streamlit Backend** - Web-based pipeline demonstration
- **API Integration** - Real AWS Bedrock Claude model calls
- **Fallback Mode** - Hardcoded examples when API unavailable

## 🛠️ Setup Instructions

### Frontend (React)
```bash
cd frontend/
npm install
npm run dev
# Opens at http://localhost:3000
# Mobile access: http://[your-ip]:3000 (same WiFi)
```

### Backend (Streamlit)  
```bash
cd backend/
pip install -r requirements.txt
streamlit run streamlit_app.py
# Opens at http://localhost:8501
# Mobile access: http://[your-ip]:8501 (same WiFi)
```

### AWS Bedrock Integration (Optional)
See `docs/AWS_BEDROCK_SETUP.md` for:
- AWS credentials configuration
- Model permissions setup
- Streamlit secrets configuration

## 🚀 Deployment Options

### Local Development
- **Desktop**: `http://localhost:3000` (React) or `http://localhost:8501` (Streamlit)
- **Mobile**: `http://[your-computer-ip]:3000` or `http://[your-computer-ip]:8501`
- **Duration**: Runs until terminal closed or computer restarts
- **Setup**: Ensure both devices on same WiFi network

### Production Deployment

#### GitHub Pages (Static Hosting)
```bash
# After pushing to GitHub
# Enable GitHub Pages in repo settings  
# Demo live at: https://yourusername.github.io/repo-name/
```

#### Vercel (React-Optimized)
```bash
npm i -g vercel
cd frontend/
vercel
# Demo live at: https://your-project.vercel.app/
```

#### Streamlit Cloud (Python Apps)
```bash
# 1. Push to GitHub (public repo)
# 2. Go to share.streamlit.io
# 3. Connect GitHub repo
# 4. Deploy backend/streamlit_app.py
# 5. Live at: https://share.streamlit.io/username/repo/streamlit_app.py
```

### Platform Comparison

| Platform | Best For | Cost | Features |
|----------|----------|------|----------|
| **GitHub Pages** | Static demos | Free | Simple hosting, custom domains |
| **Vercel** | React apps | Free tier | Fast CDN, automatic deployments |
| **Netlify** | JAMstack apps | Free tier | Form handling, serverless functions |
| **Streamlit Cloud** | Python demos | Free | ML-focused, handles dependencies |

## 📊 Evaluation Framework

Examples are scored using a comprehensive rubric:

### Output Quality (60% weight)
- **Conceptual Depth** (25%) - Tests fundamental domain understanding
- **Subtlety & Adversarial Quality** (20%) - Error difficulty to spot
- **Production Impact** (20%) - Real-world consequences  
- **Expert Differentiation** (15%) - Strong vs weak model separation
- **Educational Value** (10%) - Learning benefit
- **Realistic Context** (10%) - Production relevance

### Pipeline Demonstration (40% weight)  
- **Error Catalog Quality** (20%) - Domain-specific error sophistication
- **Model Differentiation** (20%) - Clear expert knowledge gaps
- **Difficulty Categories** (15%) - Skill progression quality
- **Judgment Sophistication** (15%) - Evaluation system quality
- **Student Assessment** (15%) - Educational transformation
- **Pipeline Flow** (15%) - Coherent step-by-step narrative

**Score Ranges:**
- 🥇 **4.5-5.0+**: Gold Standard (demo-ready)
- 🥈 **4.0-4.4**: Excellent  
- 🥉 **3.5-3.9**: Good
- ⚪ **3.0-3.4**: Fair
- 🔴 **<3.0**: Poor

## 🎮 Usage Examples

### Interactive Error Detection
```javascript
// React component usage
import { samplePipelineData } from './constants.js';

const question = samplePipelineData['LLM Post-Training with DPO'].finalQuestion;
// Renders code with clickable error spans
// User clicks spans to identify conceptual errors
// System evaluates precision/recall/F1 scores
```

### Pipeline Simulation
```python
# Streamlit demo
topic = "Knowledge Graphs for AI Agent API Discovery"
result = run_adversarial_pipeline(topic)
# Executes full 7-step pipeline with progress tracking
# Shows model differentiation and quality metrics
```

### API Integration
```python
# Real Bedrock API calls
from corrected_7step_pipeline import CorrectedSevenStepPipeline

pipeline = CorrectedSevenStepPipeline()
result = pipeline.run_full_pipeline("Multi AI Agent Systems with crewAI")
# Returns SevenStepResult with rich metadata + saved telemetry
```

## 🔬 Research Applications

### Academic Use Cases
- **AI Education** - Interactive error detection exercises
- **Model Evaluation** - Systematic capability assessment
- **Curriculum Design** - Skill progression mapping
- **Assessment Creation** - Automated question generation

### Industry Applications  
- **Technical Interviews** - Domain expertise verification
- **Training Programs** - Skill gap identification
- **Model Testing** - Production readiness validation
- **Quality Assurance** - Code review automation

## 🤝 Contributing

The system is designed for extensibility:

1. **Add New Domains** - Extend `samplePipelineData` in `constants.js`
2. **Improve Prompts** - Update `backend/prompts.json` (or overrides in `prompts_changes.json`)
3. **Create Examples** - Use evaluation rubric in `examples/`
4. **Enhance UI** - Develop new React components in `frontend/components/`

## 📈 Performance Metrics

Current gold standard examples achieve:
- **Perfect Conceptual Depth** (5.0/5.0) - Tests fundamental domain theory
- **Maximum Subtlety** (5.0/5.0) - Errors look completely reasonable  
- **Critical Impact** (5.0/5.0) - Production failure consequences
- **Clear Differentiation** (5.0/5.0) - Expert vs intermediate knowledge gaps

## 🔮 Future Enhancements

- **Multi-domain Pipeline** - Cross-cutting AI expertise testing
- **Adaptive Difficulty** - Dynamic question complexity adjustment  
- **Real-time Analytics** - Live assessment performance tracking
- **Collaborative Mode** - Team-based error detection exercises
- **API Marketplace** - Third-party domain extensions

## 📄 License

[Add your license information here]

---

**Built with:** React, Streamlit, AWS Bedrock, Claude AI, Python, JavaScript

**Powered by:** DeepLearning.AI 2024-2025 course materials and cutting-edge adversarial assessment research
