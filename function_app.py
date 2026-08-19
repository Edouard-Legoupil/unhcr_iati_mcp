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

# Setup basic logging BEFORE any other imports
# This is critical for debugging Azure deployment issues
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.info(f"function_app.py starting - file: {__file__}")
logger.info(f"Initial sys.path: {sys.path}")
logger.info(f"Initial PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
logger.info(f"Azure Functions Environment: {os.environ.get('AZURE_FUNCTIONS_ENVIRONMENT', 'Not set')}")

# Add src directory to path for imports - MUST BE FIRST
# This is critical for Azure deployment where src might not be in the path
project_root = Path(__file__).parent
src_path = project_root / "src"

logger.info(f"Project root: {project_root}")
logger.info(f"Src path: {src_path}")
logger.info(f"Src path exists: {src_path.exists()}")

# Add both project root and src to path
for path in [str(project_root), str(src_path)]:
    if path not in sys.path:
        sys.path.insert(0, path)
        logger.info(f"Added to sys.path: {path}")

# Also set PYTHONPATH environment variable for subprocesses
current_pythonpath = os.environ.get("PYTHONPATH", "")
pythonpath_parts = [p for p in current_pythonpath.split(":") if p]
for path in [str(project_root), str(src_path)]:
    if path not in pythonpath_parts:
        pythonpath_parts.insert(0, path)
os.environ["PYTHONPATH"] = ":".join(pythonpath_parts)
logger.info(f"Updated PYTHONPATH: {os.environ.get('PYTHONPATH')}")

import azure.functions as func
from starlette.middleware.cors import CORSMiddleware

logger.info("Azure functions and starlette imported successfully")

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
# Add detailed error handling for Azure deployment debugging
try:
    logger.info("Attempting to import unhcr_iati_mcp modules...")
    from unhcr_iati_mcp.config import settings
    logger.info("Successfully imported config")
    from unhcr_iati_mcp.client import IATIClient as UNHCRClient
    logger.info("Successfully imported client")
    from unhcr_iati_mcp.context import mcp as mcp_server
    logger.info("Successfully imported context - all imports successful")
except ImportError as e:
    logger.error(f"Import error in function_app.py: {e}")
    logger.error(f"sys.path: {sys.path}")
    logger.error(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    # Try to import with explicit path
    src_path_str = str(src_path)
    if src_path_str not in sys.path:
        sys.path.insert(0, src_path_str)
        logger.info(f"Added src_path to sys.path: {src_path_str}")
    try:
        logger.info("Second import attempt...")
        from unhcr_iati_mcp.config import settings
        from unhcr_iati_mcp.client import IATIClient as UNHCRClient
        from unhcr_iati_mcp.context import mcp as mcp_server
        logger.info("Imports successful after path adjustment")
    except ImportError as e2:
        logger.error(f"Second import attempt failed: {e2}")
        # Last resort: try relative import
        try:
            logger.info("Third import attempt with relative path...")
            from src.unhcr_iati_mcp.config import settings
            from src.unhcr_iati_mcp.client import IATIClient as UNHCRClient
            from src.unhcr_iati_mcp.context import mcp as mcp_server
            logger.info("Imports successful with relative path")
        except ImportError as e3:
            logger.error(f"All import attempts failed: {e3}")
            # List all files in src to debug
            if src_path.exists():
                logger.error(f"Files in src: {list(src_path.rglob('*.py'))[:10]}")
            raise

logger = logging.getLogger(__name__)

# Global server and ASGI middleware instances
_http_app = None
_asgi_middleware = None
_startup_lock = asyncio.Lock()
_startup_done = False


def get_mcp_app():
    """Get the FastMCP server instance and return its HTTP app."""
    # mcp_server is the FastMCP instance from context
    # FastMCP uses http_app() method to create a Starlette app
    return mcp_server.http_app(
        transport="streamable-http",
        path="/api/mcp",
        stateless_http=True,
        json_response=True,
    )


def get_asgi_middleware():
    """Get or create the AsgiMiddleware instance for FastMCP."""
    global _http_app, _asgi_middleware
    if _asgi_middleware is None:
        # get_mcp_app() returns the Starlette app directly
        base_app = get_mcp_app()
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
logger.info("Creating FunctionApp...")
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
logger.info("FunctionApp created successfully")


# ============================================================================
# IMPORTANT: All @app.function_name decorators MUST be in function_app.py
# We import the handlers from host.py and register them here
# ============================================================================

# Import all handler functions from host module
logger.info("Importing handlers from host module...")
try:
    from unhcr_iati_mcp.azure.host import (
        mcp_handler,
        health_handler,
        info_handler,
        openapi_handler,
        mcp_schema_handler,
        mcp_protocol_handler,
        well_known_openapi_handler,
    )
    logger.info("Successfully imported all handlers from host module")
except ImportError as e:
    logger.error(f"Failed to import handlers from host module: {e}")
    # Try to import directly
    try:
        from src.unhcr_iati_mcp.azure.host import (
            mcp_handler,
            health_handler,
            info_handler,
            openapi_handler,
            mcp_schema_handler,
            mcp_protocol_handler,
            well_known_openapi_handler,
        )
        logger.info("Successfully imported handlers with relative path")
    except ImportError as e2:
        logger.error(f"All attempts to import handlers failed: {e2}")
        raise

# Register all functions with the FunctionApp created in THIS module
logger.info("Registering function: mcp")
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

logger.info("Registered function: health")

@app.function_name(name="info")
@app.route(route="info", methods=["GET"])
async def info(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Server information endpoint."""
    return await info_handler(req, context)

logger.info("Registered function: info")

@app.function_name(name="openapi")
@app.route(route="openapi.json", methods=["GET"])
async def openapi(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """OpenAPI schema endpoint for Copilot Studio discovery."""
    return await openapi_handler(req, context)

logger.info("Registered function: openapi")

@app.function_name(name="mcp_schema")
@app.route(route=".well-known/mcp/schema", methods=["GET"])
async def mcp_schema(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """MCP Schema Discovery Endpoint for Copilot Studio."""
    return await mcp_schema_handler(req, context)

logger.info("Registered function: mcp_schema")

@app.function_name(name="mcp_protocol")
@app.route(route=".well-known/mcp", methods=["GET"])
async def mcp_protocol(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """MCP Protocol Schema Endpoint."""
    return await mcp_protocol_handler(req, context)

logger.info("Registered function: mcp_protocol")

@app.function_name(name="well_known_openapi")
@app.route(route=".well-known/openapi.json", methods=["GET"])
async def well_known_openapi(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Well-known OpenAPI Schema Endpoint."""
    return await well_known_openapi_handler(req, context)

logger.info("Registered function: well_known_openapi")
logger.info("All functions registered successfully!")


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
