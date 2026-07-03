"""
UNHCR IATI MCP Server

Main entry point for the MCP server that provides access to UNHCR's IATI data.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastmcp import FastMCP

from unhcr_iati_mcp.context import mcp as base_mcp, iati_client
from unhcr_iati_mcp.observability.logging import configure_logging

# Configure structured logging
configure_logging()


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
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
