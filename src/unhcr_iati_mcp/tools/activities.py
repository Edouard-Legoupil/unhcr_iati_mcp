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


def _resolve_country_code(country_input: str) -> str:
    """
    Resolve country input to ISO country code.
    
    Accepts ISO 2-letter, 3-letter codes, or country names (case-insensitive).
    Returns the ISO 3-letter country code used in IATI data.
    
    Args:
        country_input: Country code (2-letter, 3-letter) or name
        
    Returns:
        ISO 3-letter country code
        
    Raises:
        ValueError: If country cannot be resolved
    """
    # Country name to ISO 3-letter code mapping
    COUNTRY_NAMES_TO_ISO3 = {
        # Full names
        "afghanistan": "AFG", "south sudan": "SSD", "ukraine": "UKR",
        "syrian arab republic": "SYR", "syria": "SYR", "yemen": "YEM", 
        "somalia": "SOM", "bangladesh": "BGD", "ethiopia": "ETH",
        "kenya": "KEN", "uganda": "UGA", "turkey": "TUR", "lebanon": "LBN",
        "jordan": "JOR", "iraq": "IRQ", "colombia": "COL", 
        "venezuela": "VEN", "peru": "PER", "mexico": "MEX", "haiti": "HTI",
        "sudan": "SDN", "chad": "TCD", "niger": "NER", "mali": "MLI",
        "burkina faso": "BFA", "mauritania": "MRT", "senegal": "SEN",
        "guinea": "GIN", "liberia": "LBR", "sierra leone": "SLE",
        "gambia": "GMB", "nigeria": "NGA", "cameroon": "CMR",
        "central african republic": "CAF", "democratic republic of the congo": "COD",
        "republic of the congo": "COG", "angola": "AGO", "zambia": "ZMB",
        "zimbabwe": "ZWE", "malawi": "MWI", "mozambique": "MOZ",
        "tanzania": "TZA", "rwanda": "RWA", "burundi": "BDI",
        "eritrea": "ERI", "djibouti": "DJI", "pakistan": "PAK",
        "iran": "IRN", "afghanistan": "AFG", "myanmar": "MMR",
        "thailand": "THA", "malaysia": "MYS", "indonesia": "IDN",
        "philippines": "PHL", "sri lanka": "LKA", "nepal": "NPL",
        "bhutan": "BTN", "india": "IND", "china": "CHN", "egypt": "EGY",
        "libya": "LBY", "tunisia": "TUN", "algeria": "DZA", "morocco": "MAR",
        "mauritius": "MUS", "madagascar": "MDG", "comoros": "COM",
        "seychelles": "SYC", "cabo verde": "CPV", "guinea-bissau": "GNB",
        "equatorial guinea": "GNQ", "gabon": "GAB", "sao tome and principe": "STP",
        "botswana": "BWA", "namibia": "NAM", "eswatini": "SWZ",
        "lesotho": "LSO", "south africa": "ZAF", "brésil": "BRA",
        "argentina": "ARG", "bolivia": "BOL", "chile": "CHL",
        "paraguay": "PRY", "uruguay": "URY", "ecuador": "ECU",
        "germany": "DEU", "france": "FRA", "united kingdom": "GBR",
        "united states": "USA", "canada": "CAN", "australia": "AUS",
        "new zealand": "NZL", "japan": "JPN", "russia": "RUS",
    }
    
    # Clean and normalize input
    country_input = country_input.strip().lower()
    
    # Check if it's already a valid ISO code
    # ISO 2-letter codes
    iso2_to_iso3 = {
        "af": "AFG", "ss": "SSD", "ua": "UKR", "sy": "SYR", "ye": "YEM",
        "so": "SOM", "bd": "BGD", "et": "ETH", "ke": "KEN", "ug": "UGA",
        "tr": "TUR", "lb": "LBN", "jo": "JOR", "iq": "IRQ", "co": "COL",
        "ve": "VEN", "pe": "PER", "mx": "MEX", "ht": "HTI",
        "sd": "SDN", "td": "TCD", "ne": "NER", "ml": "MLI",
        "bf": "BFA", "mr": "MRT", "sn": "SEN", "gn": "GIN",
        "lr": "LBR", "sl": "SLE", "gm": "GMB", "ng": "NGA", "cm": "CMR",
        "cf": "CAF", "cd": "COD", "cg": "COG", "ao": "AGO", "zm": "ZMB",
        "zw": "ZWE", "mw": "MWI", "mz": "MOZ", "tz": "TZA", "rw": "RWA",
        "bi": "BDI", "er": "ERI", "dj": "DJI", "pk": "PAK", "ir": "IRN",
        "mm": "MMR", "th": "THA", "my": "MYS", "id": "IDN", "ph": "PHL",
        "lk": "LKA", "np": "NPL", "bt": "BTN", "in": "IND", "cn": "CHN",
        "eg": "EGY", "ly": "LBY", "tn": "TUN", "dz": "DZA", "ma": "MAR",
        "mu": "MUS", "mg": "MDG", "km": "COM", "sc": "SYC", "cv": "CPV",
        "gw": "GNB", "gq": "GNQ", "ga": "GAB", "st": "STP", "bw": "BWA",
        "na": "NAM", "sz": "SWZ", "ls": "LSO", "za": "ZAF", "br": "BRA",
        "ar": "ARG", "bo": "BOL", "cl": "CHL", "py": "PRY", "uy": "URY",
        "ec": "ECU", "de": "DEU", "fr": "FRA", "gb": "GBR", "us": "USA",
        "ca": "CAN", "au": "AUS", "nz": "NZL", "jp": "JPN", "ru": "RUS",
    }
    
    # If input is 2-letter ISO code, convert to 3-letter
    if len(country_input) == 2 and country_input in iso2_to_iso3:
        return iso2_to_iso3[country_input]
    
    # If input is 3-letter ISO code, validate it
    if len(country_input) == 3:
        # Check if it's a known 3-letter code
        known_iso3 = set(iso2_to_iso3.values()) | {
            "AFG", "SSD", "UKR", "SYR", "YEM", "SOM", "BGD", "ETH", "KEN", "UGA",
            "TUR", "LBN", "JOR", "IRQ", "COL", "VEN", "PER", "MEX", "HTI",
            "SDN", "TCD", "NER", "MLI", "BFA", "MRT", "SEN", "GIN", "LBR",
            "SLE", "GMB", "NGA", "CMR", "CAF", "COD", "COG", "AGO", "ZMB",
            "ZWE", "MWI", "MOZ", "TZA", "RWA", "BDI", "ERI", "DJI", "PAK",
            "IRN", "MMR", "THA", "MYS", "IDN", "PHL", "LKA", "NPL", "BTN",
            "IND", "CHN", "EGY", "LBY", "TUN", "DZA", "MAR", "MUS", "MDG",
            "COM", "SYC", "CPV", "GNB", "GNQ", "GAB", "STP", "BWA", "NAM",
            "SWZ", "LSO", "ZAF", "BRA", "ARG", "BOL", "CHL", "PRY", "URY",
            "ECU", "DEU", "FRA", "GBR", "USA", "CAN", "AUS", "NZL", "JPN",
            "RUS",
        }
        if country_input.upper() in known_iso3:
            return country_input.upper()
        
        # Try to find matching country name
        if country_input in COUNTRY_NAMES_TO_ISO3:
            return COUNTRY_NAMES_TO_ISO3[country_input]
    
    # Try to match country name
    if country_input in COUNTRY_NAMES_TO_ISO3:
        return COUNTRY_NAMES_TO_ISO3[country_input]
    
    # Try partial matching for country names
    for name, code in COUNTRY_NAMES_TO_ISO3.items():
        if country_input in name or name in country_input:
            return code
    
    # If all else fails, return as-is (might be a code we don't have mapped)
    return country_input.upper()


