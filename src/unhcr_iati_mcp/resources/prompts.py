"""
Prompt templates for UNHCR IATI MCP Server.

These prompts provide AI agents with structured instructions for analyzing
UNHCR's IATI data.
"""

from unhcr_iati_mcp.context import mcp


@mcp.prompt("unhcr://prompts/analyse_country")
async def analyse_country():
    """
    Prompt for analyzing a country's UNHCR programme.
    
    Returns:
        String containing the analysis prompt
    """
    return """
    Analyse the country programme.

    Review:
    - activity count
    - budget
    - donor concentration
    - sector coverage

    Provide recommendations.
    """
