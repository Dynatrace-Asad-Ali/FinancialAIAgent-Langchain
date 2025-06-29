"""Custom exceptions for the Financial AI Agent."""

class FinancialAgentError(Exception):
    """Base exception for Financial AI Agent."""
    pass

class ConfigurationError(FinancialAgentError):
    """Raised when configuration is invalid."""
    pass

class AgentInitializationError(FinancialAgentError):
    """Raised when agent initialization fails."""
    pass

class ToolExecutionError(FinancialAgentError):
    """Raised when tool execution fails."""
    pass

class TimeoutError(FinancialAgentError):
    """Raised when operations timeout."""
    pass