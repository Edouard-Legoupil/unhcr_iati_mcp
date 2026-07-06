"""
Result type mappings for UNHCR IATI MCP Server.

Provides IATI result framework metadata.
"""

from typing import Dict, List, Any, Optional

from unhcr_iati_mcp.context import mcp


# =============================================================================
# MINIMIZED RESULT TYPE METADATA
# =============================================================================

RESULT_TYPE_METADATA: Dict[str, Dict[str, Any]] = {
    "1": {"code": "1", "name": "Output", "level": "activity", "is_quantitative": True},
    "2": {"code": "2", "name": "Outcome", "level": "country/operation", "is_quantitative": True},
    "3": {"code": "3", "name": "Impact", "level": "global", "is_quantitative": False},
    "9": {"code": "9", "name": "Other", "level": "unspecified", "is_quantitative": False},
}


# =============================================================================
# MINIMIZED INDICATOR MEASURE METADATA
# =============================================================================

INDICATOR_MEASURE_METADATA: Dict[str, Dict[str, Any]] = {
    "1": {"code": "1", "name": "Unit", "is_quantitative": True},
    "2": {"code": "2", "name": "Percentage", "is_quantitative": True},
    "3": {"code": "3", "name": "Nominal", "is_quantitative": True},
    "4": {"code": "4", "name": "Ordinal", "is_quantitative": True},
    "5": {"code": "5", "name": "Qualitative", "is_quantitative": False},
}


# =============================================================================
# MINIMIZED UNHCR RESULT AREAS
# =============================================================================

UNHCR_RESULT_AREAS: Dict[str, Dict[str, Any]] = {
    "OA1": {"name": "Protection", "category": "protection"},
    "OA2": {"name": "Solutions", "category": "solutions"},
    "OA3": {"name": "Health", "category": "health"},
    "OA4": {"name": "Education", "category": "education"},
    "OA5": {"name": "Livelihoods", "category": "livelihoods"},
    "OA6": {"name": "Shelter and Settlements", "category": "shelter"},
    "OA7": {"name": "Water, Sanitation and Hygiene", "category": "wash"},
    "OA8": {"name": "Food Security", "category": "food"},
    "OA9": {"name": "Multi-sector", "category": "multi_sector"},
    "OA10": {"name": "Leadership, Coordination and Partnerships", "category": "coordination"},
    "OA11": {"name": "Emergency Response", "category": "emergency"},
    "OA12": {"name": "Advocacy and Legal Protection", "category": "protection"},
    "OA13": {"name": "Community Empowerment", "category": "empowerment"},
    "OA14": {"name": "Inclusion", "category": "inclusion"},
    "OA15": {"name": "Gender Equality", "category": "gender"},
    "OA16": {"name": "Age and Diversity", "category": "diversity"},
}


# =============================================================================
# MCP RESOURCES
# =============================================================================

@mcp.resource("unhcr://result_types")
async def result_types() -> Dict[str, Dict[str, Any]]:
    """Get IATI result type codes."""
    return RESULT_TYPE_METADATA


@mcp.resource("unhcr://indicator_measures")
async def indicator_measures() -> Dict[str, Dict[str, Any]]:
    """Get IATI indicator measure codes."""
    return INDICATOR_MEASURE_METADATA


@mcp.resource("unhcr://result_areas")
async def result_areas() -> Dict[str, Dict[str, Any]]:
    """Get UNHCR's 16 Operational Areas."""
    return UNHCR_RESULT_AREAS


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_result_type_name(result_type_code: str) -> str:
    """Get human-readable name for a result type code."""
    return RESULT_TYPE_METADATA.get(result_type_code, {}).get("name", "Unknown")


def get_indicator_measure_name(measure_code: str) -> str:
    """Get human-readable name for an indicator measure code."""
    return INDICATOR_MEASURE_METADATA.get(measure_code, {}).get("name", "Unknown")


def is_quantitative_measure(measure_code: str) -> bool:
    """Check if an indicator measure is quantitative."""
    return INDICATOR_MEASURE_METADATA.get(measure_code, {}).get("is_quantitative", False)
