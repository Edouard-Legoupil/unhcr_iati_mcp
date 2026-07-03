"""
Transaction-related tools for querying UNHCR transactions from IATI Datastore.
"""

from typing import Any, List

from unhcr_iati_mcp.context import (
    mcp,
    iati_client,
    unhcr_filter,
)


@mcp.tool(
    name="unhcr_transactions",
    description="Retrieve all UNHCR transactions, optionally filtered by year."
)
async def unhcr_transactions(
    year: int | None = None
) -> List[dict[str, Any]]:
    """
    Retrieve all UNHCR transactions.
    
    Args:
        year: Optional year to filter transactions by
        
    Returns:
        List of transaction dictionaries
    """
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


@mcp.tool(
    name="unhcr_transaction_search",
    description="Search UNHCR transactions with a custom Solr query."
)
async def unhcr_transaction_search(
    query: str
) -> List[dict[str, Any]]:
    """
    Search transactions using a custom Solr query string.
    
    Args:
        query: Solr query string (will be combined with UNHCR filter)
        
    Returns:
        List of transaction dictionaries matching the query
    """
    q = (
        f'{unhcr_filter()} '
        f'AND ({query})'
    )

    return await iati_client.fetch_all(
        collection="transaction",
        q=q
    )
