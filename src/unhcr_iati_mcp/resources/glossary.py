"""Glossary reference data for UNHCR IATI MCP Server."""

from unhcr_iati_mcp.context import mcp


@mcp.resource("unhcr://glossary")
async def glossary():
    """Get IATI terminology glossary."""
    return {
        "activity": "IATI project/programme",
        "transaction": "Financial movement",
        "budget": "Planned funding",
        "reporting_org": "Publishing organisation",
        "iati_identifier": "Unique identifier",
        "sector_code": "IATI sector classification",
        "sector": "Humanitarian sector",
        "datastore": "IATI Solr query API",
        "mcp": "Model Context Protocol",
    }
