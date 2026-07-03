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
    mcp_transport: str = "stdio"  # "stdio" or "http"
    host: str = "0.0.0.0"
    port: int = 8000
    resource_url: str | None = None  # e.g., "http://localhost:8000"
    
    # Authentication Configuration
    use_builtin_oauth: bool = False
    auth_server_url: str | None = None
    oauth_client_id: str = "default"
    oauth_token_expiry: int = 3600  # seconds
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"


settings = Settings()