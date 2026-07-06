"""
Sector code mappings for UNHCR IATI MCP Server.

Provides essential sector vocabulary mappings to prevent cross-vocabulary aggregation errors.
"""

from typing import Dict, List, Any

from unhcr_iati_mcp.context import mcp


# =============================================================================
# MINIMIZED SECTOR VOCABULARY METADATA
# =============================================================================
# Only essential fields kept to reduce context window usage

SECTOR_VOCABULARY_METADATA: Dict[str, Dict[str, Any]] = {
    "1": {"name": "OECD DAC CRS 5-digit", "warning": "Do NOT aggregate with vocab 2"},
    "2": {"name": "OECD DAC CRS 3-digit", "warning": "Do NOT aggregate with vocab 1"},
    "3": {"name": "UN CoFoG", "warning": "Different system - NEVER aggregate with DAC"},
    "4": {"name": "EU NACE", "warning": "Economic classification - NOT sector"},
    "10": {"name": "IASC Clusters", "warning": "Humanitarian - different from DAC"},
    "98": {"name": "UNHCR-specific", "warning": "UNHCR primary - NEVER aggregate across vocabularies", "is_unhcr_primary": True},
    "99": {"name": "Org-specific", "warning": "Org-defined - NEVER aggregate across orgs"},
}


# =============================================================================
# UNHCR-SPECIFIC SECTOR CODES (Vocabulary 98) - Minimized
# =============================================================================

UNHCR_SECTOR_CODES: Dict[str, str] = {
    "10": "Protection",
    "111": "Law and Policy",
    "113": "Legal Remedies",
    "114": "Access to Territory",
    "115": "Public Attitudes",
    "2": "Early Recovery",
    "210": "Reception Conditions",
    "212": "Registration",
    "213": "Status Determination",
    "216": "Family Reunification",
    "312": "Health",
    "4": "Shelter",
    "410": "Emergency Shelter",
    "416": "Shelter Infrastructure",
    "418": "Basic Items",
    "419": "Special Needs Services",
    "513": "Child Protection",
    "5403": "Protection of Children",
    "5404": "Gender Based Violence",
    "613": "SGBV Prevention",
    "614": "Protection of Children",
    "7": "Self Reliance",
    "710": "Integration",
    "72010": "Material Relief",
    "72011": "Material Assistance",
    "72050": "Emergency Health",
    "811": "Coordination",
    "911": "Resettlement",
    "918": "Operations Management",
    "919": "Relief Coordination",
}


# =============================================================================
# MCP RESOURCES
# =============================================================================

@mcp.resource("unhcr://sectors")
async def sectors() -> Dict[str, str]:
    """Get UNHCR sector codes (vocabulary 98) to name mapping."""
    return UNHCR_SECTOR_CODES


@mcp.resource("unhcr://sector_vocabularies")
async def sector_vocabularies() -> Dict[str, Dict[str, Any]]:
    """Get IATI sector vocabulary metadata."""
    return SECTOR_VOCABULARY_METADATA


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_vocabulary_name(vocabulary_code: str) -> str:
    """Get human-readable name for a sector vocabulary code."""
    return SECTOR_VOCABULARY_METADATA.get(vocabulary_code, {}).get("name", "Unknown")


def is_unhcr_vocabulary(vocabulary_code: str) -> bool:
    """Check if a vocabulary is UNHCR's primary vocabulary (98)."""
    return SECTOR_VOCABULARY_METADATA.get(vocabulary_code, {}).get("is_unhcr_primary", False)


def validate_sector_aggregation(sector_codes: List[str], sector_vocabularies: List[str]) -> Dict[str, Any]:
    """Validate that sector aggregation won't mix vocabularies."""
    if len(sector_codes) != len(sector_vocabularies):
        return {
            "valid": False,
            "error": "Sector codes and vocabularies lists must be the same length",
            "severity": "ERROR"
        }
    
    unique_vocabs = set(sector_vocabularies)
    
    if len(unique_vocabs) > 1:
        return {
            "valid": False,
            "error": f"Cannot aggregate across multiple vocabularies: {unique_vocabs}",
            "severity": "CRITICAL",
            "recommendation": "Filter to a single vocabulary. For UNHCR, use vocabulary 98."
        }
    
    return {
        "valid": True,
        "vocabulary": list(unique_vocabs)[0] if unique_vocabs else None,
        "message": "Aggregation is valid (single vocabulary)"
    }
