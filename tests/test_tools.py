"""Unit tests for tools."""
import pytest
from unittest.mock import Mock, patch
from tools.enhanced_fundamental_tool import enhanced_fundamental_analysis
from core.exceptions import ToolExecutionError

class TestEnhancedFundamentalTool:
    """Test cases for enhanced fundamental analysis tool."""
    
    @patch('tools.enhanced_fundamental_tool.yf.Ticker')
    def test_successful_analysis(self, mock_ticker):
        """Test successful fundamental analysis."""
        # Mock yfinance data
        mock_ticker.return_value.info = {
            "longName": "Test Company",
            "sector": "Technology",
            "marketCap": 1000000000,
            "trailingPE": 25.0,
            "profitMargins": 0.15
        }
        mock_ticker.return_value.financials = Mock()
        mock_ticker.return_value.balance_sheet = Mock()
        mock_ticker.return_value.cashflow = Mock()
        
        result = enhanced_fundamental_analysis("TEST")
        
        assert "FUNDAMENTAL ANALYSIS REPORT" in result
        assert "Test Company" in result
        assert "Technology" in result
    
    @patch('tools.enhanced_fundamental_tool.yf.Ticker')
    def test_analysis_failure(self, mock_ticker):
        """Test analysis failure handling."""
        mock_ticker.side_effect = Exception("API Error")
        
        with pytest.raises(ToolExecutionError):
            enhanced_fundamental_analysis("INVALID")

if __name__ == "__main__":
    pytest.main([__file__])