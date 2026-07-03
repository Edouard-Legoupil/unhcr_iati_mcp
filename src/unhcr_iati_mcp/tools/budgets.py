"""
Budget-related tools for querying UNHCR budgets from IATI Datastore.
"""

from typing import Any, List

from unhcr_iati_mcp.context import (
    mcp,
    iati_client,
    unhcr_filter,
)


@mcp.tool(
    name="unhcr_budgets",
    description="Retrieve all UNHCR budgets, optionally filtered by year."
)
async def unhcr_budgets(
    year: int | None = None
) -> List[dict[str, Any]]:
    """
    Retrieve all UNHCR budgets.
    
    Args:
        year: Optional year to filter budgets by
        
    Returns:
        List of budget dictionaries
    """
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
