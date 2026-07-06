"""
Code Resolution Tools for IATI Code Lookup.

This module provides tools for resolving IATI codes to human-readable values,
validating codes, and searching through code tables.

These tools complement the code_tables resources by providing dynamic lookup
and validation capabilities for AI agents and applications.
"""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path

import pyreadr

from unhcr_iati_mcp.context import mcp
from unhcr_iati_mcp.observability.logging import get_logger

logger = get_logger(__name__)

# Directory containing RData files
RDATA_DIR = Path(__file__).parent.parent.parent.parent / ".arc" / "R-analysis"

# Cache for loaded code tables
_code_table_cache: Dict[str, List[Dict[str, Any]]] = {}


def _load_code_table(filename: str) -> List[Dict[str, Any]]:
    """
    Load an RData file and return as list of dictionaries.
    
    Args:
        filename: The filename without .RData extension
    
    Returns:
        List of dictionaries representing the code table entries
    """
    if filename in _code_table_cache:
        return _code_table_cache[filename]
    
    filepath = RDATA_DIR / f"{filename}.RData"
    
    try:
        result = pyreadr.read_r(str(filepath))
        df = list(result.values())[0]
        data = df.to_dict(orient="records")
        
        # Clean up numpy types
        cleaned_data = []
        for entry in data:
            cleaned_entry = {}
            for key, value in entry.items():
                if hasattr(value, 'item'):
                    cleaned_entry[key] = value.item()
                elif value != value:  # NaN check
                    cleaned_entry[key] = None
                else:
                    cleaned_entry[key] = value
            cleaned_data.append(cleaned_entry)
        
        _code_table_cache[filename] = cleaned_data
        return cleaned_data
    except Exception as e:
        logger.error(f"Failed to load code table {filename}: {e}")
        return []


# Pre-load frequently used tables
PRELOAD_TABLES = [
    "codeCountry",
    "codeSector",
    "codeOrganisationRole",
    "codeActivityStatus",
    "codeAidType",
    "codePolicyMarker",
]

for table in PRELOAD_TABLES:
    _load_code_table(table)


# Mapping of code type aliases to actual filenames
CODE_TYPE_MAPPING = {
    # Activity codes
    "activity_status": "codeActivityStatus",
    "activity_scope": "codeActivityScope",
    "activity_date_type": "codeActivityDateType",
    "activity": "codeActivityStatus",
    
    # Organisation codes
    "organisation_role": "codeOrganisationRole",
    "organisation_type": "codeOrganisationType",
    "organisation": "codeOrganisationRole",
    "org_role": "codeOrganisationRole",
    
    # Geographic codes
    "country": "codeCountry",
    "countries": "codeCountry",
    "region": "codeRegion",
    "regions": "codeRegion",
    "geographic": "codeCountry",
    
    # Financial codes
    "aid_type": "codeAidType",
    "aid": "codeAidType",
    "flow_type": "codeFlowType",
    "currency": "codeCurrency",
    "earmarking": "codeEarmarkingCategory",
    "transaction_type": "codeTransactionType",
    "budget": "codeBudgetType",
    "financial": "codeAidType",
    
    # Sector codes
    "sector": "codeSector",
    "sectors": "codeSector",
    "sector_category": "codeSectorCategory",
    "sector_vocabulary": "codeSectorVocabulary",
    
    # Policy codes
    "policy_marker": "codePolicyMarker",
    "policy": "codePolicyMarker",
    "humanitarian_scope": "codeHumanitarianScopeType",
    "collaboration_type": "codeCollaborationType",
    "cluster": "codeHumCluster",
    
    # Result framework
    "result_type": "codeResultType",
    "indicator_measure": "codeIndicatorMeasure",
    "indicator": "codeIndicatorMeasure",
    "result": "codeResultType",
    
    # SDG
    "sdg_goal": "codeUNSDGGoals",
    "sdg_target": "codeUNSDGTargets",
    "sdg": "codeUNSDGGoals",
}


def _normalize_code_value(value: Any) -> str:
    """
    Normalize a code value for comparison.
    
    Handles numeric codes (int, float) and string codes, normalizing them
    to a consistent string representation.
    
    Examples:
        12220.0 -> "12220"
        12220 -> "12220"
        "12220" -> "12220"
        "SYR" -> "SYR"
    """
    if value is None:
        return ""
    
    # Convert to string
    str_value = str(value)
    
    # Remove trailing .0 from floats
    if str_value.endswith(".0"):
        str_value = str_value[:-2]
    
    return str_value