@mcp.tool(
    name="unhcr_activity_by_country",
    description="Retrieve UNHCR activities filtered by country code or name."
)
async def unhcr_activity_by_country(
    country_code: str,
    rows: int = 100,
    start: int = 0
) -> Dict[str, Any]:
    """Retrieve UNHCR activities filtered by country code.
    
    Args:
        country_code: ISO 2-letter code, 3-letter code, or country name (e.g., "IRQ", "IQ", "Iraq")
        rows: Number of results to return (default: 100)
        start: Starting offset for pagination (default: 0)
        
    Returns:
        Dictionary with query results including activities matching the country filter
    """
    try:
        # Resolve country code from name or ISO code
        resolved_code = _resolve_country_code(country_code)
        
        q = (
            f'{unhcr_filter()} '
            f'AND recipient_country_code:"{resolved_code}"'
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
    rows: int = 100,
    start: int = 0
) -> Dict[str, Any]:
    """Retrieve UNHCR activities for a specific year.
    
    Args:
        year: Year to filter activities by
        rows: Number of results to return (default: 100)
        start: Starting offset for pagination (default: 0)
        
    Returns:
        Dictionary with query results including activities from the specified year
    """
    try:
        q = (
            f'{unhcr_filter()} '
            f'AND activity_date_iso_date:['
            f'{year}-01-01T00:00:00Z TO '
            f'{year}-12-31T23:59:59Z]'
        )

        return await iati_client.query(
            collection="activity",
            q=q,
            rows=rows,
            start=start
        )
    except IATIError as e:
        return _handle_error(e, "unhcr_activity_by_year")
    except Exception as e:
        return _handle_error(e, "unhcr_activity_by_year")


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
