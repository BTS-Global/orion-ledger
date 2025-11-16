"""
MCP Server Configuration
"""
import os
from typing import Dict, Any
from pydantic import BaseSettings


class MCPSettings(BaseSettings):
    """MCP Server Settings"""
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Security
    API_KEY_HEADER: str = "X-MCP-API-Key"
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB_MCP", "1"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    
    # LLM Configuration
    DEFAULT_MODEL: str = "claude-3-sonnet-20240229"
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Performance
    MAX_TOKENS_PER_REQUEST: int = 4000
    EMBEDDING_CACHE_TTL: int = 3600  # 1 hour
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "json"
    
    class Config:
        env_prefix = "MCP_"
        case_sensitive = False


# Supported LLM Models
SUPPORTED_MODELS: Dict[str, Dict[str, Any]] = {
    "claude-3-opus-20240229": {
        "provider": "anthropic",
        "best_for": ["complex_analysis", "audit"],
        "cost_per_1k_tokens": 0.015,
        "max_tokens": 200000,
    },
    "claude-3-sonnet-20240229": {
        "provider": "anthropic",
        "best_for": ["classification", "general"],
        "cost_per_1k_tokens": 0.003,
        "max_tokens": 200000,
    },
    "claude-3-haiku-20240307": {
        "provider": "anthropic",
        "best_for": ["fast_classification", "batch"],
        "cost_per_1k_tokens": 0.00025,
        "max_tokens": 200000,
    },
    "gpt-4-turbo-preview": {
        "provider": "openai",
        "best_for": ["reports", "visualization"],
        "cost_per_1k_tokens": 0.01,
        "max_tokens": 128000,
    },
    "gpt-3.5-turbo": {
        "provider": "openai",
        "best_for": ["fast_queries", "simple_classification"],
        "cost_per_1k_tokens": 0.0005,
        "max_tokens": 16385,
    },
}


def get_settings() -> MCPSettings:
    """Get MCP settings singleton"""
    return MCPSettings()


settings = get_settings()
