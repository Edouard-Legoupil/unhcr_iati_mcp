"""
Portfolio reference data for UNHCR IATI MCP Server.
"""

from unhcr_iati_mcp.context import mcp


@mcp.resource("unhcr://portfolio")
async def portfolio():
    """
    Get UNHCR portfolio metadata.
    
    Returns:
        Dictionary containing UNHCR portfolio information
    """
    return {
        "publisher": "XM-DAC-41121",
        "publisher_name": "UNHCR",
        "organisation": "United Nations High Commissioner for Refugees",
        "source": "IATI Datastore",
        "api_base_url": "https://api.iatistandard.org/datastore",
        "mcp_server": "unhcr-iati-mcp",
        "description": "MCP server for accessing UNHCR's IATI data",
    }
