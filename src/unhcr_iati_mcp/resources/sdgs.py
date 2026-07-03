"""
Sustainable Development Goals reference data for UNHCR IATI MCP Server.
"""

from unhcr_iati_mcp.context import mcp


@mcp.resource("unhcr://sdgs")
async def sdgs():
    """
    Get SDG number to name mapping.
    
    Returns:
        Dictionary mapping SDG numbers to SDG names and descriptions
    """
    return {
        "1": {
            "name": "No Poverty",
            "description": "End poverty in all its forms everywhere"
        },
        "2": {
            "name": "Zero Hunger",
            "description": "End hunger, achieve food security and improved nutrition and promote sustainable agriculture"
        },
        "3": {
            "name": "Good Health and Well-being",
            "description": "Ensure healthy lives and promote well-being for all at all ages"
        },
        "4": {
            "name": "Quality Education",
            "description": "Ensure inclusive and equitable quality education and promote lifelong learning opportunities for all"
        },
        "5": {
            "name": "Gender Equality",
            "description": "Achieve gender equality and empower all women and girls"
        },
        "6": {
            "name": "Clean Water and Sanitation",
            "description": "Ensure availability and sustainable management of water and sanitation for all"
        },
        "10": {
            "name": "Reduced Inequalities",
            "description": "Reduce inequality within and among countries"
        },
        "16": {
            "name": "Peace, Justice and Strong Institutions",
            "description": "Promote peaceful and inclusive societies for sustainable development, provide access to justice for all and build effective, accountable and inclusive institutions at all levels"
        },
        "17": {
            "name": "Partnerships for the Goals",
            "description": "Strengthen the means of implementation and revitalize the global partnership for sustainable development"
        }
    }
