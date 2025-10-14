"""
Streamlit Developer Mode - 7-Step Pipeline Visualization

This app provides real-time visualization of the adversarial question generation pipeline.
It's designed for:
- Debugging prompt engineering
- Monitoring LLM responses
- Tracking pipeline performance
- Demonstrating the system to stakeholders

NOT for end users - this is the technical/developer view.
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime
import sseclient

# Page config
st.set_page_config(
    page_title="Aqumen Pipeline - Dev Mode",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .step-container {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .step-success {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
    }
    .step-pending {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
    }
    .step-error {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
    }
    .step-running {
        background-color: #cce5ff;
        border-left: 4px solid #004085;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    .metric-card {
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.title("🔬 Dev Mode Settings")

    # Demo mode toggle
    demo_mode = st.checkbox(
        "📺 Demo Mode (Use Hardcoded Example)",
        value=False,
        help="Show pre-generated assessment instead of calling API"
    )

    # API endpoint configuration
    api_endpoint = st.text_input(
        "API Endpoint",
        value="http://localhost:8000",
        help="FastAPI backend URL (local or deployed)",
        disabled=demo_mode
    )

    st.divider()

    # Model info display
    if st.button("📊 View Model Info"):
        try:
            response = requests.get(f"{api_endpoint}/api/models")
            if response.status_code == 200:
                models_info = response.json()
                st.json(models_info)
            else:
                st.error(f"Failed to fetch model info: {response.status_code}")
        except Exception as e:
            st.error(f"Error: {e}")

    st.divider()

    # About section
    st.markdown("""
    ### About Dev Mode

    This interface shows:
    - ✅ Real-time step completion
    - 📝 Full prompts sent to LLMs
    - 📊 Complete LLM responses
    - ⏱️ Timing for each step
    - 🔄 Retry attempts
    - ❌ Failure reasons

    Perfect for debugging and demos!
    """)

# Main content
st.title("🎯 Adversarial Assessment Pipeline")
st.markdown("**Developer Mode** - Real-time 7-Step Execution Monitor")

# Topic input
col1, col2 = st.columns([3, 1])
with col1:
    topic = st.text_input(
        "Enter AI/ML Topic:",
        placeholder="e.g., Group-Relative Policy Optimization in Multi-Task RL",
        help="Be specific! The more detailed, the better the generated question."
    )

with col2:
    max_retries = st.number_input(
        "Max Retries:",
        min_value=1,
        max_value=5,
        value=3,
        help="Number of attempts if differentiation fails"
    )

# Generate button
if st.button("🚀 Generate Question", type="primary", disabled=not topic):
    # Initialize session state for tracking
    if 'steps' not in st.session_state:
        st.session_state.steps = {}
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None

    st.session_state.start_time = time.time()
    st.session_state.steps = {}

    # DEMO MODE: Load hardcoded assessment with all steps
    if demo_mode:
        st.info("📺 Demo Mode - Showing pre-generated assessment from Agentic Evals run")

        try:
            import os
            demo_file = os.path.join(os.path.dirname(__file__), 'demo_assessment_with_steps.json')
            with open(demo_file, 'r') as f:
                demo_data = json.load(f)

            # Display summary metrics at top
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Topic", demo_data['topic'][:20] + "...")
            with col2:
                st.metric("Difficulty", demo_data['difficulty'])
            with col3:
                st.metric("Quality Score", demo_data['quality_score'])
            with col4:
                total_steps = len(demo_data.get('all_steps', []))
                st.metric("Total Steps", total_steps)

            st.markdown("---")

            # Create tabs for each step
            if 'all_steps' in demo_data and demo_data['all_steps']:
                steps = demo_data['all_steps']

                # Create tab names based on steps
                tab_names = []
                for step in steps:
                    step_num = step['step_number']
                    step_name = step['step_name']
                    status = "✅" if step['success'] else "❌"
                    tab_names.append(f"{status} Step {step_num}")

                # Add final assessment tab
                tab_names.append("🎯 Final Assessment")

                # Create tabs
                tabs = st.tabs(tab_names)

                # Display each step in its tab
                for i, step in enumerate(steps):
                    with tabs[i]:
                        st.markdown(f"### Step {step['step_number']}: {step['step_name']}")

                        # Step metadata
                        meta_cols = st.columns(3)
                        with meta_cols[0]:
                            st.metric("Model", step['model_used'])
                        with meta_cols[1]:
                            status_emoji = "✅ Success" if step['success'] else "❌ Failed"
                            st.metric("Status", status_emoji)
                        with meta_cols[2]:
                            st.metric("Timestamp", step['timestamp'].split('T')[1][:8])

                        st.markdown("---")

                        # Full response
                        st.markdown("#### 📝 Full LLM Response")
                        response_text = step['response']

                        # Show preview (first 1000 chars) with expander for full
                        if len(response_text) > 1000:
                            st.code(response_text[:1000], language="text")
                            with st.expander("📖 Show Full Response"):
                                st.code(response_text, language="text")
                        else:
                            st.code(response_text, language="text")

                        # Special handling for Step 7 - show if it was a retry
                        if step['step_number'] == 7:
                            # Check if there are multiple step 7s (retry logic)
                            step_7_attempts = [s for s in steps if s['step_number'] == 7]
                            if len(step_7_attempts) > 1:
                                attempt_num = step_7_attempts.index(step) + 1
                                if not step['success']:
                                    st.warning(f"⚠️ This was attempt {attempt_num} - validation failed, triggered retry")
                                else:
                                    st.success(f"✅ This was attempt {attempt_num} - validation passed!")

                # Final assessment tab
                with tabs[-1]:
                    st.markdown("### 🎯 Final Assessment - Student View")

                    st.markdown(f"**Title:** {demo_data['title']}")
                    st.markdown(f"**Difficulty:** {demo_data['difficulty']}")
                    st.markdown(f"**Topic:** {demo_data['topic']}")

                    st.markdown("---")

                    # Show code with errors highlighted
                    st.markdown("#### 💻 Generated Code")
                    code_text = "\n".join(demo_data['code'])
                    st.code(code_text, language="python")

                    # Show errors
                    st.markdown("#### 🔍 Identified Errors (Student Must Find)")
                    for i, error in enumerate(demo_data['errors'], 1):
                        with st.expander(f"Error {i}: {error['id']}", expanded=True):
                            st.error(error['description'])
                            st.caption(f"Line: {error['line_number']}")

                    # Show metadata
                    with st.expander("📊 Pipeline Metadata & Scoring"):
                        st.json(demo_data['metadata'])

            else:
                # Fallback to old format if no steps available
                st.warning("⚠️ No step-by-step data available. Showing final assessment only.")

                st.markdown("### ✅ Final Assessment Generated")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Title", demo_data['title'][:30] + "...")
                with col2:
                    st.metric("Difficulty", demo_data['difficulty'])
                with col3:
                    st.metric("Quality Score", demo_data['quality_score'])

                code_text = "\n".join(demo_data['code'])
                st.code(code_text, language="python")

                for i, error in enumerate(demo_data['errors'], 1):
                    with st.expander(f"Error {i}: {error['id']}", expanded=True):
                        st.error(error['description'])

            st.success(f"✅ Demo assessment loaded! Generated from: '{demo_data['topic']}'")

        except Exception as e:
            st.error(f"Failed to load demo data: {e}")
            import traceback
            st.code(traceback.format_exc())

        st.stop()  # Don't continue to API call

    # Create placeholders for real-time updates
    progress_container = st.container()
    tabs_container = st.container()
    result_container = st.container()

    with progress_container:
        st.markdown("### 📊 Pipeline Progress")
        progress_bar = st.progress(0, text="Initializing...")
        metrics_cols = st.columns(4)

        with metrics_cols[0]:
            elapsed_metric = st.empty()
        with metrics_cols[1]:
            completed_metric = st.empty()
        with metrics_cols[2]:
            current_step_metric = st.empty()
        with metrics_cols[3]:
            status_metric = st.empty()

    # Pre-create tabs for all 7 steps + final result
    with tabs_container:
        st.markdown("---")
        tab_names = [
            "⏳ Step 1", "⏳ Step 2", "⏳ Step 3", "⏳ Step 4",
            "⏳ Step 5", "⏳ Step 6", "⏳ Step 7", "🎯 Final"
        ]
        tabs = st.tabs(tab_names)

        # Create placeholders within each tab
        step_tab_placeholders = {}
        for i in range(1, 8):
            with tabs[i-1]:
                step_tab_placeholders[i] = {
                    'header': st.empty(),
                    'metadata': st.empty(),
                    'divider': st.empty(),
                    'response': st.empty(),
                    'status_note': st.empty()
                }

        # Final result tab placeholder
        with tabs[7]:
            final_placeholder = st.empty()

    # Connect to SSE stream
    try:
        stream_url = f"{api_endpoint}/api/generate-stream?topic={topic}&max_retries={max_retries}"

        with requests.get(stream_url, stream=True, headers={'Accept': 'text/event-stream'}) as response:
            if response.status_code != 200:
                st.error(f"Failed to connect to API: {response.status_code}")
                st.stop()

            client = sseclient.SSEClient(response)
            steps_completed = 0
            current_step = 0

            for event in client.events():
                elapsed = time.time() - st.session_state.start_time

                # Update metrics
                elapsed_metric.metric("⏱️ Elapsed", f"{elapsed:.1f}s")
                completed_metric.metric("✅ Completed", steps_completed)
                current_step_metric.metric("🔄 Current", f"Step {current_step}")

                if event.event == "start":
                    data = json.loads(event.data)
                    status_metric.metric("📡 Status", "Running", delta="Connected")
                    st.info(f"🚀 Pipeline started at {data['timestamp']}")

                elif event.event == "step":
                    data = json.loads(event.data)

                    if data['type'] == 'step':
                        step_num = data['step_number']
                        current_step = step_num

                        # Store step data
                        st.session_state.steps[step_num] = data

                        # Update progress bar
                        progress = step_num / 7
                        progress_bar.progress(progress, text=f"Step {step_num}/7: {data['description']}")

                        # Update the tab for this step
                        placeholders = step_tab_placeholders[step_num]

                        # Header
                        status_emoji = "✅" if data['success'] else "❌"
                        placeholders['header'].markdown(f"### {status_emoji} Step {step_num}: {data['description']}")

                        # Metadata columns
                        with placeholders['metadata']:
                            meta_cols = st.columns(3)
                            with meta_cols[0]:
                                st.metric("Model", data['model'])
                            with meta_cols[1]:
                                status_text = "✅ Success" if data['success'] else "❌ Failed"
                                st.metric("Status", status_text)
                            with meta_cols[2]:
                                timestamp = data['timestamp'].split('T')[1][:8] if 'T' in data['timestamp'] else data['timestamp']
                                st.metric("Timestamp", timestamp)

                        placeholders['divider'].markdown("---")

                        # Response
                        with placeholders['response']:
                            st.markdown("#### 📝 Full LLM Response")
                            response_text = data.get('response_full', 'No response')

                            if len(response_text) > 1000:
                                st.code(response_text[:1000], language="text")
                                with st.expander("📖 Show Full Response"):
                                    st.code(response_text, language="text")
                            else:
                                st.code(response_text, language="text")

                        # Status note for special cases
                        if not data['success'] and step_num == 7:
                            placeholders['status_note'].warning("⚠️ Step 7 validation failed - will retry with feedback")

                        if data['success']:
                            steps_completed += 1

                    elif data['type'] == 'final':
                        # Final result received
                        status_metric.metric("📡 Status", "Complete", delta="Success")
                        progress_bar.progress(1.0, text="✅ Pipeline Complete!")

                        # Populate the Final tab
                        with final_placeholder.container():
                            st.markdown("### 🎯 Final Assessment - Student View")

                            # Display summary metrics
                            result_cols = st.columns(4)
                            with result_cols[0]:
                                st.metric(
                                    "Success",
                                    "✅ Yes" if data['success'] else "❌ No"
                                )
                            with result_cols[1]:
                                st.metric(
                                    "Differentiation",
                                    "✅ Achieved" if data['differentiation_achieved'] else "❌ Failed"
                                )
                            with result_cols[2]:
                                st.metric(
                                    "Attempts",
                                    data['total_attempts']
                                )
                            with result_cols[3]:
                                st.metric(
                                    "Stopped At",
                                    f"Step {data['stopped_at_step']}"
                                )

                            st.markdown("---")

                            # Display assessment if generated
                            if data.get('assessment'):
                                assessment = data['assessment']

                                # Show title/topic info
                                if 'title' in assessment:
                                    st.markdown(f"**Title:** {assessment['title']}")
                                if 'difficulty' in assessment:
                                    st.markdown(f"**Difficulty:** {assessment['difficulty']}")

                                st.markdown("---")

                                # Extract and display code with errors
                                if 'code' in assessment and 'errors' in assessment:
                                    st.markdown("#### 💻 Generated Code")
                                    code_text = "\n".join(assessment['code'])
                                    st.code(code_text, language="python")

                                    st.markdown("#### 🔍 Identified Errors (Student Must Find)")
                                    for i, error in enumerate(assessment['errors'], 1):
                                        with st.expander(f"Error {i}: {error['id']}", expanded=True):
                                            st.error(error['description'])
                                            if 'line_number' in error:
                                                st.caption(f"Line: {error['line_number']}")

                                # Raw JSON view
                                with st.expander("📋 Raw Assessment JSON"):
                                    st.json(data['assessment'])

                            # Display metadata
                            if data.get('metadata'):
                                with st.expander("📊 Pipeline Metadata & Scoring"):
                                    st.json(data['metadata'])

                        # Also show summary in result container below tabs
                        with result_container:
                            st.markdown("---")
                            st.success(f"✅ Pipeline completed successfully! Check the **🎯 Final** tab above to see the generated assessment.")

                elif event.event == "error":
                    data = json.loads(event.data)
                    status_metric.metric("📡 Status", "Error", delta="Failed")
                    st.error(f"❌ Pipeline Error: {data.get('error', 'Unknown error')}")
                    break

                elif event.event == "done":
                    data = json.loads(event.data)
                    total_duration = data.get('total_duration_seconds', elapsed)
                    st.success(f"✅ Pipeline completed in {total_duration:.2f} seconds")
                    break

    except requests.exceptions.ConnectionError:
        st.error(f"""
        ❌ **Connection Error**

        Could not connect to the API at `{api_endpoint}`.

        **Troubleshooting:**
        1. Make sure the FastAPI backend is running:
           ```bash
           cd backend
           uvicorn api_server:app --reload --port 8000
           ```
        2. Check the API endpoint URL in the sidebar
        3. Verify CORS is enabled for localhost
        """)

    except Exception as e:
        st.error(f"❌ Unexpected Error: {str(e)}")
        st.exception(e)

# Instructions when no generation is running
if 'steps' not in st.session_state or not st.session_state.steps:
    st.info("""
    ### 👋 Welcome to Pipeline Dev Mode!

    **How to use:**
    1. Enter an AI/ML topic (be specific!)
    2. Set max retries (usually 3 is good)
    3. Click "Generate Question"
    4. Watch the pipeline execute in real-time!

    **What you'll see:**
    - Each step completing live
    - Full prompts and responses
    - Timing and performance metrics
    - Final assessment (if successful)

    **Tips:**
    - More specific topics = better questions
    - Watch Step 6 (Judge) carefully - it determines success
    - If Step 7 fails validation, you'll see the exact errors
    - Use expanders to dive into full LLM responses
    """)

    # Show example topics
    st.markdown("### 💡 Example Topics")
    example_topics = [
        "Group-Relative Policy Optimization in Multi-Task RL",
        "Attention Mask Broadcasting in Transformer Models",
        "Gradient Accumulation for Large Batch Training",
        "RLHF Reward Model Training with Bradley-Terry Loss",
        "RAG Document Retrieval with Vector Similarity",
    ]

    for topic_example in example_topics:
        if st.button(f"📝 {topic_example}", key=topic_example):
            st.session_state.example_topic = topic_example
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em;">
    🔬 Aqumen Pipeline Developer Mode | For debugging and demonstration purposes
</div>
""", unsafe_allow_html=True)
