"""
Country-related tools for analyzing UNHCR activities by country from IATI Datastore.
"""

from typing import Any, Dict, List, Tuple
from collections import Counter

from unhcr_iati_mcp.context import (
    mcp,
    iati_client,
    unhcr_filter,
)
from unhcr_iati_mcp.client import IATIError
from unhcr_iati_mcp.observability.logging import get_logger

logger = get_logger(__name__)


@mcp.tool(
    name="unhcr_top_countries",
    description="Get top N countries by activity count."
)
async def unhcr_top_countries(
    top_n: int = 20,
    max_records: int = 10000
) -> List[Tuple[str, int]]:
    """Get top N countries by activity count."""
    try:
        activities = await iati_client.fetch_all(
            collection="activity",
            q=unhcr_filter(),
            max_records=max_records
        )

        counter = Counter()

        for activity in activities:

            countries = activity.get(
                "recipient_country_code",
                []
            )

            for country in countries:
                counter[country] += 1

        return counter.most_common(top_n)
    except IATIError as e:
        logger.error(f"Error in unhcr_top_countries: {e}")
        return []
    except Exception as e:
        logger.exception("Unexpected error in unhcr_top_countries")
        return []