def _resolve_table_name(code_type: str) -> str:
    """Resolve a code type alias to the actual RData filename."""
    # Direct match
    if code_type in CODE_TYPE_MAPPING:
        return CODE_TYPE_MAPPING[code_type]
    
    # Try common prefixes
    prefixes = ["code", "mapping"]
    for prefix in prefixes:
        candidate = f"{prefix}{code_type.capitalize()}"
        if candidate in _code_table_cache or (RDATA_DIR / f"{candidate}.RData").exists():
            return candidate
    
    # Try as-is
    if (RDATA_DIR / f"{code_type}.RData").exists():
        return code_type
    
    # Try capitalized
    capitalized = code_type.capitalize()
    if (RDATA_DIR / f"{capitalized}.RData").exists():
        return capitalized
    
    # Default to sector as a reasonable fallback
    return "codeSector"


@mcp.tool(
    name="resolve_code",
    description="Resolve an IATI code to its human-readable name and metadata"
)
async def resolve_code(
    code_type: str,
    code: str,
    table: Optional[str] = None
) -> Dict[str, Any]:
    """Resolve an IATI code to its human-readable name and metadata."""
    try:
        # Determine which table to use
        if table:
            table_name = table
        else:
            table_name = _resolve_table_name(code_type)
        
        # Load the table
        data = _load_code_table(table_name)
        
        if not data:
            return {
                "code": code,
                "code_type": code_type,
                "table": table_name,
                "found": False,
                "error": f"Table {table_name} not found or empty"
            }
        
        # Normalize the input code for comparison
        normalized_code = _normalize_code_value(code)
        
        # Search for the code
        # Try matching on 'code' field first (most common)
        for entry in data:
            entry_code = entry.get("code")
            if _normalize_code_value(entry_code) == normalized_code:
                return {
                    "code": code,
                    "code_type": code_type,
                    "table": table_name,
                    "found": True,
                    "name": entry.get("name"),
                    "description": entry.get("description"),
                    "metadata": entry
                }
        
        # Try matching on other fields if code field doesn't match
        for entry in data:
            for key, value in entry.items():
                if _normalize_code_value(value) == normalized_code:
                    return {
                        "code": code,
                        "code_type": code_type,
                        "table": table_name,
                        "found": True,
                        "name": entry.get("name"),
                        "description": entry.get("description"),
                        "matched_field": key,
                        "metadata": entry
                    }
        
        # Code not found
        return {
            "code": code,
            "code_type": code_type,
            "table": table_name,
            "found": False,
            "error": f"Code '{code}' not found in table {table_name}"
        }
        
    except Exception as e:
        logger.error(f"Error in resolve_code: {e}")
        return {
            "code": code,
            "code_type": code_type,
            "table": table or _resolve_table_name(code_type),
            "found": False,
            "error": str(e)
        }


@mcp.tool(
    name="validate_code",
    description="Validate if an IATI code exists in a code table"
)
async def validate_code(
    code_type: str,
    code: str,
    table: Optional[str] = None
) -> Dict[str, Any]:
    """Validate if an IATI code exists in a code table."""
    try:
        if table:
            table_name = table
        else:
            table_name = _resolve_table_name(code_type)
        
        data = _load_code_table(table_name)
        
        if not data:
            return {
                "code": code,
                "code_type": code_type,
                "table": table_name,
                "valid": False,
                "error": f"Table {table_name} not found"
            }
        
        # Normalize the input code for comparison
        normalized_code = _normalize_code_value(code)
        
        # Check if code exists
        for entry in data:
            entry_code = entry.get("code")
            if _normalize_code_value(entry_code) == normalized_code:
                return {
                    "code": code,
                    "code_type": code_type,
                    "table": table_name,
                    "valid": True,
                    "name": entry.get("name")
                }
        
        return {
            "code": code,
            "code_type": code_type,
            "table": table_name,
            "valid": False,
            "error": f"Code '{code}' not found in {table_name}"
        }
        
    except Exception as e:
        logger.error(f"Error in validate_code: {e}")
        return {
            "code": code,
            "code_type": code_type,
            "table": table or _resolve_table_name(code_type),
            "valid": False,
            "error": str(e)
        }


