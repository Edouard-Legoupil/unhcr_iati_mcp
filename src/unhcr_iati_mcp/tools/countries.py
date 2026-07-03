"""
Country-related tools for analyzing UNHCR activities by country from IATI Datastore.
"""

from typing import Any, List, Tuple
from collections import Counter

from unhcr_iati_mcp.context import (
    mcp,
    iati_client,
    unhcr_filter,
)


@mcp.tool(
    name="unhcr_top_countries",
    description="Get top N countries by activity count."
)
async def unhcr_top_countries(
    top_n: int = 20
) -> List[Tuple[str, int]]:
    """
    Retrieve and rank countries by the number of activities.
    
    Args:
        top_n: Number of top countries to return
        
    Returns:
        List of tuples containing (country_code, activity_count) sorted by count descending
    """
    activities = await iati_client.fetch_all(
        collection="activity",
        q=unhcr_filter()
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
