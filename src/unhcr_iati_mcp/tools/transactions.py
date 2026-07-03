"""
Transaction-related tools for querying UNHCR transactions from IATI Datastore.
"""

import re
from typing import Any, Dict, List

from unhcr_iati_mcp.context import (
    mcp,
    iati_client,
    unhcr_filter,
)
from unhcr_iati_mcp.client import IATIError
from unhcr_iati_mcp.observability.logging import get_logger

logger = get_logger(__name__)


def _sanitize_solr_query(query: str) -> str:
    """
    Sanitize user input for safe use in Solr queries.
    
    Prevents Solr injection by escaping special characters and blocking
    dangerous operators that could be used to bypass filters or perform DoS.
    
    Args:
        query: User-provided query string
        
    Returns:
        Sanitized query string safe for Solr
    """
    # Remove potentially dangerous Solr operators and wildcards
    dangerous_patterns = [
        r'\(\s*\*\s*\)',  # (*) - matches all
        r'\*\s*:\s*\*',   # *:* - matches all
        r'AND\s+reporting_org_ref:',  # Attempt to override org filter
        r'OR\s+reporting_org_ref:',   # Attempt to override org filter
        r'NOT\s+reporting_org_ref:', # Attempt to override org filter
    ]
    
    sanitized = query
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    
    # Escape Solr special characters that aren't in allowed set
    # Allowed: alphanumeric, spaces, basic operators we permit
    special_chars = r'[+\-=&|!\(\)\{\}\[\]\^"~*?:\\/]'
    sanitized = re.sub(special_chars, r'\\\g<0>', sanitized)
    
    return sanitized.strip()


def _handle_error(error: Exception, tool_name: str) -> Dict[str, Any]:
    """Handle errors and return a consistent error response."""
    logger.exception(f"Error in {tool_name}")
    return {
        "error": str(error),
        "tool": tool_name,
        "success": False
    }


@mcp.tool(
    name="unhcr_transactions",
    description="Retrieve all UNHCR transactions, optionally filtered by year."
)
async def unhcr_transactions(
    year: int | None = None
) -> List[Dict[str, Any]]:
    """
    Retrieve all UNHCR transactions.
    
    Args:
        year: Optional year to filter transactions by
        
    Returns:
        List of transaction dictionaries or empty list on error
    """
    try:
        q = unhcr_filter()

        if year:
            q += (
                f' AND transaction_value_value_date:['
                f'{year}-01-01T00:00:00Z TO '
                f'{year}-12-31T23:59:59Z]'
            )

        return await iati_client.fetch_all(
            collection="transaction",
            q=q
        )
    except IATIError as e:
        logger.error(f"Error in unhcr_transactions: {e}")
        return []
    except Exception as e:
        logger.exception("Unexpected error in unhcr_transactions")
        return []


@mcp.tool(
    name="unhcr_transaction_search",
    description="Search UNHCR transactions with a custom Solr query."
)
async def unhcr_transaction_search(
    query: str,
    max_records: int = 10000
) -> List[Dict[str, Any]]:
    """
    Search transactions using a custom Solr query string.
    
    Args:
        query: Solr query string (will be combined with UNHCR filter)
        max_records: Maximum number of records to return (default: 10000)
        
    Returns:
        List of transaction dictionaries matching the query or empty list on error
    """
    try:
        # Sanitize user query to prevent Solr injection
        sanitized_query = _sanitize_solr_query(query)
        
        if not sanitized_query:
            logger.warning("Empty query after sanitization")
            return []
        
        q = (
            f'{unhcr_filter()} '
            f'AND ({sanitized_query})'
        )

        return await iati_client.fetch_all(
            collection="transaction",
            q=q,
            max_records=max_records
        )
    except IATIError as e:
        logger.error(f"Error in unhcr_transaction_search: {e}")
        return []
    except Exception as e:
        logger.exception("Unexpected error in unhcr_transaction_search")
        return []
