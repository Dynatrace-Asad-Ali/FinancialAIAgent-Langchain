"""Configuration management for the Financial AI Agent."""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

@dataclass
class APIConfig:
    """API configuration settings."""
    openai_api_key: str
    tavily_api_key: Optional[str] = None
    langchain_api_key: Optional[str] = None
    dynatrace_endpoint: Optional[str] = None
    dynatrace_token: Optional[str] = None

@dataclass
class AppConfig:
    """Application configuration settings."""
    timeout_seconds: int = 120
    recursion_limit: int = 100
    default_model: str = "gpt-4o-mini"
    service_name: str = "FinancialAIAgent"

def load_config() -> tuple[APIConfig, AppConfig]:
    """Load configuration from environment variables."""
    api_config = APIConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        tavily_api_key=os.getenv("TAVILY_API_KEY"),
        langchain_api_key=os.getenv("LANGCHAIN_API_KEY"),
        dynatrace_endpoint=os.getenv("DYNATRACE_EXPORTER_OTLP_ENDPOINT"),
        dynatrace_token=os.getenv("DYNATRACE_API_TOKEN")
    )
    
    app_config = AppConfig(
        timeout_seconds=int(os.getenv("TIMEOUT_SECONDS", "120")),
        recursion_limit=int(os.getenv("RECURSION_LIMIT", "100")),
        default_model=os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
    )
    
    return api_config, app_config

def validate_config(api_config: APIConfig) -> list[str]:
    """Validate required configuration."""
    errors = []
    
    if not api_config.openai_api_key:
        errors.append("OPENAI_API_KEY is required")
    
    return errors