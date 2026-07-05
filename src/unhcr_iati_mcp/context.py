"""
Context module for UNHCR IATI MCP Server.

This module holds shared state to avoid circular imports between server.py and tool files.
It provides the FastMCP instance, IATI client, and UNHCR filter function that are used
across the entire application.
"""

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


def unhcr_filter() -> str:
    """
    Generate the UNHCR publisher filter string for IATI Datastore queries.
    
    This is the base filter that should be used for all UNHCR data queries.
    It filters by reporting_org_ref to get only UNHCR-published data.
    
    Returns:
        str: Solr query filter string for UNHCR data
    """
    return f'reporting_org_ref:"{settings.unhcr_publisher_ref}"'


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
