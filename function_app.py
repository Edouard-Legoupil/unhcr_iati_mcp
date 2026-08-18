"""
Azure Function App entry point for UNHCR IATI MCP Server.

This is the main entry point for the Azure Function App that runs the UNHCR IATI MCP server.
The Function App is configured to expose the MCP server via Streamable HTTP transport
at the /mcp endpoint (which becomes /api/mcp in Azure Functions v4).

Copilot Studio should be configured to connect to:
https://<function-app-name>.azurewebsites.net/api/mcp
"""

import os
import sys
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import the Azure Function App
from unhcr_iati_mcp.azure.host import app

# Set Azure-specific configuration
def configure_azure():
    """Configure Azure-specific settings."""
    # Set default environment to production for Azure
    if "AZURE_FUNCTIONS_ENVIRONMENT" in os.environ:
        os.environ["ENVIRONMENT"] = "production"
    
    # Configure logging for Azure
    os.environ["LOG_LEVEL"] = os.getenv("LOG_LEVEL", "INFO")
    os.environ["LOG_FORMAT"] = os.getenv("LOG_FORMAT", "json")
    
    # Ensure PYTHONPATH includes src directory for Azure deployment
    src_path = str(Path(__file__).parent / "src")
    current_pythonpath = os.environ.get("PYTHONPATH", "")
    if src_path not in current_pythonpath:
        os.environ["PYTHONPATH"] = f"{src_path}:{current_pythonpath}" if current_pythonpath else src_path


# Configure Azure settings
configure_azure()

# Export the Function App for Azure Functions
# Azure Functions will automatically load this 'app' symbol from the module
# The app contains the following HTTP endpoints:
# - /api/mcp - MCP server endpoint (Streamable HTTP transport)
# - /api/health - Health check endpoint
# - /api/info - Server information and tool listing
# - /api/oauth/token - OAuth token endpoint
# - /api/.well-known/oauth-authorization-server - OAuth metadata
# - /api/.well-known/jwks.json - JWKS endpoint

# For local testing with Azure Functions Core Tools
if __name__ == "__main__":
    # When running locally via 'func start', Azure Functions will handle the execution
    # This block is only for direct Python execution (not through func CLI)
    import uvicorn
    from unhcr_iati_mcp.azure.host import get_mcp_app
    
    mcp_app = get_mcp_app()
    http_app = mcp_app.http_app(
        transport="streamable-http",
        path="/mcp",
        stateless_http=True,
        json_response=True
    )
    
    print("Starting UNHCR IATI MCP Server for local testing...")
    print("MCP endpoint: http://localhost:8000/mcp")
    print("Health endpoint: http://localhost:8000/health")
    print("Info endpoint: http://localhost:8000/info")
    print("OAuth token endpoint: http://localhost:8000/oauth/token")
    
    uvicorn.run(http_app, host="0.0.0.0", port=8000)