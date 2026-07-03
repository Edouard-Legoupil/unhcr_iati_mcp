"""
Glossary reference data for UNHCR IATI MCP Server.
"""

from unhcr_iati_mcp.context import mcp


@mcp.resource("unhcr://glossary")
async def glossary():
    """
    Get IATI terminology glossary for UNHCR data.
    
    Returns:
        Dictionary mapping terms to their definitions
    """
    return {
        "activity": "Top level IATI project/programme",
        "transaction": "Financial movement or disbursement",
        "budget": "Planned funding allocation",
        "reporting_org": "Publishing organisation",
        "reporting_org_ref": "Unique identifier for the publishing organisation",
        "iati_identifier": "Unique identifier for an activity, transaction, or budget",
        "recipient_country_code": "ISO 2-letter or 3-letter country code",
        "sector_code": "IATI sector classification code",
        "sector": "Humanitarian sector (e.g., health, education, WASH)",
        "transaction_type": "Type of financial transaction",
        "budget_period": "Time period covered by the budget",
        "datastore": "IATI's Solr-based query API",
        "mcp": "Model Context Protocol - standard for AI tool integration",
    }
