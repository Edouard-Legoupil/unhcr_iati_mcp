"""
Activity-related tools for querying UNHCR activities from IATI Datastore.
"""

from typing import Any, Dict, List

from unhcr_iati_mcp.context import (
    mcp,
    iati_client,
    unhcr_filter,
    unhcr_identifier_filter,
    parse_unhcr_identifier,
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
    """Retrieve UNHCR activities with pagination."""
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
    description="Retrieve a specific UNHCR activity by IATI identifier or identifier pattern."
)
async def unhcr_activity(
    iati_identifier: str
) -> Dict[str, Any]:
    """Retrieve a specific UNHCR activity by IATI identifier or identifier pattern."""
    try:
        # Parse the identifier to extract components
        parsed = parse_unhcr_identifier(iati_identifier)
        
        # Build the filter using the parsed components
        identifier_filter = unhcr_identifier_filter(
            year=parsed.get("year"),
            programme=parsed.get("programme") if parsed.get("programme") else None,
            country_code=parsed.get("iso3c") if parsed.get("iso3c") else None,
            operation=parsed.get("ops_type") if parsed.get("ops_type") else None,
        )
        
        # Combine with UNHCR publisher filter
        q = f'{unhcr_filter()} AND {identifier_filter}'

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
    """Retrieve UNHCR activities filtered by country code."""
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
    """Retrieve UNHCR activities filtered by sector code."""
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
    year: int,
    max_records: int = 10000
) -> List[Dict[str, Any]]:
    """Retrieve UNHCR activities for a specific year."""
    try:
        q = (
            f'{unhcr_filter()} '
            f'AND activity_date_iso_date:['
            f'{year}-01-01T00:00:00Z TO '
            f'{year}-12-31T23:59:59Z]'
        )

        return await iati_client.fetch_all(
            collection="activity",
            q=q,
            max_records=max_records
        )
    except IATIError as e:
        logger.error(f"Error in unhcr_activity_by_year: {e}")
        return []
    except Exception as e:
        logger.exception("Unexpected error in unhcr_activity_by_year")
        return []


@mcp.tool(
    name="unhcr_activity_by_identifier",
    description="Retrieve UNHCR activities filtered by IATI identifier components."
)
async def unhcr_activity_by_identifier(
    year: int | None = None,
    programme: str | None = None,
    country_code: str | None = None,
    operation: str | None = None,
    rows: int = 100,
    start: int = 0
) -> Dict[str, Any]:
    """Retrieve UNHCR activities filtered by IATI identifier components."""
    try:
        # Build the identifier filter
        identifier_filter = unhcr_identifier_filter(
            year=year,
            programme=programme,
            country_code=country_code,
            operation=operation
        )
        
        # Combine with UNHCR publisher filter
        q = f'{unhcr_filter()} AND {identifier_filter}'

        return await iati_client.query(
            collection="activity",
            q=q,
            rows=rows,
            start=start
        )
    except IATIError as e:
        return _handle_error(e, "unhcr_activity_by_identifier")
    except Exception as e:
        return _handle_error(e, "unhcr_activity_by_identifier")
