"""
Schema reference data for UNHCR IATI MCP Server.
"""

from unhcr_iati_mcp.context import mcp


@mcp.resource("unhcr://schemas/activity")
async def activity_schema():
    """
    Get schema definition for IATI activity data.
    
    Returns:
        Dictionary describing the activity schema
    """
    return {
        "iati_identifier": "string (required)",
        "title_narrative": "string[] (multilingual titles)",
        "description_narrative": "string[] (multilingual descriptions)",
        "reporting_org_ref": "string (publisher reference)",
        "reporting_org_type": "string (organization type)",
        "activity_status": "string (current status)",
        "activity_date": "string[] (activity dates)",
        "recipient_country_code": "string[] (ISO country codes)",
        "recipient_country_narrative": "string[] (country names)",
        "sector_code": "string[] (sector codes)",
        "sector_narrative": "string[] (sector names)",
        "budget": "object (linked budgets)",
        "transaction": "object[] (linked transactions)",
    }


@mcp.resource("unhcr://schemas/transaction")
async def transaction_schema():
    """
    Get schema definition for IATI transaction data.
    
    Returns:
        Dictionary describing the transaction schema
    """
    return {
        "iati_identifier": "string (linked activity)",
        "transaction_type": "string[] (transaction type codes)",
        "transaction_value": "float[] (amounts)",
        "transaction_value_currency": "string[] (currency codes)",
        "transaction_date": "string[] (dates in ISO format)",
        "provider_org_ref": "string[] (providing organization)",
        "provider_org_narrative": "string[] (provider names)",
        "receiver_org_ref": "string[] (receiving organization)",
        "receiver_org_narrative": "string[] (receiver names)",
        "description_narrative": "string[] (descriptions)",
    }


@mcp.resource("unhcr://schemas/budget")
async def budget_schema():
    """
    Get schema definition for IATI budget data.
    
    Returns:
        Dictionary describing the budget schema
    """
    return {
        "iati_identifier": "string (linked activity)",
        "budget_type": "string[] (budget type codes)",
        "budget_value": "float[] (budget amounts)",
        "budget_value_currency": "string[] (currency codes)",
        "budget_period_start": "string[] (start dates in ISO format)",
        "budget_period_end": "string[] (end dates in ISO format)",
        "description_narrative": "string[] (descriptions)",
    }
