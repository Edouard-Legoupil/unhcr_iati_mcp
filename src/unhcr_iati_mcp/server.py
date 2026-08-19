"""
UNHCR IATI MCP Server

Main entry point for the MCP server that provides access to UNHCR's IATI data.
Supports both STDIO (default) and HTTP transport modes.
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastmcp import FastMCP

from unhcr_iati_mcp.config import settings
from unhcr_iati_mcp.context import mcp as base_mcp, iati_client
from unhcr_iati_mcp.observability.logging import configure_logging, get_logger
from unhcr_iati_mcp.observability.metrics import configure_metrics

logger = get_logger(__name__)

# Configure structured logging with settings
configure_logging(
    level=settings.log_level,
    log_dir=settings.log_dir,
    log_file=settings.log_file
)

# Configure metrics with settings
configure_metrics(
    metrics_dir=settings.metrics_dir,
    metrics_file=settings.metrics_file
)


@asynccontextmanager
async def lifespan(app: FastMCP) -> AsyncGenerator[None, None]:
    """
    Lifespan manager for the MCP server.
    
    Handles startup and shutdown operations including:
    - Initializing shared state
    - Cleaning up resources on shutdown
    
    Args:
        app: The FastMCP application instance
    """
    # Startup: Already initialized in context
    yield
    # Shutdown: Close the IATI client
    await iati_client.close()


# Create the MCP server with lifespan support
mcp = base_mcp
mcp.lifespan = lifespan

# Tool registration
from unhcr_iati_mcp import tools

# Register resources
from unhcr_iati_mcp import resources


def main():
    """Run the MCP server in the configured transport mode."""
    # Check transport mode
    transport = os.getenv("MCP_TRANSPORT", settings.mcp_transport)
    
    if transport.lower() == "http":
        logger.info("Starting in HTTP mode")
        _run_http_server()
    else:
        logger.info("Starting in STDIO mode")
        # For STDIO mode, still use the basic MCP server
        mcp.run()


def _run_http_server():
    """Run the HTTP server with Streamable HTTP transport for Copilot Studio."""
    import uvicorn
    from fastapi.middleware.cors import CORSMiddleware
    from starlette.middleware.cors import CORSMiddleware as StarletteCORSMiddleware
    
    logger.info(f"HTTP Server listening on {settings.host}:{settings.port}")
    logger.info(f"Resource URL: {settings.get_resource_url()}")
    logger.info(f"Transport: streamable-http (for Copilot Studio compatibility)")
    
    # Create FastMCP app with Streamable HTTP transport
    mcp_app = mcp.create_app()
    
    # Create HTTP app with Streamable HTTP transport
    http_app = mcp_app.http_app(
        transport="streamable-http",
        path="/mcp",
        stateless_http=True,
        json_response=True,
    )
    
    # Add CORS middleware for Copilot Studio
    http_app.add_middleware(
        StarletteCORSMiddleware,
        allow_origins=[
            "*",
            "https://copilotstudio.microsoft.com",
            "https://*.copilotstudio.microsoft.com",
            "https://copilot.microsoft.com",
            "https://*.copilot.microsoft.com",
            "https://m365.cloud.microsoft",
            "https://*.m365.cloud.microsoft",
            "http://localhost:*",
            "http://127.0.0.1:*",
        ],
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
        allow_headers=["*"],
        expose_headers=[
            "Mcp-Session-Id",
            "mcp-session-id",
            "Content-Type",
            "Content-Length"
        ],
        allow_credentials=True,
        max_age=86400,
    )
    
    # Configure SSL if certificates are provided
    ssl_config = {}
    if settings.ssl_certfile and settings.ssl_keyfile:
        ssl_config = {
            "ssl_keyfile": settings.ssl_keyfile,
            "ssl_certfile": settings.ssl_certfile,
        }
        if settings.ssl_ca_certs:
            ssl_config["ssl_ca_certs"] = settings.ssl_ca_certs
        if settings.ssl_cert_reqs:
            ssl_config["ssl_cert_reqs"] = settings.ssl_cert_reqs
        logger.info(f"HTTPS enabled with certificate: {settings.ssl_certfile}")
    else:
        logger.warning("HTTPS not configured - Copilot Studio requires HTTPS for production")
    
    uvicorn.run(
        http_app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        access_log=True,
        **ssl_config
    )


if __name__ == "__main__":
    main()