@mcp.tool(
    name="search_code_table",
    description="Search an IATI code table by name or description"
)
async def search_code_table(
    code_type: str,
    query: str,
    limit: int = 20,
    table: Optional[str] = None
) -> Dict[str, Any]:
    """Search an IATI code table by name or description."""
    try:
        if table:
            table_name = table
        else:
            table_name = _resolve_table_name(code_type)
        
        data = _load_code_table(table_name)
        
        if not data:
            return {
                "query": query,
                "table": table_name,
                "results": [],
                "count": 0,
                "limit": limit,
                "error": f"Table {table_name} not found"
            }
        
        # Search in name and description fields
        query_lower = query.lower()
        results = []
        
        for entry in data:
            name = entry.get("name") or ""
            description = entry.get("description") or ""
            code = entry.get("code") or ""
            
            if (query_lower in name.lower() or 
                query_lower in description.lower() or 
                query_lower in str(code).lower()):
                results.append(entry)
        
        return {
            "query": query,
            "table": table_name,
            "results": results[:limit],
            "count": len(results),
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error in search_code_table: {e}")
        return {
            "query": query,
            "table": table or _resolve_table_name(code_type),
            "results": [],
            "count": 0,
            "limit": limit,
            "error": str(e)
        }


@mcp.tool(
    name="list_code_table",
    description="List all entries in an IATI code table"
)
async def list_code_table(
    code_type: str,
    limit: int = 100,
    offset: int = 0,
    table: Optional[str] = None
) -> Dict[str, Any]:
    """List all entries in an IATI code table."""
    try:
        if table:
            table_name = table
        else:
            table_name = _resolve_table_name(code_type)
        
        data = _load_code_table(table_name)
        
        if not data:
            return {
                "table": table_name,
                "entries": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
                "error": f"Table {table_name} not found"
            }
        
        total = len(data)
        entries = data[offset:offset + limit]
        
        return {
            "table": table_name,
            "entries": entries,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error in list_code_table: {e}")
        return {
            "table": table or _resolve_table_name(code_type),
            "entries": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
            "error": str(e)
        }


@mcp.tool(
    name="batch_resolve_codes",
    description="Resolve multiple IATI codes in a single call"
)
async def batch_resolve_codes(
    code_type: str,
    codes: List[str],
    table: Optional[str] = None
) -> Dict[str, Any]:
    """Resolve multiple IATI codes in a single call."""
    try:
        if table:
            table_name = table
        else:
            table_name = _resolve_table_name(code_type)
        
        data = _load_code_table(table_name)
        
        if not data:
            return {
                "code_type": code_type,
                "table": table_name,
                "codes": codes,
                "results": [{"code": c, "found": False, "error": "Table not found"} for c in codes],
                "resolved": 0,
                "unresolved": len(codes)
            }
        
        # Build a lookup dictionary for faster resolution
        # Use normalized codes as keys
        code_lookup = {}
        for entry in data:
            code_val = entry.get("code")
            normalized_val = _normalize_code_value(code_val)
            if normalized_val not in code_lookup:
                code_lookup[normalized_val] = entry
        
        results = []
        resolved_count = 0
        
        for code in codes:
            normalized_code = _normalize_code_value(code)
            if normalized_code in code_lookup:
                entry = code_lookup[normalized_code]
                results.append({
                    "code": code,
                    "found": True,
                    "name": entry.get("name"),
                    "description": entry.get("description"),
                    "metadata": entry
                })
                resolved_count += 1
            else:
                results.append({
                    "code": code,
                    "found": False,
                    "error": f"Code '{code}' not found in {table_name}"
                })
        
        return {
            "code_type": code_type,
            "table": table_name,
            "codes": codes,
            "results": results,
            "resolved": resolved_count,
            "unresolved": len(codes) - resolved_count
        }
        
    except Exception as e:
        logger.error(f"Error in batch_resolve_codes: {e}")
        return {
            "code_type": code_type,
            "table": table or _resolve_table_name(code_type),
            "codes": codes,
            "results": [{"code": c, "found": False, "error": str(e)} for c in codes],
            "resolved": 0,
            "unresolved": len(codes)
        }
