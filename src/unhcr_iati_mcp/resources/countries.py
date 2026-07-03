"""
Country reference data for UNHCR IATI MCP Server.
"""

from unhcr_iati_mcp.context import mcp


@mcp.resource("unhcr://countries")
async def countries():
    """
    Get country code to name mapping for UNHCR operations.
    
    Returns:
        Dictionary mapping ISO country codes to country names
    """
    return {
        "AFG": "Afghanistan",
        "SSD": "South Sudan",
        "UKR": "Ukraine",
        "SYR": "Syrian Arab Republic",
        "YEM": "Yemen",
        "SOM": "Somalia",
        "BGD": "Bangladesh",
        "ETH": "Ethiopia",
        "KEN": "Kenya",
        "UGA": "Uganda",
        "TUR": "Turkey",
        "LBN": "Lebanon",
        "JOR": "Jordan",
        "IRQ": "Iraq",
        "COL": "Colombia",
        "VEN": "Venezuela",
        "PER": "Peru",
        "MEX": "Mexico",
        "HTI": "Haiti",
    }
