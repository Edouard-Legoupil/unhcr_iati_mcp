"""Schema reference data for UNHCR IATI MCP Server."""

from unhcr_iati_mcp.context import mcp


@mcp.resource("unhcr://schemas/activity")
async def activity_schema():
    """Get IATI activity schema."""
    return {
        "iati_identifier": "string", "title_narrative": "string[]",
        "reporting_org_ref": "string", "activity_status": "string",
        "recipient_country_code": "string[]", "sector_code": "string[]",
    }


@mcp.resource("unhcr://schemas/transaction")
async def transaction_schema():
    """Get IATI transaction schema."""
    return {
        "iati_identifier": "string", "transaction_type": "string[]",
        "transaction_value": "float[]", "transaction_date": "string[]",
    }


@mcp.resource("unhcr://schemas/budget")
async def budget_schema():
    """Get IATI budget schema."""
    return {
        "iati_identifier": "string", "budget_type": "string[]",
        "budget_value": "float[]", "budget_period_start": "string[]",
        "budget_period_end": "string[]",
    }
