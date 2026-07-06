"""
Sector reference data and vocabulary management for UNHCR IATI MCP Server.

This module provides comprehensive sector code resources with critical warnings about
sector vocabulary differences. It is essential for preventing incorrect cross-vocabulary
aggregation of IATI sector/budget data.

KEY INSIGHT: Sector codes have different meanings across vocabularies.
The same code (e.g., "10") in vocabulary 10 (IASC) means something different from
code "10" in vocabulary 98 (UNHCR-specific). NEVER sum percentages or aggregate
across vocabularies without filtering by vocabulary first.

Vocabulary System:
    - Vocabulary 1: OECD DAC CRS Purpose Codes (5-digit) - Standard international aid classification
    - Vocabulary 2: OECD DAC CRS Purpose Codes (3-digit) - Aggregated categories
    - Vocabulary 10: Humanitarian Global Clusters (IASC) - Humanitarian sector classification
    - Vocabulary 98: Reporting Organisation 2 - UNHCR-specific sector classification
    - Vocabulary 99: Reporting Organisation - Organisation-specific classification

UNHCR primarily uses vocabulary 98 for their sector classification.
"""

from typing import Dict, List, Any

from unhcr_iati_mcp.context import mcp


# =============================================================================
# SECTOR VOCABULARY METADATA
# =============================================================================
# This is the authoritative source for understanding IATI sector vocabularies.
# Each vocabulary represents a different classification system, and codes
# are NOT interchangeable between vocabularies.

SECTOR_VOCABULARY_METADATA: Dict[str, Dict[str, Any]] = {
    "1": {
        "code": "1",
        "name": "OECD DAC CRS Purpose Codes (5-digit)",
        "description": "The sector reported corresponds to an OECD DAC CRS 5-digit purpose code",
        "category": "sector",
        "url": "http://reference.iatistandard.org/codelists/Sector/",
        "status": "active",
        "usage_note": "Standard international development aid classification. 5-digit codes provide granular sector detail.",
        "warning": "Do NOT aggregate with vocabulary 2 (3-digit) codes - they are at different levels of granularity."
    },
    "2": {
        "code": "2",
        "name": "OECD DAC CRS Purpose Codes (3-digit)",
        "description": "The sector reported corresponds to an OECD DAC CRS 3-digit purpose code",
        "category": "sector",
        "url": "http://reference.iatistandard.org/codelists/SectorCategory/",
        "status": "active",
        "usage_note": "Aggregated sector categories. 3-digit codes are parent categories of 5-digit codes.",
        "warning": "Do NOT aggregate with vocabulary 1 (5-digit) codes - they are at different levels of granularity."
    },
    "3": {
        "code": "3",
        "name": "Classification of the Functions of Government (UN)",
        "description": "The sector reported corresponds to the UN Classification of the Functions of Government (CoFoG)",
        "category": "sector",
        "url": "http://unstats.un.org/unsd/cr/registry/regcst.asp?Cl=4",
        "status": "active",
        "usage_note": "UN government function classification system.",
        "warning": "Completely different classification system - NEVER aggregate with DAC CRS vocabularies."
    },
    "4": {
        "code": "4",
        "name": "Statistical classification of economic activities in the European Community",
        "description": "The sector reported corresponds to the statistical classifications of economic activities in the European Community",
        "category": "sector",
        "url": "http://ec.europa.eu/eurostat/ramon/nomenclatures/index.cfm?TargetUrl=LST_NOM_DTL&StrNom=NACE_REV2&StrLanguageCode=EN",
        "status": "active",
        "usage_note": "European economic activity classification (NACE Rev 2).",
        "warning": "Economic activity classification - NOT compatible with sector classifications."
    },
    "10": {
        "code": "10",
        "name": "Humanitarian Global Clusters (Inter-Agency Standing Committee)",
        "description": "The sector reported corresponds to an Inter-Agency Standing Committee Humanitarian Global Cluster code",
        "category": "sector",
        "url": "https://data.humdata.org/dataset/global-coordination-groups-beta",
        "status": "active",
        "usage_note": "Humanitarian sector classification used by UN and NGOs. UNHCR uses this alongside vocabulary 98.",
        "warning": "Humanitarian cluster codes - different from DAC CRS. Used by UNHCR but NEVER aggregate with vocabulary 98 without explicit mapping."
    },
    "98": {
        "code": "98",
        "name": "Reporting Organisation 2",
        "description": "The sector reported corresponds to a sector vocabulary maintained by the reporting organisation for this activity (if they are referencing more than one)",
        "category": "sector",
        "url": None,
        "status": "active",
        "usage_note": "UNHCR's PRIMARY sector classification vocabulary. Contains UNHCR-specific sectors like 'Protection', 'Health', 'Shelter', 'GBV', etc.",
        "warning": "UNHCR-specific classification. Codes like '10', '111', '113' etc. are UNHCR-specific and mean different things than in other vocabularies. NEVER aggregate across vocabularies.",
        "is_unhcr_primary": True
    },
    "99": {
        "code": "99",
        "name": "Reporting Organisation",
        "description": "The sector reported corresponds to a sector vocabulary maintained by the reporting organisation for this activity",
        "category": "sector",
        "url": None,
        "status": "active",
        "usage_note": "Organisation-specific classification. Used when organisations define their own sector codes.",
        "warning": "Organisation-specific codes - meaning is defined by each publisher. NEVER aggregate across different organisations."
    }
}


