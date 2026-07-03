"""
Activity-related tools for querying UNHCR activities from IATI Datastore.
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
    name="unhcr_activities",
    description="Retrieve UNHCR activities with pagination."
)
async def unhcr_activities(
    rows: int = 100,
    start: int = 0
) -> Dict[str, Any]:
    """
    Retrieve UNHCR activities from IATI Datastore.
    
    Args:
        rows: Number of results to return per page (default: 100)
        start: Starting offset for pagination (default: 0)
        
    Returns:
        Dictionary containing IATI Datastore response with activities
        or error information if the request fails
    """
    try:
        return await iati_client.query(
            collection="activity",
            q=unhcr_filter(),
            rows=rows,
            start=start
        )
    except IATIError as e:
        return _handle_error(e, "unhcr_activities")
    except Exception as e:
        return _handle_error(e, "unhcr_activities")


@mcp.tool(
    name="unhcr_activity",
    description="Retrieve a specific UNHCR activity by IATI identifier."
)
async def unhcr_activity(
    iati_identifier: str
) -> Dict[str, Any]:
    """
    Retrieve a specific activity by its IATI identifier.
    
    Args:
        iati_identifier: The unique IATI identifier for the activity
        
    Returns:
        Dictionary containing the activity data or error information
    """
    try:
        q = (
            f'{unhcr_filter()} '
            f'AND iati_identifier:"{iati_identifier}"'
        )

        return await iati_client.query(
            collection="activity",
            q=q,
            rows=1
        )
    except IATIError as e:
        return _handle_error(e, "unhcr_activity")
    except Exception as e:
        return _handle_error(e, "unhcr_activity")


@mcp.tool(
    name="unhcr_activity_by_country",
    description="Retrieve UNHCR activities filtered by country code."
)
async def unhcr_activity_by_country(
    country_code: str,
    rows: int = 100,
    start: int = 0
) -> Dict[str, Any]:
    """
    Retrieve activities for a specific country.
    
    Args:
        country_code: ISO 2-letter or 3-letter country code
        rows: Number of results to return (default: 100)
        start: Starting offset for pagination (default: 0)
        
    Returns:
        Dictionary containing activities for the specified country or error information
    """
    try:
        q = (
            f'{unhcr_filter()} '
            f'AND recipient_country_code:"{country_code}"'
        )

        return await iati_client.query(
            collection="activity",
            q=q,
            rows=rows,
            start=start
        )
    except IATIError as e:
        return _handle_error(e, "unhcr_activity_by_country")
    except Exception as e:
        return _handle_error(e, "unhcr_activity_by_country")


@mcp.tool(
    name="unhcr_activity_by_sector",
    description="Retrieve UNHCR activities filtered by sector code."
)
async def unhcr_activity_by_sector(
    sector_code: str,
    rows: int = 100,
    start: int = 0
) -> Dict[str, Any]:
    """
    Retrieve activities for a specific sector.
    
    Args:
        sector_code: IATI sector code (e.g., "1", "2", "3")
        rows: Number of results to return (default: 100)
        start: Starting offset for pagination (default: 0)
        
    Returns:
        Dictionary containing activities for the specified sector or error information
    """
    try:
        q = (
            f'{unhcr_filter()} '
            f'AND sector_code:"{sector_code}"'
        )

        return await iati_client.query(
            collection="activity",
            q=q,
            rows=rows,
            start=start
        )
    except IATIError as e:
        return _handle_error(e, "unhcr_activity_by_sector")
    except Exception as e:
        return _handle_error(e, "unhcr_activity_by_sector")


@mcp.tool(
    name="unhcr_activity_by_year",
    description="Retrieve UNHCR activities for a specific year."
)
async def unhcr_activity_by_year(
    year: int
) -> List[Dict[str, Any]]:
    """
    Retrieve all activities for a specific year.
    
    Args:
        year: The year to filter activities by
        
    Returns:
        List of activity dictionaries or empty list on error
    """
    try:
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
    except IATIError as e:
        logger.error(f"Error in unhcr_activity_by_year: {e}")
        return []
    except Exception as e:
        logger.exception("Unexpected error in unhcr_activity_by_year")
        return []
