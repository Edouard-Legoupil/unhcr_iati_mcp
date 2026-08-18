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

    # Metrics
    metrics_dir: str = Field(default_factory=lambda: os.getenv("METRICS_DIR", "metrics"))
    metrics_file: Optional[str] = Field(default_factory=lambda: os.getenv("METRICS_FILE"))

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


settings = Settings()