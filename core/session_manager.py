"""Session management for Streamlit app."""
import streamlit as st
import asyncio
from typing import Optional, Dict, Any
from core.logging_config import setup_logging
from core.exceptions import AgentInitializationError

logger = setup_logging()

class SessionManager:
    """Manages Streamlit session state and initialization."""
    
    @staticmethod
    def initialize_session_state():
        """Initialize session state variables."""
        defaults = {
            "session_initialized": False,
            "agent": None,
            "history": [],
            "timeout_seconds": 120,
            "recursion_limit": 100,
            "thread_id": SessionManager._generate_thread_id(),
            "event_loop": None
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
        
        # Initialize event loop if not exists
        if st.session_state.event_loop is None:
            loop = asyncio.new_event_loop()
            st.session_state.event_loop = loop
            asyncio.set_event_loop(loop)
    
    @staticmethod
    def _generate_thread_id() -> str:
        """Generate a unique thread ID."""
        import uuid
        return str(uuid.uuid4())
    
    @staticmethod
    def reset_session():
        """Reset session state."""
        keys_to_reset = ["agent", "history", "session_initialized"]
        for key in keys_to_reset:
            if key in st.session_state:
                del st.session_state[key]
        
        SessionManager.initialize_session_state()
        logger.info("Session reset completed")
    
    @staticmethod
    def get_session_info() -> Dict[str, Any]:
        """Get current session information."""
        return {
            "initialized": st.session_state.get("session_initialized", False),
            "history_length": len(st.session_state.get("history", [])),
            "thread_id": st.session_state.get("thread_id", "unknown"),
            "timeout": st.session_state.get("timeout_seconds", 120)
        }