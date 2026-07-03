"""
Budget-related tools for querying UNHCR budgets from IATI Datastore.
"""

from typing import Any, Dict, List

from unhcr_iati_mcp.context import (
    mcp,
    iati_client,
    unhcr_filter,
)
from unhcr_iati_mcp.client import IATIError
from unhcr_iati_mcp.observability.logging import get_logger

logger = get_logger(__name__)


def _handle_error(error: Exception, tool_name: str) -> Dict[str, Any]:
    """Handle errors and return a consistent error response."""
    logger.exception(f"Error in {tool_name}")
    return {
        "error": str(error),
        "tool": tool_name,
        "success": False
    }


@mcp.tool(
    name="unhcr_budgets",
    description="Retrieve all UNHCR budgets, optionally filtered by year."
)
async def unhcr_budgets(
    year: int | None = None
) -> List[Dict[str, Any]]:
    """
    Retrieve all UNHCR budgets.
    
    Args:
        year: Optional year to filter budgets by
        
    Returns:
        List of budget dictionaries or empty list on error
    """
    try:
        q = unhcr_filter()

        if year:
            q += (
                f' AND budget_period_start:['
                f'{year}-01-01T00:00:00Z TO '
                f'{year}-12-31T23:59:59Z]'
            )

        return await iati_client.fetch_all(
            collection="budget",
            q=q
        )
    except IATIError as e:
        logger.error(f"Error in unhcr_budgets: {e}")
        return []
    except Exception as e:
        logger.exception("Unexpected error in unhcr_budgets")
        return []
