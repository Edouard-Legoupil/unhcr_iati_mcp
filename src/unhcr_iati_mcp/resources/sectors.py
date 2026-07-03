"""
Sector reference data for UNHCR IATI MCP Server.
"""

from unhcr_iati_mcp.context import mcp


@mcp.resource("unhcr://sectors")
async def sectors():
    """
    Get sector code to name mapping.
    
    Returns:
        Dictionary mapping IATI sector codes to sector names
    """
    return {
        "72010": "Material relief assistance",
        "72040": "Emergency food assistance",
        "15180": "Ending violence against women",
        "12110": "Health education",
        "12181": "Basic health care",
        "12261": "Water supply",
        "12262": "Basic sanitation",
        "12310": "Primary education",
        "12340": "Vocational training",
        "13010": "Environmental protection",
    }
