"""
Sector-related tools for analyzing UNHCR activities by sector from IATI Datastore.
"""

from typing import Any, Dict
from collections import defaultdict

from unhcr_iati_mcp.context import (
    mcp,
    iati_client,
    unhcr_filter,
)
from unhcr_iati_mcp.client import IATIError
from unhcr_iati_mcp.observability.logging import get_logger

logger = get_logger(__name__)


@mcp.tool(
    name="unhcr_sector_summary",
    description="Get sector distribution across UNHCR activities."
)
async def unhcr_sector_summary() -> Dict[str, int]:
    """
    Retrieve and count activities by sector code.
    
    Returns:
        Dictionary mapping sector codes to activity counts
        or empty dict on error
    """
    try:
        activities = await iati_client.fetch_all(
            collection="activity",
            q=unhcr_filter()
        )

        sectors = defaultdict(int)

        for activity in activities:

            for sector in activity.get(
                "sector_code",
                []
            ):
                sectors[sector] += 1

        return dict(sectors)
    except IATIError as e:
        logger.error(f"Error in unhcr_sector_summary: {e}")
        return {}
    except Exception as e:
        logger.exception("Unexpected error in unhcr_sector_summary")
        return {}
