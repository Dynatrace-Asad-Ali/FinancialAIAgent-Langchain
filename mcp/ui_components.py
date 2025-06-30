"""UI components for MCP application."""
import streamlit as st
from typing import Dict, Any, Optional, Tuple, List, Callable
from langchain_core.messages.ai import AIMessageChunk
from langchain_core.messages.tool import ToolMessage

def render_sidebar() -> Dict[str, Any]:
    """Render sidebar with configuration options."""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Model selection
        model_options = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
        selected_model = st.selectbox(
            "Select Model",
            model_options,
            index=model_options.index(st.session_state.get("selected_model", "gpt-4o-mini")),
            help="Choose the AI model"
        )
        
        # Timeout settings
        timeout = st.slider(
            "Timeout (seconds)",
            min_value=30,
            max_value=300,
            value=st.session_state.get("timeout_seconds", 120),
            step=30
        )
        
        # Recursion limit
        recursion_limit = st.slider(
            "Recursion Limit",
            min_value=10,
            max_value=200,
            value=st.session_state.get("recursion_limit", 100),
            step=10
        )
        
        # Session management
        st.subheader("Session Management")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Reset Session", type="secondary"):
                from session_manager import MCPSessionManager
                manager = MCPSessionManager()
                manager.reset_session()
                st.rerun()
        
        with col2:
            if st.button("Session Info", type="secondary"):
                from session_manager import MCPSessionManager
                manager = MCPSessionManager()
                st.json(manager.get_session_info())
        
        return {
            "model": selected_model,
            "timeout": timeout,
            "recursion_limit": recursion_limit
        }

def render_chat_history():
    """Render chat history with improved formatting."""
    if not st.session_state.get("history"):
        st.info("💡 Ask about math operations, weather, or Dynatrace monitoring!")
        
        # Example queries
        st.subheader("💡 Try these examples:")
        examples = [
            "What is 25 * 47?",
            "What's the weather in New York?",
            "List Dynatrace capabilities",
            "Calculate the square root of 144"
        ]
        
        for example in examples:
            if st.button(example, key=f"example_{example}", use_container_width=True):
                st.session_state.history.append({"role": "user", "content": example})
                st.rerun()
        return
    
    # Display chat history
    i = 0
    while i < len(st.session_state.history):
        message = st.session_state.history[i]
        
        if message["role"] == "user":
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(message["content"])
            i += 1
            
        elif message["role"] == "assistant":
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(message["content"])
                
                # Check for tool information
                if (i + 1 < len(st.session_state.history) and 
                    st.session_state.history[i + 1]["role"] == "assistant_tool"):
                    with st.expander("🔧 Tool Information", expanded=False):
                        st.code(st.session_state.history[i + 1]["content"], language="json")
                    i += 2
                else:
                    i += 1
        else:
            i += 1

def render_metrics(tool_count: int):
    """Render metrics dashboard."""
    st.subheader("📊 System Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Available Tools", tool_count)
    
    with col2:
        st.metric("Active Sessions", 1 if st.session_state.get("session_initialized") else 0)
    
    # Server status
    st.subheader("🌐 Server Status")
    servers = ["Math Server", "Weather Server", "Dynatrace Server"]
    
    for server in servers:
        status = "🟢 Online" if st.session_state.get("session_initialized") else "🔴 Offline"
        st.write(f"**{server}:** {status}")

def render_error_message(error: str, details: Optional[str] = None):
    """Render error message with details."""
    st.error(error)
    
    if details:
        with st.expander("Error Details"):
            st.code(details, language="text")

def get_streaming_callback(text_placeholder, tool_placeholder) -> Tuple[Callable, List, List]:
    """Create streaming callback for real-time updates."""
    accumulated_text = []
    accumulated_tool = []
    
    def callback_func(message: dict):
        nonlocal accumulated_text, accumulated_tool
        message_content = message.get("content", None)
        
        if isinstance(message_content, AIMessageChunk):
            content = message_content.content
            
            # Handle different content types
            if isinstance(content, list) and len(content) > 0:
                message_chunk = content[0]
                if message_chunk.get("type") == "text":
                    accumulated_text.append(message_chunk["text"])
                    text_placeholder.markdown("".join(accumulated_text))
                elif message_chunk.get("type") == "tool_use":
                    tool_info = message_chunk.get("partial_json", str(message_chunk))
                    accumulated_tool.append(f"\n```json\n{tool_info}\n```\n")
                    with tool_placeholder.expander("🔧 Tool Information", expanded=True):
                        st.markdown("".join(accumulated_tool))
            
            elif isinstance(content, str):
                accumulated_text.append(content)
                text_placeholder.markdown("".join(accumulated_text))
            
            elif hasattr(message_content, "tool_calls") and message_content.tool_calls:
                tool_call_info = message_content.tool_calls[0]
                accumulated_tool.append(f"\n```json\n{str(tool_call_info)}\n```\n")
                with tool_placeholder.expander("🔧 Tool Information", expanded=True):
                    st.markdown("".join(accumulated_tool))
        
        elif isinstance(message_content, ToolMessage):
            accumulated_tool.append(f"\n```json\n{str(message_content.content)}\n```\n")
            with tool_placeholder.expander("🔧 Tool Information", expanded=True):
                st.markdown("".join(accumulated_tool))
    
    return callback_func, accumulated_text, accumulated_tool