"""
Configuration management for UNHCR MCP Server.

Uses Pydantic Settings for environment-based configuration
with sensible defaults for development and production.
"""

from functools import lru_cache
from typing import Optional

import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings for UNHCR IATI MCP Server."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # IATI Datastore Configuration
    IATI_BASE_URL="https://api.iatistandard.org/datastore"
    UNHCR_PUBLISHER_REF="XM-DAC-41121"

    API_TIMEOUT: int = 30
    API_MAX_RETRIES: int = 3
    
    # MCP Server Configuration
    MCP_SERVER_NAME: str = "unhcr-refugee-data"
    MCP_SERVER_VERSION: str = "1.0.0"
    MCP_SERVER_HOST: str = "0.0.0.0"
    MCP_SERVER_PORT: int = 8000
    MCP_SERVER_DEBUG: bool = False
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # Caching
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 300  # seconds
    CACHE_MAX_SIZE: int = 1000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # or "text"
    
    # Security
    API_KEY: Optional[str] = None
    REQUIRE_API_KEY: bool = False
    
    # Pagination defaults
    DEFAULT_PAGE: int = 1
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # HTTP Client Configuration
    HTTP_POOL_SIZE: int = 10
    HTTP_MAX_CONNECTIONS: int = 100
    HTTP_KEEP_ALIVE: bool = True
    
    # Environment
    ENVIRONMENT: str = "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT.lower() == "development"
    
    def get_api_base_url(self) -> str:
        """Get the base API URL for the IATI Datastore."""
        return self.iati_base_url.rstrip("/")


# Global settings instance cache
_settings_cache: Optional[Settings] = None


def get_settings() -> Settings:
    """Get cached settings instance."""
    global _settings_cache
    if _settings_cache is None:
        _settings_cache = Settings()
    return _settings_cache


# Global settings instance - this is the cached instance
settings = get_settings()
