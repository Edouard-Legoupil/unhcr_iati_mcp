"""Donor reference data for UNHCR IATI MCP Server."""

from unhcr_iati_mcp.context import mcp


@mcp.resource("unhcr://donors")
async def donors():
    """Get donor code to name mapping."""
    return {
        "DEU": "Germany", "USA": "United States", "SWE": "Sweden",
        "GBR": "United Kingdom", "NOR": "Norway", "DNK": "Denmark",
        "NLD": "Netherlands", "FIN": "Finland", "CAN": "Canada",
        "AUS": "Australia", "JPN": "Japan", "EU": "European Union",
    }
