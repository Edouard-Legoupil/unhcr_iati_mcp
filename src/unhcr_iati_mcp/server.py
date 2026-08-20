"""
UNHCR IATI MCP Server

Main entry point for the MCP server that provides access to UNHCR's IATI data.
Supports both STDIO (default) and HTTP transport modes.
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from fastmcp import FastMCP, Context
from fastmcp.tools import Tool
from pydantic import BaseModel, Field

# Import config first
from unhcr_iati_mcp.config import settings

# Import context next - this creates the base_mcp instance
from unhcr_iati_mcp.context import mcp as base_mcp, iati_client

# Import observability
from unhcr_iati_mcp.observability.logging import configure_logging, get_logger
from unhcr_iati_mcp.client import IATIClient

logger = get_logger(__name__)

# Configure structured logging with settings
configure_logging(
    level=settings.log_level,
    log_dir=settings.log_dir,
    log_file=settings.log_file
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

# Now import tools - context is already imported, so tools will use the same mcp instance
# Import individual tool modules to trigger registration
from unhcr_iati_mcp.tools import activities
from unhcr_iati_mcp.tools import transactions
from unhcr_iati_mcp.tools import budgets
from unhcr_iati_mcp.tools import donors
from unhcr_iati_mcp.tools import sectors
from unhcr_iati_mcp.tools import countries
from unhcr_iati_mcp.tools import analytics
from unhcr_iati_mcp.tools import export
from unhcr_iati_mcp.tools import health
from unhcr_iati_mcp.tools import code_resolution

# Import resources
from unhcr_iati_mcp.resources import countries as res_countries
from unhcr_iati_mcp.resources import sectors as res_sectors
from unhcr_iati_mcp.resources import results
from unhcr_iati_mcp.resources import sdgs
from unhcr_iati_mcp.resources import donors as res_donors
from unhcr_iati_mcp.resources import glossary
from unhcr_iati_mcp.resources import portfolio
from unhcr_iati_mcp.resources import schemas
from unhcr_iati_mcp.resources import code_tables


class UNHCRServer:
    """UNHCR Refugee Data Portal MCP Server."""
    
    def __init__(self):
        """Initialize the server."""
        self.client: Optional[IATIClient] = None
        self.app: Optional[FastMCP] = None
    
    @asynccontextmanager
    async def lifespan(self, app: FastMCP):
        """Application lifespan manager."""
        # Startup
        logger.info("Starting UNHCR MCP Server")
        self.client = IATIClient()
        yield
        # Shutdown
        logger.info("Shutting down UNHCR MCP Server")
        if self.client:
            await self.client.close()
    
    def create_app(self) -> FastMCP:
        """Create and configure the FastMCP application."""
        if self.app is not None:
            return self.app
        
        # Use the base_mcp instance which already has tools and resources registered
        self.app = mcp
        
        return self.app


# Global server instance
_server: Optional[UNHCRServer] = None


def get_server() -> UNHCRServer:
    """Get or create global server instance."""
    global _server
    if _server is None:
        _server = UNHCRServer()
    return _server


# Create the FastMCP app - this is the main app instance that gets imported
app = get_server().create_app()
