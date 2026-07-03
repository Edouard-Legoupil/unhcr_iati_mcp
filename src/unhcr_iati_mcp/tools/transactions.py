"""
Transaction-related tools for querying UNHCR transactions from IATI Datastore.
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
    name="unhcr_transactions",
    description="Retrieve all UNHCR transactions, optionally filtered by year."
)
async def unhcr_transactions(
    year: int | None = None
) -> List[Dict[str, Any]]:
    """
    Retrieve all UNHCR transactions.
    
    Args:
        year: Optional year to filter transactions by
        
    Returns:
        List of transaction dictionaries or empty list on error
    """
    try:
        q = unhcr_filter()

        if year:
            q += (
                f' AND transaction_value_value_date:['
                f'{year}-01-01T00:00:00Z TO '
                f'{year}-12-31T23:59:59Z]'
            )

        return await iati_client.fetch_all(
            collection="transaction",
            q=q
        )
    except IATIError as e:
        logger.error(f"Error in unhcr_transactions: {e}")
        return []
    except Exception as e:
        logger.exception("Unexpected error in unhcr_transactions")
        return []


@mcp.tool(
    name="unhcr_transaction_search",
    description="Search UNHCR transactions with a custom Solr query."
)
async def unhcr_transaction_search(
    query: str
) -> List[Dict[str, Any]]:
    """
    Search transactions using a custom Solr query string.
    
    Args:
        query: Solr query string (will be combined with UNHCR filter)
        
    Returns:
        List of transaction dictionaries matching the query or empty list on error
    """
    try:
        q = (
            f'{unhcr_filter()} '
            f'AND ({query})'
        )

        return await iati_client.fetch_all(
            collection="transaction",
            q=q
        )
    except IATIError as e:
        logger.error(f"Error in unhcr_transaction_search: {e}")
        return []
    except Exception as e:
        logger.exception("Unexpected error in unhcr_transaction_search")
        return []
