"""
Activity-related tools for querying UNHCR activities from IATI Datastore.
"""

from datetime import datetime
from typing import Any, Dict, List

from unhcr_iati_mcp.context import (
    mcp,
    iati_client,
    unhcr_filter,
    unhcr_identifier_filter,
    parse_unhcr_identifier,
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


DEFAULT_SUMMARY_ROWS = 5
METADATA_ROW_LIMIT = 200


def _parse_iso_timestamp(value: str | None) -> datetime | None:
    if not value or not isinstance(value, str):
        return None

    clean = value.rstrip("Z")

    try:
        return datetime.fromisoformat(clean)
    except ValueError:
        return None


async def _fetch_country_availability(country_code: str) -> list[Dict[str, Any]]:
    q = (
        f"{unhcr_filter()} "
        f"AND location_code:\"{country_code}\""
    )

    try:
        payload = await iati_client.metadata_data_availability(
            q=q,
            rows=METADATA_ROW_LIMIT,
            fl=(
                "location_code,reference_period_start,"
                "reference_period_end,admin_level,category"
            ),
        )
    except IATIError as exc:
        logger.warning(
            "Failed to fetch metadata availability for %s: %s",
            country_code,
            exc,
        )
        return []
    except Exception as exc:
        logger.exception(
            "Unexpected error fetching metadata availability for %s",
            country_code,
        )
        return []

    return (
        payload
        .get("response", {})
        .get("docs", [])
    )


def _summarize_coverage(country_code: str, docs: list[Dict[str, Any]]) -> Dict[str, Any]:
    earliest_date = None
    earliest_ref = None
    latest_date = None
    latest_ref = None
    categories = set()
    admin_levels = set()

    for doc in docs:
        start_raw = doc.get("reference_period_start")
        end_raw = doc.get("reference_period_end")

        start_dt = _parse_iso_timestamp(start_raw)
        end_dt = _parse_iso_timestamp(end_raw)

        if start_dt and (earliest_date is None or start_dt < earliest_date):
            earliest_date = start_dt
            earliest_ref = start_raw

        if end_dt and (latest_date is None or end_dt > latest_date):
            latest_date = end_dt
            latest_ref = end_raw

        if isinstance(doc.get("category"), str):
            categories.add(doc["category"])

        if admin := doc.get("admin_level"):
            admin_levels.add(str(admin))

    return {
        "country_code": country_code,
        "coverage_records": len(docs),
        "earliest_reference_period_start": earliest_ref,
        "latest_reference_period_end": latest_ref,
        "categories": sorted(categories),
        "admin_levels": sorted(admin_levels),
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
    name="unhcr_activity_by_country_summary",
    description="Summarize metadata coverage before returning a small sample of country activities."
)
async def unhcr_activity_by_country_summary(
    country_code: str,
    rows: int = DEFAULT_SUMMARY_ROWS
) -> Dict[str, Any]:
    """Return activity coverage summary and the latest rows for a country."""
    metadata_docs = await _fetch_country_availability(country_code)
    coverage = _summarize_coverage(country_code, metadata_docs)

    q = (
        f'{unhcr_filter()} '
        f'AND recipient_country_code:"{country_code}"'
    )

    if (
        coverage.get("earliest_reference_period_start")
        and coverage.get("latest_reference_period_end")
    ):
        q += (
            f' AND activity_date_iso_date:['
            f'{coverage["earliest_reference_period_start"]} TO '
            f'{coverage["latest_reference_period_end"]}]'
        )

    try:
        activities = await iati_client.query(
            collection="activity",
            q=q,
            rows=rows,
        )
    except IATIError as e:
        return _handle_error(e, "unhcr_activity_by_country_summary")
    except Exception as e:
        return _handle_error(e, "unhcr_activity_by_country_summary")

    return {
        "coverage_summary": coverage,
        "activities": (
            activities.get("response", {})
            .get("docs", [])
        ),
        "query": q,
    }


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
    max_records: int = DEFAULT_MAX_RECORDS
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