# =============================================================================
# UNHCR-SPECIFIC SECTOR CODES (Vocabulary 98)
# =============================================================================
# These are the sector codes used by UNHCR in vocabulary 98.
# Note: These codes are UNHCR-specific and do NOT correspond to OECD DAC CRS codes.

UNHCR_SECTOR_CODES: Dict[str, str] = {
    # Protection cluster
    "10": "Protection",
    "111": "Law and Policy",
    "113": "Legal Remedies and Legal Assistance",
    "114": "Access to the Territory and Non Refoulement",
    "115": "Public Attitudes towards Persons of Concern",
    
    # Early Recovery cluster
    "2": "Early Recovery",
    "210": "Reception Conditions",
    "212": "Registration and Profiling",
    "213": "Status Determination",
    "216": "Family Re-unification",
    
    # Health cluster
    "312": "Health",
    "314": "Health",
    
    # Shelter cluster
    "4": "Shelter and Infrastructure",
    "410": "Emergency Shelter and NFI",
    "416": "Shelter and Infrastructure",
    "418": "Basic and Domestic Items",
    "419": "Services for Persons with Specific Needs",
    
    # Multi-sector/Cross-cutting
    "513": "Child Protection",
    "5403": "Protection of Children",
    "5404": "Gender Based Violence",
    
    # Protection sub-sectors
    "613": "SGBV Prevention and Response",
    "614": "Protection of Children",
    
    # Livelihoods
    "7": "Self Reliance and Livelihoods",
    "710": "Integration",
    "72010": "Material relief assistance and services",
    "72011": "Material relief assistance",
    "72050": "Basic Health Care Services in Emergencies",
    
    # Coordination
    "811": "Coordination and Partnerships",
    
    # Resettlement
    "911": "Resettlement",
    
    # Operations management
    "918": "Operations management, Coordination and Support",
    "919": "Relief co-ordination and support services",
}


# =============================================================================
# SECTOR ANALYSIS GUIDELINES
# =============================================================================
# Critical guidance for working with IATI sector data to prevent analysis errors.

