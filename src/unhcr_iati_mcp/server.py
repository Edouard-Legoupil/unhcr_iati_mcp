"""
UNHCR IATI MCP Server

Main entry point for the MCP server that provides access to UNHCR's IATI data.
Supports both STDIO (default) and HTTP transport modes.
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastmcp import FastMCP, Context
from fastmcp.tools import Tool
from pydantic import BaseModel, Field

from .config import settings
from .context import mcp as base_mcp, iati_client
from .observability.logging import configure_logging, get_logger
from .observability.metrics import configure_metrics

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


class UNHCRServer:
    """UNHCR Refugee Data Portal MCP Server."""
    
    def __init__(self):
        """Initialize the server."""
        self.client: Optional[UNHCRClient] = None
        self.app: Optional[FastMCP] = None
    
    @asynccontextmanager
    async def lifespan(self, app: FastMCP):
        """Application lifespan manager."""
        # Startup
        logger.info("Starting UNHCR MCP Server")
        self.client = UNHCRClient()
        yield
        # Shutdown
        logger.info("Shutting down UNHCR MCP Server")
        if self.client:
            await self.client.close()
    
    def create_app(self) -> FastMCP:
        """Create and configure the FastMCP application."""
        if self.app is not None:
            return self.app
        
        # Create FastMCP app
        self.app = FastMCP(
            name=settings.MCP_SERVER_NAME,
            version=settings.MCP_SERVER_VERSION,
            lifespan=self.lifespan,
        )
        
        # Register tools
        self._register_tools()
        self._register_resources()
        
        def _register_tools(self) -> None:
            """Register all MCP tools."""
            if self.app is None:
                return
            self.app.add_tool(self.tools)
        
        def _register_resources(self) -> None:
            """Register all MCP resources."""
            if self.app is None:
                return
            self.app.add_tool(self.resources)
        
        return self.app

# Global server instance
_server: Optional[UNHCRServer] = None


def get_server() -> UNHCRServer:
    """Get or create global server instance."""
    global _server
    if _server is None:
        _server = UNHCRServer()
    return _server


# Create the FastMCP app
app = get_server().create_app()