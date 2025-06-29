"""Improved fundamental analysis agent."""
from typing import List
from langchain_core.tools import BaseTool
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from agents.base_agent import BaseAgent
from tools.enhanced_fundamental_tool import EnhancedFundamentalTool

class FundamentalAgent(BaseAgent):
    """Agent for fundamental analysis."""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        super().__init__(model, "fundamental_agent")
    
    def get_tools(self) -> List[BaseTool]:
        """Get fundamental analysis tools."""
        return [
            YahooFinanceNewsTool(),
            EnhancedFundamentalTool()
        ]
    
    def get_prompt(self) -> str:
        """Get agent prompt."""
        return (
            "You are a fundamental analysis expert specializing in comprehensive stock evaluation.\n\n"
            "ANALYSIS FRAMEWORK:\n"
            "1. Financial Health Assessment:\n"
            "   - Revenue growth trends (3-5 years)\n"
            "   - Profitability metrics (margins, ROE, ROA)\n"
            "   - Balance sheet strength (debt ratios, liquidity)\n"
            "   - Cash flow analysis (operating, free cash flow)\n\n"
            "2. Valuation Analysis:\n"
            "   - P/E, P/B, P/S ratios vs industry/market\n"
            "   - PEG ratio for growth consideration\n"
            "   - DCF model with clear assumptions\n"
            "   - Comparable company analysis\n\n"
            "3. Competitive Position:\n"
            "   - Market share and competitive advantages\n"
            "   - Industry dynamics and trends\n"
            "   - Management quality and strategy\n\n"
            "4. Risk Assessment:\n"
            "   - Business risks and challenges\n"
            "   - Regulatory and market risks\n"
            "   - Financial risks\n\n"
            "INSTRUCTIONS:\n"
            "- Provide data-driven analysis with specific numbers\n"
            "- Compare metrics to industry averages\n"
            "- Highlight both strengths and weaknesses\n"
            "- Include forward-looking insights\n"
            "- Conclude with investment thesis summary\n"
        )