SECTOR_ANALYSIS_GUIDELINES: Dict[str, Any] = {
    "general_rules": {
        "rule_1": {
            "title": "NEVER aggregate across vocabularies",
            "description": "Sector codes have different meanings in different vocabularies. Summing percentages or counts across vocabularies without filtering will produce incorrect results.",
            "severity": "CRITICAL",
            "example": "Code '10' in vocabulary 10 (IASC) means 'Protection' but code '10' in vocabulary 1 (OECD DAC) means something completely different."
        },
        "rule_2": {
            "title": "Always filter by vocabulary first",
            "description": "When analyzing sector data, always group and filter by sector_vocabulary before performing any aggregation.",
            "severity": "CRITICAL",
            "example": "SELECT sector_vocabulary, sector_code, SUM(sector_percentage) FROM activities GROUP BY sector_vocabulary, sector_code"
        },
        "rule_3": {
            "title": "UNHCR uses multiple vocabularies",
            "description": "UNHCR primarily uses vocabulary 98 for their specific sector classification, but also uses vocabulary 10 (IASC clusters) and occasionally vocabulary 1 (OECD DAC).",
            "severity": "HIGH",
            "recommendation": "For UNHCR analysis, filter to vocabulary 98 for UNHCR-specific sectors, or vocabulary 10 for IASC humanitarian clusters."
        }
    },
    "common_mistakes": {
        "mistake_1": {
            "title": "Summing percentages across vocabularies",
            "description": "Adding up sector_percentage values without considering that they belong to different vocabulary systems.",
            "impact": "Will produce meaningless totals that don't represent any real sector allocation.",
            "fix": "Always group by sector_vocabulary AND sector_code before summing percentages."
        },
        "mistake_2": {
            "title": "Assuming code meanings are consistent",
            "description": "Assuming that sector code '12261' means the same thing in all vocabularies.",
            "impact": "Code '12261' in vocabulary 1 (OECD DAC) is 'Water supply' but in vocabulary 98 it could be something completely different.",
            "fix": "Always check the sector_vocabulary field alongside sector_code."
        },
        "mistake_3": {
            "title": "Ignoring percentage allocations",
            "description": "Using sector counts without considering sector_percentage weights.",
            "impact": "Activities can have multiple sectors with different percentage allocations. Counting each sector once ignores the actual resource distribution.",
            "fix": "Weight analyses by sector_percentage to reflect actual budget allocation."
        }
    },
    "recommended_queries": {
        "by_vocabulary": {
            "description": "Get sector breakdown by vocabulary",
            "query_pattern": "SELECT sector_vocabulary, sector_code, sector_narrative, SUM(sector_percentage) as total_percentage, COUNT(*) as activity_count FROM activities GROUP BY sector_vocabulary, sector_code, sector_narrative",
            "note": "This is the safest way to analyze sector data."
        },
        "unhcr_specific": {
            "description": "Get UNHCR-specific sector analysis",
            "query_pattern": "SELECT sector_code, sector_narrative, SUM(sector_percentage) as total_percentage FROM activities WHERE sector_vocabulary = '98' GROUP BY sector_code, sector_narrative",
            "note": "Filters to UNHCR's primary vocabulary."
        },
        "iasc_clusters": {
            "description": "Get humanitarian cluster analysis",
            "query_pattern": "SELECT sector_code, sector_narrative, SUM(sector_percentage) as total_percentage FROM activities WHERE sector_vocabulary = '10' GROUP BY sector_code, sector_narrative",
            "note": "Filters to IASC humanitarian cluster classification."
        }
    },
    "data_quality_notes": {
        "multiple_sectors_per_activity": "A single activity can have multiple sector classifications (from different vocabularies or the same vocabulary).",
        "percentage_normalization": "Sector percentages within a single activity typically sum to 100% but may not due to data quality issues.",
        "missing_vocabulary": "Some activities may have sector codes without explicit vocabulary specification. Treat these with caution.",
        "vocabulary_mixing": "UNHCR activities often mix vocabulary 98 (UNHCR-specific) and vocabulary 10 (IASC clusters) in the same activity."
    }
}


# =============================================================================
# MCP RESOURCES
# =============================================================================

@mcp.resource("unhcr://sectors")
async def sectors() -> Dict[str, str]:
    """
    Get sector code to name mapping for UNHCR-specific sectors (Vocabulary 98).
    
    This resource provides the primary sector classification used by UNHCR.
    These codes are UNHCR-specific and should NOT be confused with OECD DAC CRS codes
    or other vocabulary systems.
    
    IMPORTANT: The same code number can mean different things in different vocabularies.
    Always check the sector_vocabulary field in the source data.
    
    Returns:
        Dictionary mapping UNHCR sector codes (vocabulary 98) to sector names
        
    Example:
        {
            "10": "Protection",
            "111": "Law and Policy",
            "72010": "Material relief assistance and services",
            ...
        }
    """
    return UNHCR_SECTOR_CODES


@mcp.resource("unhcr://sector_vocabularies")
async def sector_vocabularies() -> Dict[str, Dict[str, Any]]:
    """
    Get metadata about all IATI sector vocabularies.
    
    This resource provides comprehensive information about each sector vocabulary
    system available in IATI data. This is CRITICAL for understanding that sector
    codes are NOT interchangeable between vocabularies.
    
    Key vocabularies for UNHCR analysis:
        - 98: UNHCR-specific sectors (PRIMARY for UNHCR analysis)
        - 10: IASC Humanitarian Clusters (used alongside 98)
        - 1: OECD DAC CRS 5-digit (occasionally used)
        - 2: OECD DAC CRS 3-digit (occasionally used)
    
    Returns:
        Dictionary mapping vocabulary codes to their metadata including:
        - name: Human-readable vocabulary name
        - description: What the vocabulary represents
        - usage_note: Guidance on when and how to use
        - warning: Critical warnings about cross-vocabulary aggregation
        - is_unhcr_primary: Boolean flag for UNHCR's primary vocabulary
        
    Example:
        {
            "98": {
                "name": "Reporting Organisation 2",
                "description": "UNHCR-specific sector classification",
                "is_unhcr_primary": True,
                "warning": "NEVER aggregate with other vocabularies"
            },
            ...
        }
    """
    return SECTOR_VOCABULARY_METADATA


