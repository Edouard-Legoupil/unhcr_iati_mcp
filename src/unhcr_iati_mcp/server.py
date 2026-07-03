"""
UNHCR IATI MCP Server

Main entry point for the MCP server that provides access to UNHCR's IATI data.
"""

from unhcr_iati_mcp.context import mcp, iati_client, unhcr_filter
from unhcr_iati_mcp.observability.logging import configure_logging

# Configure structured logging
configure_logging()

# Tool registration
from unhcr_iati_mcp import tools

# Register resources
from unhcr_iati_mcp import resources


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()