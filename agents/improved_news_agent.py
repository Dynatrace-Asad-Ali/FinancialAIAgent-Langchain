"""Improved news agent with better error handling and caching."""
from typing import List
from langchain_core.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchRun
from agents.base_agent import BaseAgent
from core.exceptions import ToolExecutionError
from core.logging_config import setup_logging
import time
from functools import lru_cache

logger = setup_logging()

class NewsAgent(BaseAgent):
    """News agent for fetching latest news."""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        super().__init__(model, "news_agent")
        self._search_cache = {}
    
    def get_tools(self) -> List[BaseTool]:
        """Get news search tools."""
        return [DuckDuckGoSearchRun()]
    
    def get_prompt(self) -> str:
        """Get agent prompt."""
        return (
            "You are a news agent that helps users find the latest news.\n\n"
            "INSTRUCTIONS:\n"
            "- Focus on recent, relevant news articles\n"
            "- Provide concise summaries with key information\n"
            "- Include publication dates when available\n"
            "- Verify information from multiple sources when possible\n"
            "- If no recent news is found, clearly state this\n"
            "- Limit responses to 4 most relevant news items\n"
            "- Always cite sources with URLs when available\n"
        )
    
    @lru_cache(maxsize=100)
    def cached_search(self, query: str, max_age_hours: int = 1) -> str:
        """Cached search to avoid duplicate API calls."""
        cache_key = f"{query}_{int(time.time() // (max_age_hours * 3600))}"
        
        if cache_key in self._search_cache:
            logger.info(f"Using cached result for query: {query}")
            return self._search_cache[cache_key]
        
        try:
            search_tool = DuckDuckGoSearchRun()
            result = search_tool.run(query)
            self._search_cache[cache_key] = result
            return result
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {str(e)}")
            raise ToolExecutionError(f"News search failed: {str(e)}")