@mcp.resource("unhcr://sector_analysis_guidelines")
async def sector_analysis_guidelines() -> Dict[str, Any]:
    """
    Get comprehensive guidelines for correctly analyzing IATI sector data.
    
    This resource provides essential rules, common mistakes, and recommended
    patterns for working with IATI sector data. Following these guidelines
    is CRITICAL to prevent incorrect aggregation across sector vocabularies.
    
    The most important rule: NEVER sum sector percentages or counts across
    different vocabularies without first filtering by vocabulary.
    
    Returns:
        Dictionary containing:
        - general_rules: Fundamental rules for sector analysis
        - common_mistakes: Frequently encountered errors and how to fix them
        - recommended_queries: Pattern examples for correct analysis
        - data_quality_notes: Important considerations about data quality
        
    Example:
        {
            "general_rules": {
                "rule_1": {
                    "title": "NEVER aggregate across vocabularies",
                    "severity": "CRITICAL",
                    "description": "Sector codes have different meanings..."
                },
                ...
            },
            ...
        }
    """
    return SECTOR_ANALYSIS_GUIDELINES


@mcp.resource("unhcr://sector_vocabulary_warnings")
async def sector_vocabulary_warnings() -> Dict[str, List[str]]:
    """
    Get critical warnings about sector vocabulary usage.
    
    This is a quick-reference resource that highlights the most important
    warnings for each vocabulary to prevent common analysis errors.
    
    Returns:
        Dictionary mapping vocabulary codes to lists of critical warnings.
        
    Example:
        {
            "1": ["Do NOT aggregate with vocabulary 2 (3-digit) codes"],
            "2": ["Do NOT aggregate with vocabulary 1 (5-digit) codes"],
            "98": ["UNHCR-specific - NEVER aggregate across vocabularies"],
            ...
        }
    """
    warnings = {}
    for vocab_code, metadata in SECTOR_VOCABULARY_METADATA.items():
        warnings[vocab_code] = [
            metadata.get("warning", ""),
            f"Vocabulary {vocab_code} uses a different classification system - always filter by vocabulary before aggregating"
        ]
        # Add UNHCR-specific note
        if metadata.get("is_unhcr_primary"):
            warnings[vocab_code].append("PRIMARY VOCABULARY FOR UNHCR ANALYSIS")
    return warnings


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_vocabulary_name(vocabulary_code: str) -> str:
    """
    Get the human-readable name for a sector vocabulary code.
    
    Args:
        vocabulary_code: The vocabulary code (e.g., "1", "2", "10", "98", "99")
        
    Returns:
        The name of the vocabulary, or "Unknown" if not found.
    """
    return SECTOR_VOCABULARY_METADATA.get(vocabulary_code, {}).get("name", "Unknown")


def is_unhcr_vocabulary(vocabulary_code: str) -> bool:
    """
    Check if a vocabulary is UNHCR's primary vocabulary.
    
    Args:
        vocabulary_code: The vocabulary code to check
        
    Returns:
        True if this is UNHCR's primary vocabulary (98), False otherwise.
    """
    return SECTOR_VOCABULARY_METADATA.get(vocabulary_code, {}).get("is_unhcr_primary", False)


def validate_sector_aggregation(sector_codes: List[str], sector_vocabularies: List[str]) -> Dict[str, Any]:
    """
    Validate that sector aggregation won't mix vocabularies.
    
    This function checks if a planned aggregation would violate the rule
    against mixing vocabularies.
    
    Args:
        sector_codes: List of sector codes to be aggregated
        sector_vocabularies: List of vocabulary codes corresponding to the sector codes
        
    Returns:
        Dictionary with validation result and warnings/errors
    """
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
            "recommendation": "Filter to a single vocabulary before aggregation. For UNHCR analysis, use vocabulary 98."
        }
    
    return {
        "valid": True,
        "vocabulary": list(unique_vocabs)[0] if unique_vocabs else None,
        "message": "Aggregation is valid (single vocabulary)"
    }
