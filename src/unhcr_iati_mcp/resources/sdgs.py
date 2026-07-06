"""Sustainable Development Goals reference data for UNHCR IATI MCP Server."""

from unhcr_iati_mcp.context import mcp


@mcp.resource("unhcr://sdgs")
async def sdgs():
    """Get SDG number to name mapping."""
    return {
        "1": {"name": "No Poverty"},
        "2": {"name": "Zero Hunger"},
        "3": {"name": "Good Health and Well-being"},
        "4": {"name": "Quality Education"},
        "5": {"name": "Gender Equality"},
        "6": {"name": "Clean Water and Sanitation"},
        "10": {"name": "Reduced Inequalities"},
        "16": {"name": "Peace, Justice and Strong Institutions"},
        "17": {"name": "Partnerships for the Goals"},
    }
