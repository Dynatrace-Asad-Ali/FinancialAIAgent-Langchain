"""Reusable UI components for Streamlit app."""
import streamlit as st
from typing import List, Dict, Any, Optional
from core.session_manager import SessionManager

def render_sidebar() -> Dict[str, Any]:
    """Render sidebar with configuration options."""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Model selection
        model_options = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
        selected_model = st.selectbox(
            "Select Model",
            model_options,
            index=0,
            help="Choose the AI model for analysis"
        )
        
        # Timeout settings
        timeout = st.slider(
            "Timeout (seconds)",
            min_value=30,
            max_value=300,
            value=st.session_state.get("timeout_seconds", 120),
            step=30,
            help="Maximum time to wait for responses"
        )
        
        # Recursion limit
        recursion_limit = st.slider(
            "Recursion Limit",
            min_value=10,
            max_value=200,
            value=st.session_state.get("recursion_limit", 100),
            step=10,
            help="Maximum number of agent interactions"
        )
        
        # Session management
        st.subheader("Session Management")
        session_info = SessionManager.get_session_info()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Reset Session", type="secondary"):
                SessionManager.reset_session()
                st.rerun()
        
        with col2:
            if st.button("Session Info", type="secondary"):
                st.json(session_info)
        
        # Display current settings
        st.subheader("Current Settings")
        st.write(f"**Model:** {selected_model}")
        st.write(f"**Timeout:** {timeout}s")
        st.write(f"**Recursion Limit:** {recursion_limit}")
        st.write(f"**Initialized:** {session_info['initialized']}")
        
        return {
            "model": selected_model,
            "timeout": timeout,
            "recursion_limit": recursion_limit
        }

def render_chat_history():
    """Render chat history with improved formatting."""
    if not st.session_state.get("history"):
        st.info("💡 Start by asking about a stock analysis, latest news, or fundamental analysis!")
        return
    
    for i, message in enumerate(st.session_state.history):
        if message["role"] == "user":
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(message["content"])
        
        elif message["role"] == "assistant":
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(message["content"])
                
                # Check for tool information
                if (i + 1 < len(st.session_state.history) and 
                    st.session_state.history[i + 1]["role"] == "assistant_tool"):
                    with st.expander("🔧 Tool Details", expanded=False):
                        st.code(st.session_state.history[i + 1]["content"], language="json")

def render_example_queries():
    """Render example queries for users."""
    st.subheader("💡 Example Queries")
    
    examples = [
        "Analyze AAPL stock comprehensively",
        "What's the latest news on Tesla?",
        "Perform fundamental analysis on Microsoft",
        "Give me technical analysis for NVDA",
        "Compare Apple and Microsoft fundamentals"
    ]
    
    cols = st.columns(len(examples))
    for i, example in enumerate(examples):
        with cols[i % len(cols)]:
            if st.button(example, key=f"example_{i}", use_container_width=True):
                return example
    
    return None

def render_metrics_dashboard(metrics: Optional[Dict[str, Any]] = None):
    """Render metrics dashboard."""
    if not metrics:
        return
    
    st.subheader("📊 Analysis Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Response Time", f"{metrics.get('response_time', 0):.2f}s")
    
    with col2:
        st.metric("Tools Used", metrics.get('tools_used', 0))
    
    with col3:
        st.metric("Agents Involved", metrics.get('agents_used', 0))
    
    with col4:
        st.metric("Success Rate", f"{metrics.get('success_rate', 0):.1%}")

def render_error_message(error: str, details: Optional[str] = None):
    """Render error message with details."""
    st.error(f"❌ {error}")
    
    if details:
        with st.expander("Error Details"):
            st.code(details, language="text")
    
    st.info("💡 Try rephrasing your question or check your configuration.")