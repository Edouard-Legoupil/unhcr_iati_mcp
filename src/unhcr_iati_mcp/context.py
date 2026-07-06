"""
Context module for UNHCR IATI MCP Server.

This module holds shared state to avoid circular imports between server.py and tool files.
It provides the FastMCP instance, IATI client, and UNHCR filter function that are used
across the entire application.
"""

from typing import Any, Dict

from fastmcp import FastMCP

from unhcr_iati_mcp.client import IATIClient
from unhcr_iati_mcp.config import settings

# Initialize shared state
mcp = FastMCP(
    name="unhcr-iati-mcp",
    instructions="IATI Datastore for UNHCR - Access UNHCR's humanitarian aid data from IATI"
)

# Create the IATI client instance
iati_client = IATIClient()

DEFAULT_MAX_RECORDS = 500


def unhcr_filter() -> str:
    """
    Generate the UNHCR publisher filter string for IATI Datastore queries.
    
    This is the base filter that should be used for all UNHCR data queries.
    It filters by reporting_org_ref to get only UNHCR-published data.
    
    Returns:
        str: Solr query filter string for UNHCR data
    """
    return f'reporting_org_ref:"{settings.unhcr_publisher_ref}"'


# Programme code to label mapping
PROGRAMME_LABELS = {
    "AFR": "Africa",
    "AME": "The Americas",
    "ASO": "Asia and the Pacific",
    "EHGL": "East and Horn of Africa",
    "EUR": "Europe",
    "GLOBALPROG": "Global Program",
    "HQ": "Head Quarter",
    "JPO": "Junior Professional Officer",
    "MENA": "Middle East and North Africa",
    "SA": "Southern Africa",
    "SAO": "Southern Africa",
    "WCA": "West and Central Africa",
}


def parse_unhcr_identifier(iati_identifier: str) -> Dict[str, Any]:
    """
    Parse UNHCR IATI identifier to extract year, region, programme, country, and operation type.
    
    This replicates the R code logic from the original analysis framework.
    
    Args:
        iati_identifier: The IATI identifier string (e.g., "XM-DAC-41121-2024-MENA-SYR")
        
    Returns:
        Dictionary containing:
        - iati_identifier_year_reg_ops: Full identifier without XM-DAC-41121- prefix
        - year: Extracted year as integer (or None)
        - programme: Programme code (e.g., "MENA", "HQ", "GLOBALPROG")
        - programme_label: Human-readable programme name
        - iati_identifier_ops: Operation/country part (e.g., "SYR")
        - iso3c: ISO3 country code (or empty string)
        - ops_type: Operation type (or empty string)
        - is_operation: Boolean indicating if this is an operation (has "-" separator)
    """
    if not iati_identifier:
        return {
            "iati_identifier_year_reg_ops": "",
            "year": None,
            "programme": "",
            "programme_label": "",
            "iati_identifier_ops": "",
            "iso3c": "",
            "ops_type": "",
            "is_operation": False,
        }
    
    # Remove XM-DAC-41121- prefix
    prefix = "XM-DAC-41121-"
    if iati_identifier.startswith(prefix):
        year_reg_ops = iati_identifier[len(prefix):]
    else:
        year_reg_ops = iati_identifier
    
    # Extract year (first 4 characters)
    year = None
    if len(year_reg_ops) >= 4:
        year_str = year_reg_ops[:4]
        try:
            year = int(year_str)
        except ValueError:
            pass
    
    # Extract region/operation part (after year and dash)
    if len(year_reg_ops) > 5:
        reg_ops = year_reg_ops[5:]  # Skip year (4 chars) and dash (1 char)
    else:
        reg_ops = ""
    
    # Check if it's an operation (contains "-")
    is_operation = "-" in reg_ops
    sep = reg_ops.find("-") if is_operation else -1
    
    # Extract programme
    if is_operation and sep > 0:
        programme = reg_ops[:sep]
    else:
        programme = reg_ops
    
    # Map programme code to label
    programme_label = PROGRAMME_LABELS.get(programme, programme)
    
    # Extract operation part (after separator)
    if is_operation and sep >= 0:
        iati_identifier_ops = reg_ops[sep + 1:]
    else:
        iati_identifier_ops = ""
    
    # Extract ISO3 country code (first 3 characters of operation part)
    iso3c = ""
    if len(iati_identifier_ops) >= 3:
        iso3c = iati_identifier_ops[:3]
    
    # Extract operation type (after country code, if longer than 3 chars)
    ops_type = ""
    if len(iati_identifier_ops) > 3:
        ops_type = iati_identifier_ops[4:]  # Skip "-" and 3-char country code
    
    return {
        "iati_identifier_year_reg_ops": year_reg_ops,
        "year": year,
        "programme": programme,
        "programme_label": programme_label,
        "iati_identifier_ops": iati_identifier_ops,
        "iso3c": iso3c,
        "ops_type": ops_type,
        "is_operation": is_operation,
    }


def unhcr_identifier_filter(
    year: int | None = None,
    programme: str | None = None,
    country_code: str | None = None,
    operation: str | None = None,
) -> str:
    """
    Generate a Solr filter for UNHCR activities based on IATI identifier components.
    
    This function constructs a Solr query filter that matches UNHCR's IATI identifier
    pattern: XM-DAC-41121-{YEAR}-{PROGRAMME}[-{COUNTRY}[-{OPERATION}]]
    
    Args:
        year: Optional year to filter by (e.g., 2024)
        programme: Optional programme code (e.g., "MENA", "AFR", "HQ", "GLOBALPROG")
        country_code: Optional ISO3 country code (e.g., "SYR", "ETH")
        operation: Optional operation code (e.g., "USARO", "CRIRLU")
    
    Returns:
        str: Solr query filter string to be combined with unhcr_filter()
        
    Examples:
        # Filter for 2024 activities
        unhcr_identifier_filter(year=2024)
        
        # Filter for MENA region
        unhcr_identifier_filter(programme="MENA")
        
        # Filter for Syria country operations
        unhcr_identifier_filter(country_code="SYR")
        
        # Filter for MENA region, Syria, 2024
        unhcr_identifier_filter(year=2024, programme="MENA", country_code="SYR")
    """
    filters = []
    
    # Build the identifier pattern
    # XM-DAC-41121-{YEAR}-{PROGRAMME}[-{COUNTRY}[-{OPERATION}]]
    parts = []
    
    # Start with the publisher prefix
    parts.append("XM-DAC-41121")
    parts.append("-")
    
    # Add year
    if year is not None:
        parts.append(str(year))
    else:
        parts.append("*")
    
    parts.append("-")
    
    # Add programme
    if programme is not None:
        parts.append(programme)
    else:
        parts.append("*")
    
    # If we have country or operation, add them
    if country_code is not None or operation is not None:
        parts.append("-")
        
        if country_code is not None:
            parts.append(country_code)
        else:
            parts.append("*")
        
        if operation is not None:
            parts.append("-")
            parts.append(operation)
    
    # Construct the Solr query
    # Use iati_identifier_exact field which preserves the full identifier
    # and supports wildcard matching
    filter_str = "".join(parts)
    
    # The iati_identifier_exact field supports wildcard matching with *
    return f'iati_identifier_exact:{filter_str}'
