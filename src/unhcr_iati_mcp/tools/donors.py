"""
Donor-related tools for analyzing UNHCR funding from IATI Datastore.
"""

from typing import Any, Dict, List, Tuple
from collections import defaultdict

from unhcr_iati_mcp.context import (
    mcp,
    iati_client,
    unhcr_filter,
    DEFAULT_MAX_RECORDS,
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
    name="unhcr_top_donors",
    description="Get top N donors by contribution amount."
)
async def unhcr_top_donors(
    top_n: int = 20,
    max_records: int = DEFAULT_MAX_RECORDS
) -> List[Tuple[str, float]]:
    """Get top N donors by contribution amount."""
    try:
        tx = await iati_client.fetch_all(
            collection="transaction",
            q=unhcr_filter(),
            max_records=max_records
        )

        donors = defaultdict(float)

        for row in tx:
            name = row.get(
                "transaction_provider_org_narrative",
                ["Unknown"]
            )[0]

            amount = row.get(
                "transaction_value",
                [0]
            )[0]

            donors[name] += float(amount)

        ranking = sorted(
            donors.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return ranking[:top_n]
    except IATIError as e:
        logger.error(f"Error in unhcr_top_donors: {e}")
        return []
    except Exception as e:
        logger.exception("Unexpected error in unhcr_top_donors")
        return []
