"""
Azure Function App entry point for UNHCR IATI MCP Server.

This is the main entry point for the Azure Function App that runs the UNHCR IATI MCP server.
The Function App is configured to expose the MCP server via Streamable HTTP transport
at the /mcp endpoint (which becomes /api/mcp in Azure Functions v4).

Copilot Studio should be configured to connect to:
https://<function-app-name>.azurewebsites.net/api/mcp

IMPORTANT: Azure Functions v4 Python's custom loader ONLY scans function_app.py
for @app.function_name decorators. All function decorators MUST be in this file.
"""

import os
import sys
import json
import logging
import asyncio
from pathlib import Path

import azure.functions as func
from starlette.middleware.cors import CORSMiddleware

# Add src directory to path for imports - MUST BE FIRST
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Set Azure-specific configuration BEFORE importing anything else
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


# Configure Azure settings FIRST
configure_azure()

# Import required modules from src
from unhcr_iati_mcp.config import settings
from unhcr_iati_mcp.client import IATIClient as UNHCRClient
from unhcr_iati_mcp.server import mcp as get_server
from unhcr_iati_mcp.context import mcp as mcp_context

logger = logging.getLogger(__name__)

# Global server and ASGI middleware instances
_server = None
_http_app = None
_asgi_middleware = None
_startup_lock = asyncio.Lock()
_startup_done = False


def get_mcp_app():
    """Get or create the FastMCP server instance."""
    global _server
    if _server is None:
        _server = get_server()
    return _server.create_app()


def get_asgi_middleware():
    """Get or create the AsgiMiddleware instance for FastMCP."""
    global _http_app, _asgi_middleware
    if _asgi_middleware is None:
        mcp_app = get_mcp_app()
        # FastMCP Starlette app route path must match the Azure Functions route prefix (/api/mcp)
        base_app = mcp_app.http_app(
            transport="streamable-http",
            path="/api/mcp",
            stateless_http=True,
            json_response=True,
        )
        # Add CORSMiddleware so Copilot Studio browser preflights succeed and Mcp-Session-Id is exposed
        _http_app = CORSMiddleware(
            base_app,
            allow_origins=[
                # Microsoft Copilot Studio and related domains
                "https://copilotstudio.microsoft.com",
                "https://*.copilotstudio.microsoft.com",
                "https://copilot.microsoft.com",
                "https://*.copilot.microsoft.com",
                "https://m365.cloud.microsoft",
                "https://*.m365.cloud.microsoft",
                # Claude AI domains
                "https://claude.ai",
                "https://*.claude.ai",
                # Local development
                "http://localhost:*",
                "http://127.0.0.1:*",
            ],
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
            allow_headers=["*"],
            expose_headers=["Mcp-Session-Id", "mcp-session-id", "Content-Type", "Content-Length"],
            allow_credentials=True,
            max_age=86400,
        )
        _asgi_middleware = func.AsgiMiddleware(_http_app)
    return _asgi_middleware


async def ensure_asgi_startup():
    """Ensure FastMCP ASGI lifespan startup has executed on the current event loop."""
    global _startup_done
    if not _startup_done:
        async with _startup_lock:
            if not _startup_done:
                middleware = get_asgi_middleware()
                logger.info("Initializing FastMCP ASGI lifespan startup...")
                await middleware.notify_startup()
                _startup_done = True


# ============================================================================
# CRITICAL: Create the FunctionApp HERE in function_app.py
# Azure Functions v4 Python ONLY scans function_app.py for @app.function_name
# ============================================================================
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Azure Functions can inspect the app more than once during registration and startup.
# The runtime mutates `functions_bindings` in-place, so a second discovery pass raises
# a duplicate-name ValueError and prevents the function list from appearing in the portal.
_original_validate_function_names = app.validate_function_names


def _validate_function_names_idempotent(functions):
    """Reset the function registry before each discovery pass so Azure can scan the app repeatedly."""
    app.functions_bindings = {}
    return _original_validate_function_names(functions)


app.validate_function_names = _validate_function_names_idempotent


# ============================================================================
# IMPORTANT: All @app.function_name decorators MUST be in function_app.py
# We import the handlers from host.py and register them here
# ============================================================================

# Import all handler functions from host module
from unhcr_iati_mcp.azure.host import (
    mcp_handler,
    health_handler,
    info_handler,
    openapi_handler,
    mcp_schema_handler,
    mcp_protocol_handler,
    well_known_openapi_handler,
)

# Register all functions with the FunctionApp created in THIS module
@app.function_name(name="mcp")
@app.route(route="mcp/{*path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"])
async def mcp(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Main MCP HTTP handler for Streamable HTTP transport."""
    return await mcp_handler(req, context)


@app.function_name(name="health")
@app.route(route="health", methods=["GET"])
async def health(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Health check endpoint."""
    return await health_handler(req, context)


@app.function_name(name="info")
@app.route(route="info", methods=["GET"])
async def info(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Server information endpoint."""
    return await info_handler(req, context)


@app.function_name(name="openapi")
@app.route(route="openapi.json", methods=["GET"])
async def openapi(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """OpenAPI schema endpoint for Copilot Studio discovery."""
    return await openapi_handler(req, context)


@app.function_name(name="mcp_schema")
@app.route(route=".well-known/mcp/schema", methods=["GET"])
async def mcp_schema(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """MCP Schema Discovery Endpoint for Copilot Studio."""
    return await mcp_schema_handler(req, context)


@app.function_name(name="mcp_protocol")
@app.route(route=".well-known/mcp", methods=["GET"])
async def mcp_protocol(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """MCP Protocol Schema Endpoint."""
    return await mcp_protocol_handler(req, context)


@app.function_name(name="well_known_openapi")
@app.route(route=".well-known/openapi.json", methods=["GET"])
async def well_known_openapi(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Well-known OpenAPI Schema Endpoint."""
    return await well_known_openapi_handler(req, context)


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
    
    uvicorn.run(http_app, host="0.0.0.0", port=8000)
