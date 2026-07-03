"""
Export tools for UNHCR IATI data in various formats.
"""

import re
import json
import csv
from io import StringIO
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
    special_chars = r'[+\-=&|!\(\)\{\}\[\]\^"~*?:\\/]'
    sanitized = re.sub(special_chars, r'\\\g<0>', sanitized)
    
    return sanitized.strip()


@mcp.tool(
    name="unhcr_export_json",
    description="Export UNHCR data as JSON."
)
async def unhcr_export_json(
    collection: str,
    query: str = "",
    max_records: int = 10000
) -> str:
    """
    Export data from a collection as JSON.
    
    Args:
        collection: The IATI Datastore collection to export (activity, transaction, budget)
        query: Optional additional Solr query filter
        max_records: Maximum number of records to export (default: 10000)
        
    Returns:
        JSON string containing the exported data or error message
    """
    try:
        sanitized_query = _sanitize_solr_query(query) if query else ""
        if sanitized_query:
            q = f"{unhcr_filter()} AND ({sanitized_query})"
        else:
            q = unhcr_filter()
        
        data = await iati_client.fetch_all(
            collection=collection,
            q=q,
            max_records=max_records
        )
        return json.dumps(data, indent=2, default=str)
    except IATIError as e:
        logger.error(f"Error in unhcr_export_json: {e}")
        return json.dumps({"error": str(e), "success": False})
    except Exception as e:
        logger.exception("Unexpected error in unhcr_export_json")
        return json.dumps({"error": "Internal server error", "success": False})


@mcp.tool(
    name="unhcr_export_csv",
    description="Export UNHCR data as CSV."
)
async def unhcr_export_csv(
    collection: str,
    query: str = "",
    max_records: int = 10000
) -> str:
    """
    Export data from a collection as CSV.
    
    Args:
        collection: The IATI Datastore collection to export (activity, transaction, budget)
        query: Optional additional Solr query filter
        max_records: Maximum number of records to export (default: 10000)
        
    Returns:
        CSV string containing the exported data or error message
    """
    try:
        sanitized_query = _sanitize_solr_query(query) if query else ""
        if sanitized_query:
            q = f"{unhcr_filter()} AND ({sanitized_query})"
        else:
            q = unhcr_filter()
        
        data = await iati_client.fetch_all(
            collection=collection,
            q=q,
            max_records=max_records
        )
        
        if not data:
            return ""
        
        # Get all keys from all records
        fieldnames = set()
        for record in data:
            fieldnames.update(record.keys())
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=sorted(fieldnames), extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()
    except IATIError as e:
        logger.error(f"Error in unhcr_export_csv: {e}")
        return f"error: {str(e)}"
    except Exception as e:
        logger.exception("Unexpected error in unhcr_export_csv")
        return f"error: Internal server error"


@mcp.tool(
    name="unhcr_bulk_extract",
    description="Bulk extract data from multiple IATI collections."
)
async def unhcr_bulk_extract(
    collections: List[str],
    format: str = "json",
    max_records_per_collection: int = 10000
) -> Dict[str, Any]:
    """
    Bulk extract data from multiple collections.
    
    Args:
        collections: List of collection names to extract
        format: Output format (json or csv)
        max_records_per_collection: Maximum records per collection (default: 10000)
        
    Returns:
        Dictionary mapping collection names to extracted data or error information
    """
    results = {}
    
    for collection in collections:
        try:
            q = unhcr_filter()
            data = await iati_client.fetch_all(
                collection=collection,
                q=q,
                max_records=max_records_per_collection
            )
            
            if format == "csv":
                # Convert to CSV
                if data:
                    fieldnames = set()
                    for record in data:
                        fieldnames.update(record.keys())
                    output = StringIO()
                    writer = csv.DictWriter(output, fieldnames=sorted(fieldnames), extrasaction='ignore')
                    writer.writeheader()
                    writer.writerows(data)
                    results[collection] = output.getvalue()
                else:
                    results[collection] = ""
            else:
                # Default to JSON
                results[collection] = data
        except IATIError as e:
            logger.error(f"Error extracting {collection}: {e}")
            results[collection] = {"error": str(e), "success": False}
        except Exception as e:
            logger.exception(f"Unexpected error extracting {collection}")
            results[collection] = {"error": "Internal server error", "success": False}
    
    return results
