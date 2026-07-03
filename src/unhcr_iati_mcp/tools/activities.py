"""
Activity-related tools for querying UNHCR activities from IATI Datastore.
"""

from typing import Any

from unhcr_iati_mcp.context import (
    mcp,
    iati_client,
    unhcr_filter,
)


@mcp.tool(
    name="unhcr_activities",
    description="Retrieve UNHCR activities with pagination."
)
async def unhcr_activities(
    rows: int = 100,
    start: int = 0
) -> dict[str, Any]:
    """
    Retrieve UNHCR activities from IATI Datastore.
    
    Args:
        rows: Number of results to return per page
        start: Starting offset for pagination
        
    Returns:
        Dictionary containing IATI Datastore response with activities
    """
    return await iati_client.query(
        collection="activity",
        q=unhcr_filter(),
        rows=rows,
        start=start
    )


@mcp.tool(
    name="unhcr_activity",
    description="Retrieve a specific UNHCR activity by IATI identifier."
)
async def unhcr_activity(
    iati_identifier: str
) -> dict[str, Any]:
    """
    Retrieve a specific activity by its IATI identifier.
    
    Args:
        iati_identifier: The unique IATI identifier for the activity
        
    Returns:
        Dictionary containing the activity data
    """
    q = (
        f'{unhcr_filter()} '
        f'AND iati_identifier:"{iati_identifier}"'
    )

    return await iati_client.query(
        collection="activity",
        q=q,
        rows=1
    )


@mcp.tool(
    name="unhcr_activity_by_country",
    description="Retrieve UNHCR activities filtered by country code."
)
async def unhcr_activity_by_country(
    country_code: str,
    rows: int = 100
) -> dict[str, Any]:
    """
    Retrieve activities for a specific country.
    
    Args:
        country_code: ISO 2-letter or 3-letter country code
        rows: Number of results to return
        
    Returns:
        Dictionary containing activities for the specified country
    """
    q = (
        f'{unhcr_filter()} '
        f'AND recipient_country_code:{country_code}'
    )

    return await iati_client.query(
        collection="activity",
        q=q,
        rows=rows
    )


@mcp.tool(
    name="unhcr_activity_by_sector",
    description="Retrieve UNHCR activities filtered by sector code."
)
async def unhcr_activity_by_sector(
    sector_code: str,
    rows: int = 100
) -> dict[str, Any]:
    """
    Retrieve activities for a specific sector.
    
    Args:
        sector_code: IATI sector code (e.g., "1", "2", "3")
        rows: Number of results to return
        
    Returns:
        Dictionary containing activities for the specified sector
    """
    q = (
        f'{unhcr_filter()} '
        f'AND sector_code:{sector_code}'
    )

    return await iati_client.query(
        collection="activity",
        q=q,
        rows=rows
    )


@mcp.tool(
    name="unhcr_activity_by_year",
    description="Retrieve UNHCR activities for a specific year."
)
async def unhcr_activity_by_year(
    year: int
) -> list[dict[str, Any]]:
    """
    Retrieve all activities for a specific year.
    
    Args:
        year: The year to filter activities by
        
    Returns:
        List of activity dictionaries
    """
    q = (
        f'{unhcr_filter()} '
        f'AND activity_date_iso_date:['
        f'{year}-01-01T00:00:00Z TO '
        f'{year}-12-31T23:59:59Z]'
    )

    return await iati_client.fetch_all(
        collection="activity",
        q=q
    )
