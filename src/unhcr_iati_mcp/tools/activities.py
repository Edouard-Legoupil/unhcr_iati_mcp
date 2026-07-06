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
    description="Retrieve a specific UNHCR activity by IATI identifier or identifier pattern."
)
async def unhcr_activity(
    iati_identifier: str
) -> Dict[str, Any]:
    """
    Retrieve a specific activity by its IATI identifier.
    
    This tool supports both full IATI identifiers and partial patterns.
    It uses the iati_identifier_exact field with wildcard matching for better results.
    
    Args:
        iati_identifier: The IATI identifier for the activity. Can be:
            - Full identifier: "XM-DAC-41121-2024-MENA-SYR"
            - Partial pattern: "XM-DAC-41121-2024-MENA" (matches all MENA activities in 2024)
            - Year only: "XM-DAC-41121-2024" (matches all activities in 2024)
        
    Returns:
        Dictionary containing the activity data or error information
    """
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
    year: int,
    max_records: int = 10000
) -> List[Dict[str, Any]]:
    """
    Retrieve all activities for a specific year.
    
    Args:
        year: The year to filter activities by
        max_records: Maximum number of records to return (default: 10000)
        
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
    """
    Retrieve UNHCR activities filtered by IATI identifier components.
    
    This tool provides flexible filtering using the UNHCR IATI identifier structure:
    XM-DAC-41121-{YEAR}-{PROGRAMME}[-{COUNTRY}[-{OPERATION}]]
    
    It uses the iati_identifier_exact field with wildcard matching for precise results.
    
    Args:
        year: Optional year to filter by (e.g., 2024)
        programme: Optional programme code (e.g., "MENA", "AFR", "HQ", "GLOBALPROG")
        country_code: Optional ISO3 country code (e.g., "SYR", "ETH")
        operation: Optional operation code (e.g., "USARO", "CRIRLU")
        rows: Number of results to return per page (default: 100)
        start: Starting offset for pagination (default: 0)
        
    Returns:
        Dictionary containing IATI Datastore response with filtered activities
        or error information if the request fails
        
    Examples:
        # Filter for 2024 activities
        unhcr_activity_by_identifier(year=2024)
        
        # Filter for MENA region
        unhcr_activity_by_identifier(programme="MENA")
        
        # Filter for Syria country operations
        unhcr_activity_by_identifier(country_code="SYR")
        
        # Filter for MENA region, Syria, 2024
        unhcr_activity_by_identifier(year=2024, programme="MENA", country_code="SYR")
    """
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
