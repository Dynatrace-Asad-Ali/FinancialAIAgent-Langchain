"""Configuration management for MCP application."""
import json
import os
from typing import Dict, Any, List
import streamlit as st

class ConfigManager:
    """Manages MCP server configuration."""
    
    CONFIG_FILE = "config.json"
    
    def __init__(self):
        self.default_config = {
            "math": {
                "url": "http://localhost:8000/mcp",
                "transport": "streamable_http",
            },
            "weather": {
                "url": "http://localhost:8080/mcp",
                "transport": "streamable_http",
            },
            "dynatrace": {
                "url": "http://52.186.168.229:3000/mcp",
                "transport": "streamable_http",
            }
        }
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    return self._validate_and_fix_config(config)
            else:
                self.save_config(self.default_config)
                return self.default_config
        except Exception as e:
            st.error(f"Error loading config: {str(e)}")
            return self.default_config
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to JSON file."""
        try:
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            st.error(f"Error saving config: {str(e)}")
            return False
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate MCP configuration."""
        if not isinstance(config, dict):
            return False
        
        for server_name, server_config in config.items():
            if not isinstance(server_config, dict):
                return False
            
            required_fields = ["url", "transport"]
            for field in required_fields:
                if field not in server_config:
                    return False
        
        return True
    
    def _validate_and_fix_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and fix configuration issues."""
        fixed_config = {}
        
        for server_name, server_config in config.items():
            if isinstance(server_config, dict) and "url" in server_config:
                fixed_config[server_name] = {
                    "url": server_config["url"],
                    "transport": server_config.get("transport", "streamable_http")
                }
        
        # Add missing default servers
        for server_name, server_config in self.default_config.items():
            if server_name not in fixed_config:
                fixed_config[server_name] = server_config
        
        return fixed_config
    
    def get_server_list(self, config: Dict[str, Any]) -> List[str]:
        """Get list of configured servers."""
        return list(config.keys())