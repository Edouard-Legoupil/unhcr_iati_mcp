"""
Context module for UNHCR IATI MCP Server.

This module holds shared state to avoid circular imports between server.py and tool files.
It provides the FastMCP instance, IATI client, and UNHCR filter function that are used
across the entire application.
"""

from fastmcp import FastMCP

from unhcr_iati_mcp.client import IATIClient
from unhcr_iati_mcp.config import settings

# Initialize shared state
mcp = FastMCP(
    name="unhcr-iati-mcp",
    instructions="IATI Datastore for UNHCR - Access UNHCR's humanitarian aid data from IATI"
)

# Create the IATI client instance
iati_client = IATIClient()


def unhcr_filter() -> str:
    """
    Generate the UNHCR publisher filter string for IATI Datastore queries.
    
    Returns:
        str: Solr query filter string for UNHCR data
    """
    return f'reporting_org_ref:"{settings.unhcr_publisher_ref}"'
