import streamlit as st
import json
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Aqumen Demo - Original vs Modular",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #3B82F6, #8B5CF6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .architecture-card {
        background: rgba(31, 41, 55, 0.8);
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3B82F6;
        margin: 1rem 0;
    }
    
    .code-block {
        background: rgba(17, 24, 39, 1);
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid rgba(75, 85, 99, 0.3);
    }
    
    .metric-card {
        text-align: center;
        padding: 1rem;
        background: rgba(31, 41, 55, 0.6);
        border-radius: 0.5rem;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🧠 Aqumen.ai Demo Architecture</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #9CA3AF;">Multi-Model Adversarial Pipeline: Original vs Modular Implementation</p>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.selectbox(
        "Select View:",
        ["🏠 Overview", "📊 Architecture Comparison", "📁 File Structure", "💻 Code Examples", "🚀 Demo Links"]
    )
    
    if page == "🏠 Overview":
        show_overview()
    elif page == "📊 Architecture Comparison":
        show_architecture_comparison()
    elif page == "📁 File Structure":
        show_file_structure()
    elif page == "💻 Code Examples":
        show_code_examples()
    elif page == "🚀 Demo Links":
        show_demo_links()

def show_overview():
    st.header("📋 Project Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="architecture-card">
            <h3>🎯 What This Demonstrates</h3>
            <ul>
                <li><strong>Code Modularization</strong>: Transform monolithic code into clean, maintainable modules</li>
                <li><strong>React Best Practices</strong>: Component composition, custom hooks, separation of concerns</li>
                <li><strong>Production Architecture</strong>: Scalable patterns for real-world applications</li>
                <li><strong>ML Pipeline Simulation</strong>: Multi-model adversarial testing workflow</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="architecture-card">
            <h3>🔧 Technologies Used</h3>
            <ul>
                <li><strong>Frontend</strong>: React 18, Modern Hooks, ES6 Modules</li>
                <li><strong>Styling</strong>: Tailwind CSS, Responsive Design</li>
                <li><strong>Architecture</strong>: Component-based, Custom Hooks</li>
                <li><strong>Deployment</strong>: Static hosting, Streamlit demo</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Metrics
    st.header("📊 Project Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h2 style="color: #EF4444;">1</h2>
            <p>Original File</p>
            <small>676 lines</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h2 style="color: #10B981;">13</h2>
            <p>Modular Files</p>
            <small>Clean separation</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h2 style="color: #3B82F6;">9</h2>
            <p>UI Components</p>
            <small>Reusable modules</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h2 style="color: #8B5CF6;">3</h2>
            <p>Custom Hooks</p>
            <small>State management</small>
        </div>
        """, unsafe_allow_html=True)

def show_architecture_comparison():
    st.header("🏗️ Architecture Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="architecture-card" style="border-left-color: #EF4444;">
            <h3 style="color: #EF4444;">📄 Original Version</h3>
            <div class="code-block">
                <strong>Structure:</strong> Monolithic component<br>
                <strong>Lines:</strong> 676 in single file<br>
                <strong>State:</strong> All useState hooks together<br>
                <strong>Logic:</strong> All functions inline<br>
                <strong>UI:</strong> Single massive return statement<br>
                <strong>Data:</strong> Hardcoded in component<br>
            </div>
            
            <h4>❌ Challenges:</h4>
            <ul>
                <li>Hard to maintain and debug</li>
                <li>Difficult to test individual pieces</li>
                <li>No code reusability</li>
                <li>Hard to collaborate on</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="architecture-card" style="border-left-color: #10B981;">
            <h3 style="color: #10B981;">📦 Modular Version</h3>
            <div class="code-block">
                <strong>Structure:</strong> Component-based architecture<br>
                <strong>Files:</strong> 13 focused modules<br>
                <strong>State:</strong> Custom hooks for state logic<br>
                <strong>Logic:</strong> Separated utility functions<br>
                <strong>UI:</strong> Individual components<br>
                <strong>Data:</strong> Separate constants file<br>
            </div>
            
            <h4>✅ Benefits:</h4>
            <ul>
                <li>Easy to maintain and extend</li>
                <li>Individual components are testable</li>
                <li>High code reusability</li>
                <li>Great for team collaboration</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def show_file_structure():
    st.header("📁 File Structure & Responsibilities")
    
    # Create tabs for different categories
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 UI Components", "🔧 Logic & State", "📊 Data & Config", "🧪 Testing & Docs"])
    
    with tab1:
        st.markdown("""
        ### UI Components (9 files)
        Each component has a single responsibility:
        """)
        
        components = [
            ("Header.jsx", "Application branding and navigation", "Presentational"),
            ("TopicInput.jsx", "User input for assessment topics", "Interactive"),
            ("DifficultySelection.jsx", "Choose difficulty and subtopics", "Interactive"),
            ("GenerationLog.jsx", "Pipeline execution logging", "Data Display"),
            ("AdversarialAttempts.jsx", "Live attempt visualization", "Data Display"),
            ("AssessmentQuestion.jsx", "Interactive error detection", "Complex Interactive"),
            ("ResultsDisplay.jsx", "Performance metrics", "Data Display"),
            ("AntiCheatAlert.jsx", "Security warnings", "Conditional"),
            ("Footer.jsx", "Application footer", "Presentational")
        ]
        
        for name, description, type_info in components:
            st.markdown(f"""
            <div class="code-block" style="margin: 0.5rem 0;">
                <strong>{name}</strong> <span style="color: #3B82F6;">({type_info})</span><br>
                <small style="color: #9CA3AF;">{description}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("""
        ### Logic & State Management (3 files)
        """)
        
        logic_files = [
            ("hooks.js", "Custom React hooks for state management", "3 hooks: usePipelineState, useAdversarialAttempts, useErrorClicks"),
            ("utils.js", "Pure utility functions", "API calls, evaluation metrics, pipeline orchestration"),
            ("demo-modular.jsx", "Main component orchestrator", "Combines all modules into working application")
        ]
        
        for name, description, details in logic_files:
            st.markdown(f"""
            <div class="code-block" style="margin: 0.5rem 0;">
                <strong>{name}</strong><br>
                <em>{description}</em><br>
                <small style="color: #9CA3AF;">{details}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("""
        ### Data & Configuration (1 file)
        """)
        
        st.markdown("""
        <div class="code-block">
            <strong>constants.js</strong><br>
            <em>Centralized configuration and sample data</em><br>
            <small style="color: #9CA3AF;">Model configurations, API settings, sample pipeline data</small>
        </div>
        """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown("""
        ### Documentation & Testing
        """)
        
        docs = [
            ("README.md", "Project overview and setup instructions"),
            ("explan.md", "Detailed architecture explanation for data scientists"),
            ("INSTRUCTIONS.md", "How to run and deploy the demo"),
            ("test.js", "Basic test setup (framework for future testing)"),
            ("package.json", "Dependencies and build scripts")
        ]
        
        for name, description in docs:
            st.markdown(f"""
            <div class="code-block" style="margin: 0.5rem 0;">
                <strong>{name}</strong><br>
                <small style="color: #9CA3AF;">{description}</small>
            </div>
            """, unsafe_allow_html=True)

def show_code_examples():
    st.header("💻 Code Examples")
    
    example_type = st.selectbox(
        "Select Example:",
        ["Component Structure", "Custom Hooks", "Utility Functions", "State Management"]
    )
    
    if example_type == "Component Structure":
        st.markdown("### React Component Pattern")
        st.code("""
// components/TopicInput.jsx - Clean, focused component
import React from 'react';
import { RefreshCw } from 'lucide-react';

const TopicInput = ({ 
  userTopic,           // Props: clear interface
  setUserTopic, 
  isGenerating, 
  onGenerateDifficulties 
}) => {
  return (
    <div className="bg-gray-800/50 backdrop-blur rounded-lg shadow-xl p-8">
      <h2 className="text-3xl font-bold mb-6 text-center">Enter Assessment Topic</h2>
      <div className="max-w-2xl mx-auto">
        <input
          type="text"
          value={userTopic}
          onChange={(e) => setUserTopic(e.target.value)}
          placeholder="e.g., Machine Learning - Reinforcement Learning"
          className="w-full p-4 text-lg bg-gray-700 border border-gray-600 rounded-lg"
        />
        <button
          onClick={() => onGenerateDifficulties(userTopic)}
          disabled={!userTopic.trim() || isGenerating}
          className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg"
        >
          {isGenerating ? (
            <div className="flex items-center gap-2">
              <RefreshCw className="w-5 h-5 animate-spin" />
              Analyzing Topic...
            </div>
          ) : (
            'Start Pipeline Analysis'
          )}
        </button>
      </div>
    </div>
  );
};

export default TopicInput;
        """, language="javascript")
        
        st.markdown("""
        **Key Features:**
        - ✅ Single responsibility (handles topic input only)
        - ✅ Clear props interface (like function parameters)
        - ✅ No internal state (easier to test and debug)
        - ✅ Conditional rendering for loading states
        """)
    
    elif example_type == "Custom Hooks":
        st.markdown("### Custom Hooks for State Logic")
        st.code("""
// hooks.js - Reusable state management
import { useState } from 'react';

export const usePipelineState = () => {
  const [currentStep, setCurrentStep] = useState('input');
  const [userTopic, setUserTopic] = useState('');
  const [finalQuestion, setFinalQuestion] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  
  // Return everything the components need
  return {
    currentStep, setCurrentStep,
    userTopic, setUserTopic,
    finalQuestion, setFinalQuestion,
    isGenerating, setIsGenerating
  };
};

export const useAdversarialAttempts = () => {
  const [adversarialAttempts, setAdversarialAttempts] = useState([]);
  const [generationLog, setGenerationLog] = useState([]);
  
  const addLog = (message) => {
    setGenerationLog(prev => [...prev, { 
      timestamp: new Date().toLocaleTimeString(), 
      message 
    }]);
  };
  
  const showAttemptInProgress = (attempt) => {
    setAdversarialAttempts(prev => [...prev, {
      attempt,
      status: 'testing',
      sonnetResponse: 'Analyzing...',
      haikuResponse: 'Generating...',
      timestamp: Date.now()
    }]);
  };
  
  return {
    adversarialAttempts,
    generationLog,
    addLog,
    showAttemptInProgress
  };
};
        """, language="javascript")
        
        st.markdown("""
        **Benefits:**
        - 🔄 **Reusable**: Can be used in multiple components
        - 🧪 **Testable**: Logic is separated from UI
        - 📦 **Encapsulated**: Related state and functions grouped together
        - 🔍 **Debuggable**: Easier to track state changes
        """)
    
    elif example_type == "Utility Functions":
        st.markdown("### Pure Utility Functions")
        st.code("""
// utils.js - Pure functions (no side effects)
export const evaluateResponse = (finalQuestion, clicks) => {
  if (!finalQuestion) return null;

  const correctErrors = new Set(
    finalQuestion.errors
      .filter(e => e.severity !== 'trick')
      .map(e => e.id)
  );
  const selectedErrors = new Set(clicks);

  // Calculate familiar ML metrics
  const intersection = new Set([...selectedErrors].filter(x => correctErrors.has(x)));
  const precision = selectedErrors.size > 0 ? intersection.size / selectedErrors.size : 0;
  const recall = correctErrors.size > 0 ? intersection.size / correctErrors.size : 0;
  const f1 = precision + recall > 0 ? 2 * (precision * recall) / (precision + recall) : 0;
  
  return { precision, recall, f1 };
};

export const makeAPICall = async (model, prompt, operation, addLog) => {
  addLog(`🧠 ${operation} with ${model}...`);
  
  // Simulate API call for demo
  await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
  
  if (operation.includes("Sonnet") && Math.random() < 0.1) {
    throw new Error("Model differentiation failed - retry needed");
  }
  
  return "Sample API response for demo";
};
        """, language="javascript")
        
        st.markdown("""
        **Pure Function Benefits:**
        - ✅ **Predictable**: Same input always produces same output
        - ✅ **Testable**: Easy to unit test with different inputs
        - ✅ **Reusable**: Can be used anywhere in the application
        - ✅ **Side-effect free**: Don't modify external state
        """)

def show_demo_links():
    st.header("🚀 Live Demo Links")
    
    st.markdown("""
    ### 🌐 Local Development Server
    Your demo is currently running locally. Access it at:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="architecture-card">
            <h4>💻 Computer Access</h4>
            <code>http://localhost:8080/test.html</code>
            
            <h4>📱 Mobile Access (Same WiFi)</h4>
            <code>http://192.168.11.150:8080/test.html</code>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="architecture-card">
            <h4>✨ Features Available</h4>
            <ul>
                <li>Toggle between Original/Architecture views</li>
                <li>Interactive demo simulation</li>
                <li>No API keys required</li>
                <li>Mobile-responsive design</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 🚀 Deployment Options
    
    **GitHub Pages** (Static hosting)
    - Free hosting for public repos
    - Automatic deployments from main branch
    - Perfect for frontend demos
    
    **Vercel/Netlify** (Modern hosting)
    - Instant deployments from Git
    - Custom domains available
    - Optimized for React applications
    
    **Streamlit Cloud** (This demo!)
    - Great for data science projects
    - Easy Python-based deployments
    - Perfect for showcasing architecture
    """)
    
    st.info("💡 **Tip**: For production deployment, consider using Vercel or Netlify for the React demo, and keep this Streamlit app for documentation and architecture explanation!")

if __name__ == "__main__":
    main()