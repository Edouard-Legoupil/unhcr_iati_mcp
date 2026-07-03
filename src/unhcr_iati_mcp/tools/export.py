"""
Export tools for UNHCR IATI data in various formats.
"""

import json
import csv
from io import StringIO
from typing import Any, List, Dict

from unhcr_iati_mcp.context import (
    mcp,
    iati_client,
    unhcr_filter,
)


@mcp.tool(
    name="unhcr_export_json",
    description="Export UNHCR data as JSON."
)
async def unhcr_export_json(
    collection: str,
    query: str = ""
) -> str:
    """
    Export data from a collection as JSON.
    
    Args:
        collection: The IATI Datastore collection to export (activity, transaction, budget)
        query: Optional additional Solr query filter
        
    Returns:
        JSON string containing the exported data
    """
    q = f"{unhcr_filter()}" + (f" AND ({query})" if query else "")
    data = await iati_client.fetch_all(collection=collection, q=q)
    return json.dumps(data, indent=2, default=str)


@mcp.tool(
    name="unhcr_export_csv",
    description="Export UNHCR data as CSV."
)
async def unhcr_export_csv(
    collection: str,
    query: str = ""
) -> str:
    """
    Export data from a collection as CSV.
    
    Args:
        collection: The IATI Datastore collection to export (activity, transaction, budget)
        query: Optional additional Solr query filter
        
    Returns:
        CSV string containing the exported data
    """
    q = f"{unhcr_filter()}" + (f" AND ({query})" if query else "")
    data = await iati_client.fetch_all(collection=collection, q=q)
    
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


@mcp.tool(
    name="unhcr_bulk_extract",
    description="Bulk extract data from multiple IATI collections."
)
async def unhcr_bulk_extract(
    collections: List[str],
    format: str = "json"
) -> Dict[str, Any]:
    """
    Bulk extract data from multiple collections.
    
    Args:
        collections: List of collection names to extract
        format: Output format (json or csv)
        
    Returns:
        Dictionary mapping collection names to extracted data
    """
    results = {}
    for collection in collections:
        q = unhcr_filter()
        data = await iati_client.fetch_all(collection=collection, q=q)
        
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
    
    return results
