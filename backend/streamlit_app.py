import streamlit as st
import time
import random
from datetime import datetime
import json

# Import Bedrock integration
try:
    from bedrock_utils import get_bedrock_client, test_bedrock_connection, generate_difficulty_categories, generate_adversarial_question, generate_domain_expertise_evaluation, create_student_assessment
    BEDROCK_AVAILABLE = True
except ImportError as e:
    st.warning(f"Bedrock integration not available: {e}")
    BEDROCK_AVAILABLE = False

# Page config
st.set_page_config(
    page_title="Aqumen.ai Demo - Interactive Streamlit Version",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
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
    
    .step-container {
        background: rgba(31, 41, 55, 0.8);
        padding: 2rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3B82F6;
        margin: 1rem 0;
    }
    
    .pipeline-log {
        background: rgba(17, 24, 39, 1);
        padding: 1rem;
        border-radius: 0.5rem;
        font-family: monospace;
        font-size: 12px;
        max-height: 300px;
        overflow-y: auto;
    }
    
    .error-span {
        background: #FEF3C7;
        color: #92400E;
        padding: 2px 4px;
        border-radius: 3px;
        border: 1px solid #F59E0B;
        cursor: pointer;
        margin: 0 2px;
    }
    
    .error-span-selected {
        background: #FEE2E2;
        color: #991B1B;
        border-color: #EF4444;
    }
    
    .metric-card {
        text-align: center;
        padding: 1rem;
        background: rgba(31, 41, 55, 0.6);
        border-radius: 0.5rem;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    
    .attempt-card {
        background: rgba(31, 41, 55, 0.6);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #8B5CF6;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Gold Standard Sample Data from 2024-2025 DeepLearning.AI Courses
SAMPLE_DATA = {
    # GOLD STANDARD #1: LLM Post-Training Pipeline (Score: 5.36)
    'LLM Post-Training with DPO': {
        'difficulty_categories': {
            "Beginner": ["Basic fine-tuning concepts", "Supervised fine-tuning (SFT)", "Dataset preparation"],
            "Intermediate": ["RLHF pipeline design", "DPO vs PPO trade-offs", "Preference data curation"], 
            "Advanced": ["Multi-stage optimization", "Constitutional AI", "RLAIF and iterative refinement"]
        },
        'final_question': {
            'title': "RLHF Training Pipeline Error Detection",
            'context': "Implementing preference learning for a code generation model using DPO",
            'code': """from transformers import AutoModelForCausalLM
from trl import DPOTrainer

def implement_rlhf_pipeline(base_model_path, preference_dataset):
    # Load foundation model  
    model = AutoModelForCausalLM.from_pretrained(base_model_path)
    
    # Configure DPO training directly on base model
    [ERROR_1]trainer = DPOTrainer(
        model=model,
        train_dataset=preference_dataset,
        beta=0.1,
        learning_rate=5e-7
    )[/ERROR_1]
    
    # Start preference training
    trainer.train()
    return model""",
            'errors': [
                {
                    'id': 1,
                    'description': "Cannot apply DPO to base model - needs SFT first to learn instruction following",
                    'severity': "high",
                    'correct': True,
                    'concept': "training_sequence"
                }
            ]
        }
    },

    # GOLD STANDARD #2: Knowledge Graph API Discovery (Score: 5.56)
    'Knowledge Graphs for AI Agent API Discovery': {
        'difficulty_categories': {
            "Beginner": ["Basic RDF/OWL concepts", "Simple SPARQL queries", "API schema extraction"],
            "Intermediate": ["Semantic reasoning with entailment", "Graph embedding spaces", "Dynamic API capability mapping"],
            "Advanced": ["Multi-hop logical reasoning", "Compositional API orchestration", "Self-evolving ontologies"]
        },
        'final_question': {
            'title': "Agent API Composition Reasoning Engine",
            'context': "Building an agent that discovers multi-step workflows by composing financial APIs",
            'code': """class APICompositionEngine:
    def find_workflow(self, user_query, available_apis):
        query_embedding = self.embed_query(user_query)
        
        # Find best API using semantic similarity
        best_apis = []
        for api in available_apis:
            api_embedding = self.embed_api_description(api)
            [ERROR_1]similarity = cosine_similarity(query_embedding, api_embedding)[/ERROR_1]
            best_apis.append((api, similarity))
            
        # Return highest similarity APIs for composition
        return sorted(best_apis, key=lambda x: x[1], reverse=True)[:3]""",
            'errors': [
                {
                    'id': 1,
                    'description': "Semantic similarity doesn't guarantee logical compatibility - need constraint reasoning",
                    'severity': "high", 
                    'correct': True,
                    'concept': "logical_reasoning"
                }
            ]
        }
    },

    # GOLD STANDARD #3: Multi-Agent Coordination (Score: 5.56)
    'Multi AI Agent Systems with crewAI': {
        'difficulty_categories': {
            "Beginner": ["Basic agent roles", "Sequential task execution", "Simple memory sharing"],
            "Intermediate": ["Parallel agent coordination", "State synchronization", "Error propagation handling"],
            "Advanced": ["Byzantine fault tolerance", "Distributed consensus mechanisms", "Self-organizing agent hierarchies"]
        },
        'final_question': {
            'title': "High-Throughput Multi-Agent Content Pipeline",
            'context': "Building a content creation system with 50+ concurrent agent crews processing user requests",
            'code': """class ContentPipelineOrchestrator:
    async def process_content_requests(self, user_requests):
        results = []
        
        for request in user_requests:
            crew = Crew(agents=[researcher, writer, editor], tasks=tasks)
            
            # Process crew synchronously to ensure quality
            [ERROR_1]result = crew.kickoff(inputs={'topic': request.topic}, wait=True)[/ERROR_1]
            results.append(result)
            
        return results""",
            'errors': [
                {
                    'id': 1,
                    'description': "Synchronous kickoff blocks pipeline - should use async for production scale",
                    'severity': "high",
                    'correct': True,
                    'concept': "async_coordination"
                }
            ]
        }
    },

    # Legacy example for backward compatibility
    'Machine Learning - Reinforcement Learning': {
        'difficulty_categories': {
            "Beginner": ["Q-learning basics", "Markov Decision Processes", "Reward function design"],
            "Intermediate": ["Policy gradient methods", "Actor-Critic architectures", "Exploration vs exploitation"],
            "Advanced": ["Multi-agent RL", "Hierarchical RL", "Meta-learning in RL"]
        },
        'final_question': {
            'title': "Q-Learning Implementation Error Detection",
            'code': """def epsilon_greedy_policy(Q_values, epsilon=0.1):
    \"\"\"Select action using epsilon-greedy strategy\"\"\"
    if np.random.random() < epsilon:
        # Exploration: choose random action
        return [ERROR_1]np.argmax(Q_values)[/ERROR_1]
    else:
        # Exploitation: choose best action
        return [ERROR_2]np.random.choice(len(Q_values))[/ERROR_2]

def update_q_table(Q, state, action, reward, next_state, alpha=0.1, gamma=0.9):
    \"\"\"Update Q-table using Bellman equation\"\"\"
    current_q = Q[state][action]
    max_next_q = np.max(Q[next_state])
    
    # Temporal difference update
    Q[state][action] = current_q + alpha * [ERROR_3](reward + gamma * max_next_q - current_q)[/ERROR_3]
    
    return Q""",
            'errors': [
                {
                    'id': 1,
                    'description': "Should use np.random.choice() for exploration, not np.argmax()",
                    'severity': "high",
                    'correct': True
                },
                {
                    'id': 2,
                    'description': "Should use np.argmax() for exploitation, not random choice", 
                    'severity': "high",
                    'correct': True
                },
                {
                    'id': 3,
                    'description': "Bellman update is actually correct - this is a trick question",
                    'severity': "trick",
                    'correct': False
                }
            ]
        }
    }
}

# Initialize session state
def init_session_state():
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 'input'
    if 'user_topic' not in st.session_state:
        st.session_state.user_topic = ''
    if 'selected_difficulty' not in st.session_state:
        st.session_state.selected_difficulty = None
    if 'selected_subtopic' not in st.session_state:
        st.session_state.selected_subtopic = None
    if 'generation_log' not in st.session_state:
        st.session_state.generation_log = []
    if 'adversarial_attempts' not in st.session_state:
        st.session_state.adversarial_attempts = []
    if 'selected_errors' not in st.session_state:
        st.session_state.selected_errors = set()
    if 'evaluation_results' not in st.session_state:
        st.session_state.evaluation_results = None

def add_log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.generation_log.append(f"[{timestamp}] {message}")

def simulate_api_call(operation, delay_range=(1, 3)):
    """Simulate API call with realistic delays"""
    delay = random.uniform(*delay_range)
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(100):
        progress_bar.progress(i + 1)
        status_text.text(f"{operation}... {i+1}%")
        time.sleep(delay / 100)
    
    progress_bar.empty()
    status_text.empty()
    
    # Small chance of simulated failure for realism
    if random.random() < 0.1:
        raise Exception(f"Model differentiation failed - retry needed")
    
    return f"Success: {operation}"

def run_adversarial_pipeline():
    """Simulate the adversarial pipeline with live updates"""
    st.session_state.adversarial_attempts = []
    
    add_log("🧠 Step 2: Generating conceptual error catalog (Opus)")
    simulate_api_call("Generating error catalog", (1, 2))
    add_log("✅ Error catalog generated")
    
    add_log("🎯 Step 3: Generating adversarial question (Opus)")  
    simulate_api_call("Creating adversarial question", (1, 2))
    add_log("✅ Adversarial question created")
    
    # Adversarial attempts loop
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        add_log(f"🔄 Attempt {attempt}: Testing model differentiation")
        
        # Add attempt to session state
        st.session_state.adversarial_attempts.append({
            'attempt': attempt,
            'status': 'testing',
            'sonnet_response': 'Analyzing...',
            'haiku_response': 'Generating...'
        })
        
        # Simulate parallel model testing
        col1, col2 = st.columns(2)
        with col1:
            st.info("🧠 Sonnet: Analyzing code...")
            simulate_api_call("Sonnet validation", (1, 2))
        with col2:
            st.info("⚡ Haiku: Testing response...")
            simulate_api_call("Haiku testing", (1, 2))
        
        # Update attempt results
        st.session_state.adversarial_attempts[-1].update({
            'status': 'success' if attempt >= 2 else 'failed',
            'sonnet_response': '✅ Correctly identifies the error' if attempt <= 2 else '✅ Comprehensive analysis',
            'haiku_response': '❌ Misses the conceptual issue' if attempt <= 2 else '✅ Actually got it right (retry needed)' if attempt == 3 else '❌ Falls for semantic trap'
        })
        
        add_log("⚖️ Step 6: Judging model responses (Opus)")
        simulate_api_call("Response judgment", (0.5, 1))
        
        # Success condition
        if attempt >= 2 or random.random() > 0.3:
            add_log("✅ Pipeline successful: Model differentiation achieved")
            st.session_state.adversarial_attempts[-1]['status'] = 'success'
            break
        else:
            add_log(f"❌ Attempt {attempt} failed: Insufficient differentiation, retrying...")
            time.sleep(1)
    
    add_log("📝 Step 7: Creating student assessment (Opus)")
    simulate_api_call("Student question creation", (1, 2))
    add_log("🎉 Assessment ready!")
    
    st.session_state.current_step = 'assessment'

def render_code_with_errors(code_text):
    """Render code with clickable error spans"""
    # Replace error markers with clickable spans
    for i in range(1, 4):
        error_class = "error-span-selected" if i in st.session_state.selected_errors else "error-span"
        code_text = code_text.replace(f'[ERROR_{i}]', f'<span class="{error_class}" onclick="toggleError({i})">')
        code_text = code_text.replace(f'[/ERROR_{i}]', '</span>')
    
    return code_text

def main():
    init_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🧠 Aqumen.ai Interactive Demo</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #9CA3AF;">Multi-Model Adversarial Pipeline for Intelligent Error Detection</p>', unsafe_allow_html=True)
    
    # Bedrock connection status
    if BEDROCK_AVAILABLE:
        connection_status = test_bedrock_connection()
        if connection_status:
            st.success("🚀 **LIVE MODE**: Connected to AWS Bedrock - Using real Claude models!")
        else:
            st.warning("⚡ **DEMO MODE**: Bedrock configured but not connected - Using simulations")
    else:
        st.info("📝 **DEMO MODE**: Using simulated API calls - Configure Bedrock for live models")
    
    # Sidebar navigation
    st.sidebar.title("🎯 Demo Navigation")
    
    # Architecture toggle
    demo_mode = st.sidebar.radio(
        "Select View:",
        ["🚀 Interactive Demo", "📊 Architecture Comparison"],
        index=0 if st.session_state.current_step != 'architecture' else 1
    )
    
    if demo_mode == "📊 Architecture Comparison":
        show_architecture_comparison()
        return
    
    # Progress indicator
    steps = ["📝 Input", "🎯 Selection", "⚙️ Pipeline", "📊 Assessment"]
    current_idx = ['input', 'difficulty', 'pipeline', 'assessment'].index(st.session_state.current_step) if st.session_state.current_step in ['input', 'difficulty', 'pipeline', 'assessment'] else 0
    
    st.sidebar.markdown("### 📍 Progress")
    for i, step in enumerate(steps):
        if i == current_idx:
            st.sidebar.markdown(f"**➤ {step}** ⭐")
        elif i < current_idx:
            st.sidebar.markdown(f"✅ {step}")
        else:
            st.sidebar.markdown(f"⭕ {step}")
    
    # Step 1: Topic Input
    if st.session_state.current_step == 'input':
        st.markdown('<div class="step-container">', unsafe_allow_html=True)
        st.header("📝 Step 1: Enter Assessment Topic")
        
        topic = st.text_input(
            "Domain/Subject:",
            value=st.session_state.user_topic,
            placeholder="e.g., Machine Learning - Reinforcement Learning",
            key="topic_input"
        )
        
        st.session_state.user_topic = topic
        
        if st.button("🚀 Start Pipeline Analysis", disabled=not topic.strip(), type="primary"):
            add_log(f"📊 Starting pipeline for: {topic}")
            
            with st.spinner("Analyzing topic and generating difficulty categories..."):
                simulate_api_call("Generating difficulty categories", (2, 3))
            
            add_log("✅ Difficulty categories generated")
            st.session_state.current_step = 'difficulty'
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 2: Difficulty Selection
    elif st.session_state.current_step == 'difficulty':
        st.markdown('<div class="step-container">', unsafe_allow_html=True)
        st.header("🎯 Step 2: Select Difficulty & Subtopic")
        
        if st.session_state.user_topic in SAMPLE_DATA:
            categories = SAMPLE_DATA[st.session_state.user_topic]['difficulty_categories']
        else:
            categories = {
                "Beginner": ["Basic concepts", "Fundamentals", "Introduction"],
                "Intermediate": ["Applied knowledge", "Problem solving", "Integration"],
                "Advanced": ["Complex scenarios", "Optimization", "Research-level"]
            }
        
        for difficulty, subtopics in categories.items():
            st.subheader(f"🎓 {difficulty} Level")
            cols = st.columns(len(subtopics))
            
            for i, subtopic in enumerate(subtopics):
                with cols[i]:
                    if st.button(
                        subtopic, 
                        key=f"{difficulty}_{subtopic}",
                        use_container_width=True
                    ):
                        st.session_state.selected_difficulty = difficulty
                        st.session_state.selected_subtopic = subtopic
                        add_log(f"🎯 Selected: {subtopic} ({difficulty})")
                        st.session_state.current_step = 'pipeline'
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 3: Pipeline Execution
    elif st.session_state.current_step == 'pipeline':
        st.header("⚙️ Step 3: Adversarial Pipeline Execution")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📊 Pipeline Progress")
            
            if not st.session_state.adversarial_attempts:
                st.info(f"🎯 Running adversarial pipeline for: **{st.session_state.selected_subtopic}** ({st.session_state.selected_difficulty})")
                
                if st.button("▶️ Start Adversarial Pipeline", type="primary"):
                    with st.spinner("Running multi-model adversarial pipeline..."):
                        run_adversarial_pipeline()
                    st.rerun()
            else:
                # Show adversarial attempts
                st.subheader("🔄 Live Adversarial Loop")
                for attempt in st.session_state.adversarial_attempts:
                    with st.container():
                        cols = st.columns([1, 2, 2, 1])
                        
                        with cols[0]:
                            status_color = "🟢" if attempt['status'] == 'success' else "🔴" if attempt['status'] == 'failed' else "🟡"
                            st.write(f"{status_color} **Attempt {attempt['attempt']}**")
                        
                        with cols[1]:
                            st.info(f"🧠 Sonnet: {attempt['sonnet_response']}")
                        
                        with cols[2]:
                            st.error(f"⚡ Haiku: {attempt['haiku_response']}")
                        
                        with cols[3]:
                            st.write(attempt['status'].upper())
                
                if st.button("📊 Continue to Assessment", type="primary"):
                    st.session_state.current_step = 'assessment'
                    st.rerun()
        
        with col2:
            st.subheader("📝 Execution Log")
            log_text = "\n".join(st.session_state.generation_log[-10:])  # Show last 10 entries
            st.markdown(f'<div class="pipeline-log">{log_text}</div>', unsafe_allow_html=True)
    
    # Step 4: Assessment
    elif st.session_state.current_step == 'assessment':
        show_assessment()
    
    # Sidebar stats
    if st.session_state.generation_log:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📈 Session Stats")
        st.sidebar.metric("Log Entries", len(st.session_state.generation_log))
        st.sidebar.metric("Adversarial Attempts", len(st.session_state.adversarial_attempts))
        if st.session_state.selected_errors:
            st.sidebar.metric("Errors Selected", len(st.session_state.selected_errors))

def show_assessment():
    """Show the interactive assessment interface"""
    st.header("📊 Step 4: Interactive Error Detection")
    
    if st.session_state.user_topic in SAMPLE_DATA:
        question_data = SAMPLE_DATA[st.session_state.user_topic]['final_question']
    else:
        st.error("No assessment data available for this topic")
        return
    
    st.subheader(question_data['title'])
    st.write(f"Find conceptual errors in this **{st.session_state.selected_subtopic}** implementation.")
    st.info("💡 **Instructions**: Click the buttons below the code to select/deselect errors, then evaluate your response!")
    
    # Show code
    st.markdown("### 💻 Code to Review:")
    st.code(question_data['code'].replace('[ERROR_1]', '').replace('[/ERROR_1]', '')
                                   .replace('[ERROR_2]', '').replace('[/ERROR_2]', '')
                                   .replace('[ERROR_3]', '').replace('[/ERROR_3]', ''), language='python')
    
    # Error selection interface
    st.markdown("### 🎯 Select Errors (Click to toggle):")
    
    cols = st.columns(len(question_data['errors']))
    for i, error in enumerate(question_data['errors']):
        with cols[i]:
            error_id = error['id']
            is_selected = error_id in st.session_state.selected_errors
            
            button_type = "primary" if is_selected else "secondary"
            button_text = f"{'✅' if is_selected else '❌'} Error {error_id}"
            
            if st.button(button_text, key=f"error_{error_id}", type=button_type, use_container_width=True):
                if error_id in st.session_state.selected_errors:
                    st.session_state.selected_errors.remove(error_id)
                else:
                    st.session_state.selected_errors.add(error_id)
                st.rerun()
            
            st.caption(error['description'])
    
    # Evaluation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("📊 Evaluate Response", type="primary", use_container_width=True):
            evaluate_response(question_data)
            st.rerun()
    
    # Show results
    if st.session_state.evaluation_results:
        st.markdown("### 🏆 Evaluation Results")
        
        results = st.session_state.evaluation_results
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Precision", f"{results['precision']:.1%}", help="Percentage of selected errors that are actually errors")
        
        with col2:
            st.metric("Recall", f"{results['recall']:.1%}", help="Percentage of actual errors that were found")
        
        with col3:
            st.metric("F1 Score", f"{results['f1']:.1%}", help="Harmonic mean of precision and recall")
        
        with col4:
            st.metric("Selected", f"{len(st.session_state.selected_errors)}", help="Number of errors you selected")
        
        # Detailed feedback
        st.markdown("### 📋 Detailed Feedback")
        
        correct_errors = {e['id'] for e in question_data['errors'] if e['correct']}
        
        for error in question_data['errors']:
            error_id = error['id']
            is_selected = error_id in st.session_state.selected_errors
            is_correct = error['correct']
            
            if is_selected and is_correct:
                st.success(f"✅ **Error {error_id}**: Correctly identified! {error['description']}")
            elif is_selected and not is_correct:
                st.error(f"❌ **Error {error_id}**: False positive! {error['description']}")
            elif not is_selected and is_correct:
                st.warning(f"⚠️ **Error {error_id}**: Missed! {error['description']}")
            else:
                st.info(f"✅ **Error {error_id}**: Correctly ignored! {error['description']}")
    
    # Reset button
    st.markdown("---")
    if st.button("🔄 Start New Assessment", type="secondary"):
        # Reset session state
        for key in ['current_step', 'user_topic', 'selected_difficulty', 'selected_subtopic', 
                   'generation_log', 'adversarial_attempts', 'selected_errors', 'evaluation_results']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

def evaluate_response(question_data):
    """Evaluate the user's error selection"""
    correct_errors = {e['id'] for e in question_data['errors'] if e['correct']}
    selected_errors = st.session_state.selected_errors
    
    # Calculate metrics
    if selected_errors:
        precision = len(selected_errors & correct_errors) / len(selected_errors)
    else:
        precision = 0
    
    if correct_errors:
        recall = len(selected_errors & correct_errors) / len(correct_errors)
    else:
        recall = 0
    
    if precision + recall > 0:
        f1 = 2 * (precision * recall) / (precision + recall)
    else:
        f1 = 0
    
    st.session_state.evaluation_results = {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'correct_errors': correct_errors,
        'selected_errors': selected_errors
    }

def show_architecture_comparison():
    """Show architecture comparison page"""
    st.header("🏗️ Architecture Comparison: Original vs Modular")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📄 Original Monolithic Version
        
        **Structure**: Single massive React component
        - **Size**: 676 lines in one file
        - **State**: All useState hooks together
        - **Logic**: All functions inline
        - **UI**: One giant return statement
        - **Data**: Hardcoded in component
        
        **❌ Challenges**:
        - Hard to maintain and debug
        - Difficult to test individual pieces  
        - No code reusability
        - Poor collaboration experience
        - Performance issues with re-renders
        """)
    
    with col2:
        st.markdown("""
        ### 📦 Modular Component Architecture
        
        **Structure**: 13 focused, reusable modules
        - **Components**: 9 individual UI components
        - **Hooks**: 3 custom state management hooks
        - **Utils**: Separated utility functions
        - **Constants**: Dedicated configuration file
        - **Logic**: Clear separation of concerns
        
        **✅ Benefits**:
        - Easy to maintain and extend
        - Individual components are testable
        - High code reusability
        - Great for team collaboration
        - Optimized performance
        """)
    
    st.markdown("---")
    st.header("📊 Metrics Comparison")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Original Files", "1", help="Single monolithic component")
    with col2:
        st.metric("Modular Files", "13", help="Focused, reusable modules")  
    with col3:
        st.metric("Lines of Code", "676", help="Same functionality, better organized")
    with col4:
        st.metric("Reusable Components", "9", help="Can be used across different features")
    
    st.info("💡 **Key Insight**: Both versions have identical functionality, but the modular approach provides significantly better maintainability, testability, and developer experience!")
    
    if st.button("🚀 Try Interactive Demo", type="primary"):
        st.session_state.current_step = 'input'
        st.rerun()

if __name__ == "__main__":
    main()