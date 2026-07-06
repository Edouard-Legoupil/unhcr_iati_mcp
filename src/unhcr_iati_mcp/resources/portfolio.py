"""Portfolio reference data for UNHCR IATI MCP Server."""

from unhcr_iati_mcp.context import mcp


@mcp.resource("unhcr://portfolio")
async def portfolio():
    """Get UNHCR portfolio metadata."""
    return {
        "publisher": "XM-DAC-41121",
        "publisher_name": "UNHCR",
        "organisation": "United Nations High Commissioner for Refugees",
    }
