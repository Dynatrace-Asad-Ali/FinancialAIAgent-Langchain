"""Improved main application with better structure and error handling."""
import streamlit as st
import asyncio
from typing import Optional, Dict, Any
import time

# Local imports
from config.settings import load_config, validate_config
from core.exceptions import FinancialAgentError, ConfigurationError
from core.logging_config import setup_logging
from core.session_manager import SessionManager
from ui.components import (
    render_sidebar, render_chat_history, render_example_queries,
    render_metrics_dashboard, render_error_message
)
from agents.improved_news_agent import NewsAgent
from agents.improved_fundamental_agent import FundamentalAgent
from agents.technical_agent import technical_agent
from agents.humorous_news_agent import humorous_news_agent
from agents.supervisor_agent import supervisor_agent
from utils.utils import astream_graph
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

# Initialize logging
logger = setup_logging()

# Page configuration
st.set_page_config(
    page_title="Financial AI Agent",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

class FinancialAgentApp:
    """Main application class."""
    
    def __init__(self):
        self.api_config, self.app_config = load_config()
        self.supervisor = None
        self.metrics = {}
    
    def validate_configuration(self) -> bool:
        """Validate application configuration."""
        errors = validate_config(self.api_config)
        
        if errors:
            st.error("❌ Configuration Error")
            for error in errors:
                st.error(f"• {error}")
            
            st.info("Please check your environment variables and restart the application.")
            return False
        
        return True
    
    def initialize_agents(self) -> bool:
        """Initialize all agents."""
        try:
            with st.spinner("🔄 Initializing AI agents..."):
                # Initialize individual agents
                news_agent_instance = NewsAgent(self.app_config.default_model)
                fundamental_agent_instance = FundamentalAgent(self.app_config.default_model)
                technical_agent_instance = technical_agent()
                humorous_agent_instance = humorous_news_agent()
                
                # Initialize supervisor
                self.supervisor = supervisor_agent(
                    news_agent_instance.agent,
                    fundamental_agent_instance.agent,
                    technical_agent_instance,
                    humorous_agent_instance
                ).compile()
                
                st.session_state.agent = self.supervisor
                st.session_state.session_initialized = True
                
                logger.info("All agents initialized successfully")
                return True
                
        except Exception as e:
            logger.error(f"Agent initialization failed: {str(e)}")
            render_error_message("Failed to initialize agents", str(e))
            return False
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process user query with metrics tracking."""
        start_time = time.time()
        
        try:
            if not st.session_state.get("session_initialized"):
                raise FinancialAgentError("Agents not initialized")
            
            # Create placeholders for streaming
            with st.chat_message("assistant", avatar="🤖"):
                text_placeholder = st.empty()
                tool_placeholder = st.empty()
                
                # Process query
                response = await astream_graph(
                    st.session_state.agent,
                    {"messages": [HumanMessage(content=query)]},
                    callback=self._create_streaming_callback(text_placeholder, tool_placeholder),
                    config=RunnableConfig(
                        recursion_limit=st.session_state.recursion_limit,
                        thread_id=st.session_state.thread_id,
                    ),
                )
                
                # Calculate metrics
                end_time = time.time()
                self.metrics = {
                    "response_time": end_time - start_time,
                    "tools_used": 1,  # Simplified
                    "agents_used": 1,  # Simplified
                    "success_rate": 1.0
                }
                
                return {"success": True, "response": response}
                
        except asyncio.TimeoutError:
            error_msg = f"Request timed out after {st.session_state.timeout_seconds} seconds"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
            
        except Exception as e:
            error_msg = f"Query processing failed: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _create_streaming_callback(self, text_placeholder, tool_placeholder):
        """Create streaming callback for real-time updates."""
        accumulated_text = []
        accumulated_tool = []
        
        def callback(message: dict):
            nonlocal accumulated_text, accumulated_tool
            
            content = message.get("content")
            if hasattr(content, "content") and isinstance(content.content, str):
                accumulated_text.append(content.content)
                text_placeholder.markdown("".join(accumulated_text))
            
            # Handle tool calls (simplified)
            if hasattr(content, "tool_calls") and content.tool_calls:
                tool_info = str(content.tool_calls[0])
                accumulated_tool.append(tool_info)
                with tool_placeholder.expander("🔧 Tool Information", expanded=True):
                    st.code("".join(accumulated_tool), language="json")
        
        return callback
    
    def run(self):
        """Run the main application."""
        # Header
        st.title("📈 Financial AI Agent")
        st.markdown("*Comprehensive stock analysis powered by AI*")
        
        # Validate configuration
        if not self.validate_configuration():
            return
        
        # Initialize session
        SessionManager.initialize_session_state()
        
        # Render sidebar
        config = render_sidebar()
        
        # Update session state with new config
        st.session_state.timeout_seconds = config["timeout"]
        st.session_state.recursion_limit = config["recursion_limit"]
        
        # Initialize agents if not done
        if not st.session_state.get("session_initialized"):
            if not self.initialize_agents():
                return
        
        # Main content area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Chat interface
            render_chat_history()
            
            # Example queries
            example_query = render_example_queries()
            
            # Chat input
            user_input = st.chat_input("💬 Ask about stocks, news, or analysis...")
            
            # Process input
            query = example_query or user_input
            if query:
                # Add user message to history
                st.session_state.history.append({"role": "user", "content": query})
                
                # Display user message
                with st.chat_message("user", avatar="🧑‍💻"):
                    st.markdown(query)
                
                # Process query
                result = st.session_state.event_loop.run_until_complete(
                    self.process_query(query)
                )
                
                if result["success"]:
                    # Add assistant response to history
                    st.session_state.history.append({
                        "role": "assistant", 
                        "content": "Analysis completed successfully"
                    })
                else:
                    render_error_message(result["error"])
                
                st.rerun()
        
        with col2:
            # Metrics dashboard
            render_metrics_dashboard(self.metrics)
            
            # System status
            st.subheader("🔧 System Status")
            status_data = {
                "Agents": "✅ Online" if st.session_state.get("session_initialized") else "❌ Offline",
                "Model": config["model"],
                "Session": f"Active ({len(st.session_state.get('history', []))} messages)"
            }
            
            for key, value in status_data.items():
                st.write(f"**{key}:** {value}")

if __name__ == "__main__":
    app = FinancialAgentApp()
    app.run()