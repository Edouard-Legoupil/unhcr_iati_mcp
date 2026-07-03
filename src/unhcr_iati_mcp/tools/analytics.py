"""
Analytics tools for UNHCR portfolio from IATI Datastore.
"""

from typing import Any, Dict

from unhcr_iati_mcp.context import (
    mcp,
    iati_client,
    unhcr_filter,
)
from unhcr_iati_mcp.observability.logging import get_logger

logger = get_logger(__name__)


@mcp.tool(
    name="unhcr_portfolio_summary",
    description="Get aggregate counts for UNHCR portfolio (activities, budgets, transactions)."
)
async def unhcr_portfolio_summary() -> Dict[str, int]:
    """
    Retrieve aggregate counts for the UNHCR portfolio.
    
    Returns:
        Dictionary with counts for activities, budgets, and transactions
    """
    try:
        activities = await iati_client.fetch_all(
            "activity",
            unhcr_filter()
        )
        budgets = await iati_client.fetch_all(
            "budget",
            unhcr_filter()
        )
        transactions = await iati_client.fetch_all(
            "transaction",
            unhcr_filter()
        )
        return {
            "activities": len(activities),
            "budgets": len(budgets),
            "transactions": len(transactions)
        }
    except Exception as e:
        logger.exception("Error in portfolio summary")
        return {
            "error": str(e),
            "activities": 0,
            "budgets": 0,
            "transactions": 0
        }
