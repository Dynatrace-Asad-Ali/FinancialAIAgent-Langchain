"""Improved MCP application with better structure and error handling."""
import streamlit as st
import asyncio
import json
import os
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Core imports
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_mcp_adapters.client import MultiServerMCPClient

# Local imports
from utils import astream_graph, random_uuid
from ui_components import (
    render_sidebar, render_chat_history, render_metrics,
    render_error_message, get_streaming_callback
)
from config_manager import ConfigManager
from session_manager import MCPSessionManager

load_dotenv()

# Initialize tracing if configured
try:
    from traceloop.sdk import Traceloop
    if os.environ.get("DYNATRACE_API_TOKEN"):
        headers = {"Authorization": f"Api-Token {os.environ.get('DYNATRACE_API_TOKEN')}"}
        Traceloop.init(
            app_name="MCPAgent",
            api_endpoint=os.environ.get("DYNATRACE_EXPORTER_OTLP_ENDPOINT"),
            headers=headers,
            disable_batch=True
        )
except ImportError:
    st.warning("Traceloop not available. Tracing disabled.")

# Page configuration
st.set_page_config(
    page_title="MCP Multi-Agent System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

class MCPApplication:
    """Main MCP application class."""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.session_manager = MCPSessionManager()
        self.metrics = {}
    
    def initialize_session_state(self):
        """Initialize Streamlit session state."""
        defaults = {
            "session_initialized": False,
            "agent": None,
            "history": [],
            "mcp_client": None,
            "timeout_seconds": 120,
            "selected_model": "gpt-4o-mini",
            "recursion_limit": 100,
            "thread_id": random_uuid(),
            "event_loop": None,
            "tool_count": 0,
            "pending_mcp_config": self.config_manager.load_config()
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
        
        # Initialize event loop
        if st.session_state.event_loop is None:
            loop = asyncio.new_event_loop()
            st.session_state.event_loop = loop
            asyncio.set_event_loop(loop)
    
    async def initialize_mcp_session(self, mcp_config: Optional[Dict] = None) -> bool:
        """Initialize MCP session with proper error handling."""
        try:
            with st.spinner("🔄 Connecting to MCP servers..."):
                # Cleanup existing client
                await self.session_manager.cleanup_client()
                
                if mcp_config is None:
                    mcp_config = self.config_manager.load_config()
                
                # Validate configuration
                if not self.config_manager.validate_config(mcp_config):
                    st.error("❌ Invalid MCP configuration")
                    return False
                
                # Initialize client
                client = MultiServerMCPClient(mcp_config)
                tools = await client.get_tools()
                
                st.session_state.tool_count = len(tools)
                st.session_state.mcp_client = client
                
                # Initialize model
                model = ChatOpenAI(
                    model=st.session_state.selected_model,
                    temperature=0,
                    max_tokens=16000,
                )
                
                # Create agent
                agent = create_react_agent(
                    model,
                    tools,
                    checkpointer=MemorySaver(),
                    prompt=self._get_system_prompt(),
                )
                
                st.session_state.agent = agent
                st.session_state.session_initialized = True
                
                st.success(f"✅ Connected to {len(tools)} tools across MCP servers")
                return True
                
        except Exception as e:
            st.error(f"❌ Failed to initialize MCP session: {str(e)}")
            return False
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent."""
        return """
You are an intelligent AI assistant with access to multiple specialized tools through MCP servers.

CAPABILITIES:
- Math operations and calculations
- Weather information lookup
- Dynatrace monitoring and observability queries
- General problem-solving and analysis

INSTRUCTIONS:
1. Analyze the user's question carefully
2. Select the most appropriate tool(s) to answer the question
3. Provide clear, professional, and helpful responses
4. If using tools, base your answer primarily on the tool output
5. Include sources when applicable (URLs or references)
6. Be concise but comprehensive in your responses

RESPONSE FORMAT:
- Direct answer to the question
- Supporting details from tools
- Sources (if applicable)

Remember: Only use the tools provided. Do not make up information.
"""
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process user query with comprehensive error handling."""
        if not st.session_state.get("session_initialized"):
            return {"error": "🚫 MCP session not initialized"}
        
        try:
            with st.chat_message("assistant", avatar="🤖"):
                text_placeholder = st.empty()
                tool_placeholder = st.empty()
                
                streaming_callback, accumulated_text, accumulated_tool = (
                    get_streaming_callback(text_placeholder, tool_placeholder)
                )
                
                response = await asyncio.wait_for(
                    astream_graph(
                        st.session_state.agent,
                        {"messages": [HumanMessage(content=query)]},
                        callback=streaming_callback,
                        config={
                            "recursion_limit": st.session_state.recursion_limit,
                            "thread_id": st.session_state.thread_id,
                        },
                    ),
                    timeout=st.session_state.timeout_seconds,
                )
                
                return {
                    "success": True,
                    "response": response,
                    "final_text": "".join(accumulated_text),
                    "final_tool": "".join(accumulated_tool)
                }
                
        except asyncio.TimeoutError:
            error_msg = f"⏱️ Request timed out after {st.session_state.timeout_seconds} seconds"
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"❌ Query processing failed: {str(e)}"
            return {"error": error_msg}
    
    def run(self):
        """Run the main application."""
        # Header
        st.title("🤖 MCP Multi-Agent System")
        st.markdown("*Intelligent assistance powered by Model Context Protocol*")
        
        # Initialize session
        self.initialize_session_state()
        
        # Sidebar configuration
        config = render_sidebar()
        
        # Update session state
        st.session_state.timeout_seconds = config["timeout"]
        st.session_state.recursion_limit = config["recursion_limit"]
        st.session_state.selected_model = config["model"]
        
        # Initialize MCP session if needed
        if not st.session_state.get("session_initialized"):
            success = st.session_state.event_loop.run_until_complete(
                self.initialize_mcp_session(st.session_state.pending_mcp_config)
            )
            if not success:
                st.stop()
        
        # Main content
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Chat interface
            render_chat_history()
            
            # Chat input
            user_query = st.chat_input("💬 Ask about math, weather, or Dynatrace...")
            
            if user_query:
                # Add user message
                st.session_state.history.append({"role": "user", "content": user_query})
                
                # Display user message
                with st.chat_message("user", avatar="🧑‍💻"):
                    st.markdown(user_query)
                
                # Process query
                result = st.session_state.event_loop.run_until_complete(
                    self.process_query(user_query)
                )
                
                if "error" in result:
                    render_error_message(result["error"])
                else:
                    # Add assistant response to history
                    st.session_state.history.append({
                        "role": "assistant",
                        "content": result["final_text"]
                    })
                    
                    if result["final_tool"].strip():
                        st.session_state.history.append({
                            "role": "assistant_tool",
                            "content": result["final_tool"]
                        })
                
                st.rerun()
        
        with col2:
            # Metrics and status
            render_metrics(st.session_state.get("tool_count", 0))
            
            # System status
            st.subheader("🔧 System Status")
            status_data = {
                "MCP Servers": "✅ Connected" if st.session_state.get("session_initialized") else "❌ Disconnected",
                "Tools Available": st.session_state.get("tool_count", 0),
                "Model": st.session_state.get("selected_model", "N/A"),
                "Session": f"Active ({len(st.session_state.get('history', []))} messages)"
            }
            
            for key, value in status_data.items():
                st.write(f"**{key}:** {value}")

if __name__ == "__main__":
    app = MCPApplication()
    app.run()