"""
Configuration management for UNHCR MCP Server.

Uses Pydantic Settings for environment-based configuration
with sensible defaults for development and production.
"""

import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _env_flag(name: str, default: bool = False) -> bool:
    """Parse boolean-like Azure/app settings robustly."""
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class Settings(BaseSettings):
    """Application settings for UNHCR IATI MCP Server."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    # IATI Datastore Configuration
    iati_api_key: str = ""
    iati_base_url: str = "https://api.iatistandard.org/datastore"
    unhcr_publisher_ref: str = "XM-DAC-41121"

    # Client Configuration
    timeout_seconds: int = 120
    page_size: int = 1000

    # Server Configuration
    mcp_transport: str = Field(default_factory=lambda: os.getenv("MCP_TRANSPORT", "http"))
    host: str = Field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = Field(default_factory=lambda: int(os.getenv("PORT", "8000")))
    resource_url: str | None = Field(default_factory=lambda: os.getenv("RESOURCE_URL"))

    # Azure Configuration
    azure_function_app: bool = Field(default_factory=lambda: _env_flag("AZURE_FUNCTION_APP", False))
    website_hostname: str | None = Field(default_factory=lambda: os.getenv("WEBSITE_HOSTNAME"))

    # SSL/TLS Configuration for Copilot Studio HTTPS requirement
    ssl_certfile: Optional[str] = None
    ssl_keyfile: Optional[str] = None
    ssl_ca_certs: Optional[str] = None
    ssl_cert_reqs: int = 2

    # Authentication Configuration
    use_builtin_oauth: bool = Field(default_factory=lambda: _env_flag("USE_BUILTIN_OAUTH", True))
    auth_server_url: str | None = Field(default_factory=lambda: os.getenv("AUTH_SERVER_URL"))
    oauth_client_id: str = Field(default_factory=lambda: os.getenv("OAUTH_CLIENT_ID", "default"))
    oauth_token_expiry: int = Field(default_factory=lambda: int(os.getenv("OAUTH_TOKEN_EXPIRY", "3600")))

    # Environment
    environment: str = Field(default_factory=lambda: os.getenv("ENVIRONMENT", "production"))
    mcp_server_name: str = Field(default_factory=lambda: os.getenv("MCP_SERVER_NAME", "unhcr-iati-mcp"))
    mcp_server_version: str = Field(default_factory=lambda: os.getenv("MCP_SERVER_VERSION", "0.0.1"))
    unhcr_api_version: str = Field(default_factory=lambda: os.getenv("UNHCR_API_VERSION", "1.0"))

    # Logging
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    log_dir: str = Field(default_factory=lambda: os.getenv("LOG_DIR", "logs"))
    log_file: Optional[str] = Field(default_factory=lambda: os.getenv("LOG_FILE"))
    log_format: str = Field(default_factory=lambda: os.getenv("LOG_FORMAT", "json"))

    # Metrics
    metrics_dir: str = Field(default_factory=lambda: os.getenv("METRICS_DIR", "metrics"))
    metrics_file: Optional[str] = Field(default_factory=lambda: os.getenv("METRICS_FILE"))

    # Rate Limiting
    rate_limit_requests: int = Field(default_factory=lambda: int(os.getenv("RATE_LIMIT_REQUESTS", "100")))
    rate_limit_period: int = Field(default_factory=lambda: int(os.getenv("RATE_LIMIT_PERIOD", "60")))

    # Pagination defaults
    default_page: int = 1
    default_page_size: int = 20
    max_page_size: int = 100

    # HTTP Client Configuration
    http_pool_size: int = 10
    http_max_connections: int = 100
    http_keep_alive: bool = True

    # Caching
    cache_enabled: bool = True
    cache_ttl: int = 300  # seconds
    cache_max_size: int = 1000

    # Security
    require_api_key: bool = False

    def get_api_base_url(self) -> str:
        """Get the base API URL for the IATI Datastore."""
        return self.iati_base_url.rstrip("/")

    def get_resource_url(self) -> str:
        """Get the resource URL for the MCP server."""
        if self.resource_url:
            return self.resource_url.rstrip("/")
        if self.azure_function_app and self.website_hostname:
            return f"https://{self.website_hostname}"
        if self.environment.lower() == "production" and self.website_hostname:
            return f"https://{self.website_hostname}"
        return f"http://{self.host}:{self.port}"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"

    # Backward compatibility properties for uppercase access
    @property
    def ENVIRONMENT(self) -> str:
        """Backward compatibility: uppercase access to environment."""
        return self.environment

    @property
    def LOG_LEVEL(self) -> str:
        """Backward compatibility: uppercase access to log_level."""
        return self.log_level

    @property
    def LOG_FORMAT(self) -> str:
        """Backward compatibility: uppercase access to log_format."""
        return self.log_format

    @property
    def MCP_SERVER_NAME(self) -> str:
        """Backward compatibility: uppercase access to mcp_server_name."""
        return self.mcp_server_name

    @property
    def MCP_SERVER_VERSION(self) -> str:
        """Backward compatibility: uppercase access to mcp_server_version."""
        return self.mcp_server_version

    @property
    def MCP_SERVER_HOST(self) -> str:
        """Backward compatibility: uppercase access to host."""
        return self.host

    @property
    def MCP_SERVER_PORT(self) -> int:
        """Backward compatibility: uppercase access to port."""
        return self.port

    @property
    def MCP_SERVER_DEBUG(self) -> bool:
        """Backward compatibility: uppercase access to azure_function_app (debug mode)."""
        return self.azure_function_app

    @property
    def RATE_LIMIT_REQUESTS(self) -> int:
        """Backward compatibility: uppercase access to rate_limit_requests."""
        return self.rate_limit_requests

    @property
    def RATE_LIMIT_PERIOD(self) -> int:
        """Backward compatibility: uppercase access to rate_limit_period."""
        return self.rate_limit_period

    @property
    def UNHCR_API_VERSION(self) -> str:
        """Backward compatibility: uppercase access to unhcr_api_version."""
        return self.unhcr_api_version


# Global settings instance
settings = Settings()
