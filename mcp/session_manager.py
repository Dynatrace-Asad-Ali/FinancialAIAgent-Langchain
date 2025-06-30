"""Session management for MCP application."""
import streamlit as st
from typing import Optional
import asyncio

class MCPSessionManager:
    """Manages MCP session lifecycle."""
    
    async def cleanup_client(self):
        """Safely cleanup existing MCP client."""
        if "mcp_client" in st.session_state and st.session_state.mcp_client is not None:
            try:
                await st.session_state.mcp_client.__aexit__(None, None, None)
                st.session_state.mcp_client = None
            except Exception as e:
                # Log but don't show error to user for cleanup
                pass
    
    def reset_session(self):
        """Reset the current session."""
        keys_to_reset = [
            "session_initialized", "agent", "history", 
            "mcp_client", "tool_count"
        ]
        
        for key in keys_to_reset:
            if key in st.session_state:
                del st.session_state[key]
        
        st.success("🔄 Session reset successfully")
    
    def get_session_info(self) -> dict:
        """Get current session information."""
        return {
            "initialized": st.session_state.get("session_initialized", False),
            "tool_count": st.session_state.get("tool_count", 0),
            "history_length": len(st.session_state.get("history", [])),
            "thread_id": st.session_state.get("thread_id", "unknown"),
            "model": st.session_state.get("selected_model", "unknown")
        }