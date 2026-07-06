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
        mcp.run()


def _run_http_server():
    """Run the HTTP server."""
    import uvicorn
    from unhcr_iati_mcp.server_http import app
    
    logger.info(f"HTTP Server listening on {settings.host}:{settings.port}")
    logger.info(f"Resource URL: {settings.resource_url or f'http://{settings.host}:{settings.port}'}")
    logger.info(f"OAuth: {'enabled' if settings.use_builtin_oauth else 'disabled'}")
    
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        access_log=True,
    )


if __name__ == "__main__":
    main()
