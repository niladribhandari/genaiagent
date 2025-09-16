"""
Configuration for the Web Search System.
"""

import os
from typing import Dict, Any

# Default configuration
DEFAULT_CONFIG = {
    "search": {
        "default_max_results": 10,
        "default_search_type": "web",
        "timeout_seconds": 30,
        "rate_limit_per_minute": 100,
        "cache_duration_minutes": 60
    },
    "agents": {
        "web_search": {
            "enabled": True,
            "max_concurrent_searches": 5
        },
        "content_analysis": {
            "enabled": True,
            "max_content_length": 10000
        },
        "fact_checking": {
            "enabled": True,
            "max_claims_per_check": 10
        },
        "summarization": {
            "enabled": True,
            "default_summary_length": "medium"
        },
        "trend_monitoring": {
            "enabled": True,
            "trend_history_days": 30
        }
    },
    "apis": {
        "serpapi": {
            "enabled": bool(os.getenv("SERPAPI_API_KEY")),
            "api_key": os.getenv("SERPAPI_API_KEY"),
            "rate_limit": 100
        },
        "bing": {
            "enabled": bool(os.getenv("BING_SEARCH_API_KEY")),
            "api_key": os.getenv("BING_SEARCH_API_KEY"),
            "rate_limit": 1000
        }
    },
    "logging": {
        "level": os.getenv("LOG_LEVEL", "INFO"),
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
}

def get_config() -> Dict[str, Any]:
    """Get the current configuration."""
    return DEFAULT_CONFIG.copy()

def update_config(updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update configuration with new values."""
    config = get_config()
    
    def deep_update(base_dict, update_dict):
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    deep_update(config, updates)
    return config
