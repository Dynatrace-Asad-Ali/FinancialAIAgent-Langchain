"""Unit tests for agents."""
import pytest
from unittest.mock import Mock, patch
from agents.improved_news_agent import NewsAgent
from agents.improved_fundamental_agent import FundamentalAgent
from core.exceptions import AgentInitializationError, ToolExecutionError

class TestNewsAgent:
    """Test cases for NewsAgent."""
    
    def test_initialization(self):
        """Test agent initialization."""
        agent = NewsAgent()
        assert agent.name == "news_agent"
        assert agent.model == "gpt-4o-mini"
    
    def test_get_tools(self):
        """Test tool retrieval."""
        agent = NewsAgent()
        tools = agent.get_tools()
        assert len(tools) > 0
    
    def test_get_prompt(self):
        """Test prompt generation."""
        agent = NewsAgent()
        prompt = agent.get_prompt()
        assert "news agent" in prompt.lower()
        assert "instructions" in prompt.lower()
    
    @patch('agents.improved_news_agent.DuckDuckGoSearchRun')
    def test_cached_search(self, mock_search):
        """Test cached search functionality."""
        mock_search.return_value.run.return_value = "test result"
        
        agent = NewsAgent()
        result1 = agent.cached_search("test query")
        result2 = agent.cached_search("test query")
        
        assert result1 == result2
        assert mock_search.return_value.run.call_count == 1

class TestFundamentalAgent:
    """Test cases for FundamentalAgent."""
    
    def test_initialization(self):
        """Test agent initialization."""
        agent = FundamentalAgent()
        assert agent.name == "fundamental_agent"
        assert agent.model == "gpt-4o-mini"
    
    def test_get_tools(self):
        """Test tool retrieval."""
        agent = FundamentalAgent()
        tools = agent.get_tools()
        assert len(tools) >= 2  # Should have at least 2 tools
    
    def test_get_prompt(self):
        """Test prompt generation."""
        agent = FundamentalAgent()
        prompt = agent.get_prompt()
        assert "fundamental analysis" in prompt.lower()
        assert "financial health" in prompt.lower()

if __name__ == "__main__":
    pytest.main([__file__])