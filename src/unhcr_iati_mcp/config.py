from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings for UNHCR IATI MCP Server."""
    
    # IATI Datastore Configuration
    iati_api_key: str
    iati_base_url: str = "https://api.iatistandard.org/datastore"
    unhcr_publisher_ref: str = "XM-DAC-41121"
    
    # Client Configuration
    timeout_seconds: int = 120
    page_size: int = 1000
    
    # Server Configuration
    mcp_transport: str = "http"  # "stdio" or "http" - Changed to http for Copilot Studio
    host: str = "0.0.0.0"
    port: int = 8000
    resource_url: str | None = None  # e.g., "http://localhost:8000"
    
    # Azure Configuration
    azure_function_app: bool = False
    website_hostname: str | None = None  # Azure Function App hostname
    
    # SSL/TLS Configuration for Copilot Studio HTTPS requirement
    ssl_certfile: Optional[str] = None  # Path to SSL certificate file
    ssl_keyfile: Optional[str] = None   # Path to SSL private key file
    ssl_ca_certs: Optional[str] = None  # Path to CA bundle for certificate verification
    ssl_cert_reqs: int = 2  # 0 = CERT_NONE, 1 = CERT_OPTIONAL, 2 = CERT_REQUIRED
    
    # Authentication Configuration
    use_builtin_oauth: bool = True  # Enabled by default for Copilot Studio
    auth_server_url: str | None = None
    oauth_client_id: str = "default"
    oauth_token_expiry: int = 3600  # seconds
    
    # Environment
    environment: str = "production"
    mcp_server_name: str = "unhcr-iati-mcp"
    mcp_server_version: str = "0.0.1"
    unhcr_api_version: str = "1.0"
    
    # Logging
    log_level: str = "INFO"
    log_dir: str = "logs"
    log_file: Optional[str] = None
    
    # Metrics
    metrics_dir: str = "metrics"
    metrics_file: Optional[str] = None
    
    class Config:
        env_file = ".env"
    
    def get_api_base_url(self) -> str:
        """Get the base API URL for the IATI Datastore."""
        return self.iati_base_url.rstrip("/")
    
    def get_resource_url(self) -> str:
        """Get the resource URL for the MCP server."""
        if self.resource_url:
            return self.resource_url.rstrip("/")
        if self.azure_function_app and self.website_hostname:
            return f"https://{self.website_hostname}"
        return f"http://{self.host}:{self.port}"


settings = Settings()