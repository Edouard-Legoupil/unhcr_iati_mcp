"""
Result and Indicator resources for UNHCR IATI MCP Server.

This module provides comprehensive resources for working with IATI result framework data,
including result types, indicator measures, and UNHCR-specific result areas.

The IATI result framework is essential for tracking and reporting on the outcomes
and impacts of humanitarian activities. UNHCR uses a hierarchical results framework
with Output, Outcome, and Impact levels.

Key Concepts:
- Results: Classified by type (Output, Outcome, Impact, Other)
- Indicators: Measurable metrics within results (Unit, Percentage, Nominal, Ordinal, Qualitative)
- Periods: Time-bound measurements (baseline, target, actual)
- Dimensions: Disaggregation by characteristics (sex, age, location, etc.)

UNHCR's Results Framework:
- Impact: Long-term outcomes (global level)
- Outcome: Medium-term results (country/operation level) - 16 Operational Areas
- Output: Short-term deliverables (activity level)
"""

from typing import Dict, List, Any, Optional

from unhcr_iati_mcp.context import mcp


# =============================================================================
# RESULT TYPE METADATA
# =============================================================================
# From codeResultType.RData

RESULT_TYPE_METADATA: Dict[str, Dict[str, Any]] = {
    "1": {
        "code": "1",
        "name": "Output",
        "description": "Results of the activity that came about as a direct effect of your work and specific, what is done, and what communities are reached. For example, X number of individuals.",
        "category": "result",
        "level": "activity",
        "unhcr_level": "Short-term deliverables",
        "example": "Number of refugees provided with shelter",
        "url": None,
        "status": "active"
    },
    "2": {
        "code": "2",
        "name": "Outcome",
        "description": "Results of the activity that produce an effect on the overall communities or issues you serve. For example lower rate of infection after a vaccination programme.",
        "category": "result",
        "level": "country/operation",
        "unhcr_level": "Medium-term results",
        "example": "Improved access to protection services",
        "unhcr_notes": "UNHCR has 16 Operational Areas (OA) at the outcome level",
        "url": None,
        "status": "active"
    },
    "3": {
        "code": "3",
        "name": "Impact",
        "description": "The long term effects of the outcomes, that lead to larger, over arching results, such as improved life-expectancy.",
        "category": "result",
        "level": "global",
        "unhcr_level": "Long-term outcomes",
        "example": "Improved life expectancy for refugees",
        "url": None,
        "status": "active"
    },
    "9": {
        "code": "9",
        "name": "Other",
        "description": "Another type of result, not specified above.",
        "category": "result",
        "level": "unspecified",
        "unhcr_level": "Other",
        "url": None,
        "status": "active"
    }
}


# =============================================================================
# INDICATOR MEASURE METADATA
# =============================================================================
# From codeIndicatorMeasure.RData

INDICATOR_MEASURE_METADATA: Dict[str, Dict[str, Any]] = {
    "1": {
        "code": "1",
        "name": "Unit",
        "description": "The indicator is measured in units.",
        "category": "indicator",
        "is_quantitative": True,
        "example": "Number of individuals",
        "url": None,
        "status": "active"
    },
    "2": {
        "code": "2",
        "name": "Percentage",
        "description": "The indicator is measured in percentages",
        "category": "indicator",
        "is_quantitative": True,
        "example": "Percentage of population with access",
        "url": None,
        "status": "active"
    },
    "3": {
        "code": "3",
        "name": "Nominal",
        "description": "The indicator is measured as a quantitative nominal scale.",
        "category": "indicator",
        "is_quantitative": True,
        "example": "Number of categories",
        "url": None,
        "status": "active"
    },
    "4": {
        "code": "4",
        "name": "Ordinal",
        "description": "The indicator is measured as a quantitative ordinal scale.",
        "category": "indicator",
        "is_quantitative": True,
        "example": "Rating on a scale of 1-5",
        "url": None,
        "status": "active"
    },
    "5": {
        "code": "5",
        "name": "Qualitative",
        "description": "The indicator is qualitative.",
        "category": "indicator",
        "is_quantitative": False,
        "example": "Description of quality",
        "url": None,
        "status": "active"
    }
}


# =============================================================================
# UNHCR-SPECIFIC RESULT FRAMEWORK
# =============================================================================
# UNHCR's 16 Operational Areas (OA) at the outcome level

UNHCR_RESULT_AREAS: Dict[str, Dict[str, Any]] = {
    "OA1": {
        "code": "OA1",
        "name": "Protection",
        "description": "Ensure that all persons of concern to UNHCR can exercise their rights in a safe and dignified manner",
        "level": "Outcome",
        "category": "protection"
    },
    "OA2": {
        "code": "OA2",
        "name": "Solutions",
        "description": "Persons of concern to UNHCR achieve durable solutions (voluntary repatriation, local integration, resettlement)",
        "level": "Outcome",
        "category": "solutions"
    },
    "OA3": {
        "code": "OA3",
        "name": "Health",
        "description": "Persons of concern to UNHCR have improved health and well-being",
        "level": "Outcome",
        "category": "health"
    },
    "OA4": {
        "code": "OA4",
        "name": "Education",
        "description": "Persons of concern to UNHCR have equitable and inclusive access to quality education",
        "level": "Outcome",
        "category": "education"
    },
    "OA5": {
        "code": "OA5",
        "name": "Livelihoods",
        "description": "Persons of concern to UNHCR have improved self-reliance and economic resilience",
        "level": "Outcome",
        "category": "livelihoods"
    },
    "OA6": {
        "code": "OA6",
        "name": "Shelter and Settlements",
        "description": "Persons of concern to UNHCR live in safe, dignified and appropriate housing and settlements",
        "level": "Outcome",
        "category": "shelter"
    },
    "OA7": {
        "code": "OA7",
        "name": "Water, Sanitation and Hygiene (WASH)",
        "description": "Persons of concern to UNHCR have access to safe water, sanitation and hygiene",
        "level": "Outcome",
        "category": "wash"
    },
    "OA8": {
        "code": "OA8",
        "name": "Food Security",
        "description": "Persons of concern to UNHCR have improved food security and nutrition",
        "level": "Outcome",
        "category": "food"
    },
    "OA9": {
        "code": "OA9",
        "name": "Multi-sector",
        "description": "Multi-sector outcomes that cut across multiple operational areas",
        "level": "Outcome",
        "category": "multi_sector"
    },
    "OA10": {
        "code": "OA10",
        "name": "Leadership, Coordination and Partnerships",
        "description": "UNHCR leads, coordinates and partners effectively for the protection and well-being of persons of concern",
        "level": "Outcome",
        "category": "coordination"
    },
    "OA11": {
        "code": "OA11",
        "name": "Emergency Response",
        "description": "UNHCR responds effectively to emergencies to save lives and protect rights",
        "level": "Outcome",
        "category": "emergency"
    },
    "OA12": {
        "code": "OA12",
        "name": "Advocacy and Legal Protection",
        "description": "UNHCR advocates for the rights of persons of concern and provides legal protection",
        "level": "Outcome",
        "category": "protection"
    },
    "OA13": {
        "code": "OA13",
        "name": "Community Empowerment",
        "description": "Persons of concern to UNHCR are empowered to participate in decisions affecting their lives",
        "level": "Outcome",
        "category": "empowerment"
    },
    "OA14": {
        "code": "OA14",
        "name": "Inclusion",
        "description": "Persons of concern to UNHCR are included in national systems and services",
        "level": "Outcome",
        "category": "inclusion"
    },
    "OA15": {
        "code": "OA15",
        "name": "Gender Equality",
        "description": "UNHCR promotes gender equality and the empowerment of women and girls",
        "level": "Outcome",
        "category": "gender"
    },
    "OA16": {
        "code": "OA16",
        "name": "Age and Diversity",
        "description": "UNHCR ensures that the needs of all persons of concern are addressed, including age and diversity considerations",
        "level": "Outcome",
        "category": "diversity"
    }
}


# =============================================================================
# RESULT ANALYSIS GUIDELINES
# =============================================================================

RESULT_ANALYSIS_GUIDELINES: Dict[str, Any] = {
    "framework_structure": {
        "description": "IATI Results Framework hierarchical structure",
        "levels": {
            "impact": {
                "code": "3",
                "level": "Global",
                "description": "Long-term effects of outcomes, leading to larger, overarching results",
                "example": "Improved life expectancy for refugee populations"
            },
            "outcome": {
                "code": "2",
                "level": "Country/Operation",
                "description": "Results that produce an effect on the overall communities or issues served",
                "example": "Improved access to protection services for refugees in Country X",
                "unhcr_notes": "UNHCR has 16 Operational Areas (OA) at the outcome level"
            },
            "output": {
                "code": "1",
                "level": "Activity",
                "description": "Direct effects of work, what is done, and what communities are reached",
                "example": "Number of refugees provided with shelter kits"
            }
        }
    },
    "best_practices": {
        "bp_1": {
            "title": "Always link indicators to results",
            "description": "Each indicator should be clearly associated with a specific result to maintain traceability",
            "severity": "HIGH"
        },
        "bp_2": {
            "title": "Use consistent disaggregation",
            "description": "Maintain consistent disaggregation dimensions (sex, age, location) across all indicators",
            "severity": "HIGH"
        },
        "bp_3": {
            "title": "Track baseline, target, and actual",
            "description": "For each indicator, track baseline values, targets, and actual achievements",
            "severity": "HIGH"
        },
        "bp_4": {
            "title": "Distinguish quantitative vs qualitative",
            "description": "Clearly identify whether indicators are quantitative (Unit, Percentage, Nominal, Ordinal) or qualitative",
            "severity": "MEDIUM"
        }
    },
    "common_mistakes": {
        "cm_1": {
            "title": "Mixing result types",
            "description": "Aggregating Output-level indicators with Outcome-level indicators without proper context",
            "impact": "Loss of meaning and incorrect analysis",
            "fix": "Always group by result_type before aggregation"
        },
        "cm_2": {
            "title": "Ignoring disaggregation",
            "description": "Analyzing indicator data without considering disaggregation dimensions",
            "impact": "Hides disparities and inequalities",
            "fix": "Always include disaggregation dimensions in analysis"
        },
        "cm_3": {
            "title": "Mismatched periods",
            "description": "Comparing baseline, target, and actual values from different time periods",
            "impact": "Invalid progress calculations",
            "fix": "Ensure all period dates align correctly"
        }
    },
    "progress_calculation": {
        "percentage_formula": "(actual - baseline) / (target - baseline) * 100",
        "deviation_formula": "actual - target",
        "notes": [
            "For percentage-based indicators, use actual percentage value directly",
            "For qualitative indicators, progress is typically narrative-based",
            "For nominal/ordinal indicators, calculate based on scale positions"
        ]
    }
}


# =============================================================================
# DISAGGREGATION DIMENSIONS
# =============================================================================
# Common disaggregation dimensions used in IATI data

COMMON_DISAGGREGATION_DIMENSIONS: Dict[str, Dict[str, Any]] = {
    "sex": {
        "name": "Sex",
        "description": "Biological sex of the population",
        "category": "demographic",
        "common_values": ["Male", "Female", "Other"],
        "is_standard": True
    },
    "age": {
        "name": "Age",
        "description": "Age group of the population",
        "category": "demographic",
        "common_values": ["0-4", "5-11", "12-17", "18-59", "60+", "Children", "Adults", "Elderly"],
        "is_standard": True
    },
    "disability": {
        "name": "Disability",
        "description": "Disability status",
        "category": "demographic",
        "common_values": ["Persons with disabilities", "Persons without disabilities"],
        "is_standard": True
    },
    "population_group": {
        "name": "Population Group",
        "description": "Specific population groups",
        "category": "demographic",
        "common_values": ["Refugees", "Asylum-seekers", "IDPs", "Stateless", "Returnees", "Host community"],
        "is_standard": True
    },
    "location": {
        "name": "Location",
        "description": "Geographic location of the population",
        "category": "geographic",
        "common_values": ["Rural", "Urban", "Camp", "Non-camp", "Specific country/region"],
        "is_standard": True
    },
    "goal": {
        "name": "Goal",
        "description": "UNHCR strategic goal or objective",
        "category": "strategic",
        "common_values": ["Emergency response", "Protection and mixed solutions", "Resilience and self-reliance"],
        "is_unhcr_specific": True
    }
}


# =============================================================================
# MCP RESOURCES
# =============================================================================

@mcp.resource("unhcr://result_types")
async def result_types() -> Dict[str, Dict[str, Any]]:
    """
    Get metadata about IATI result type codes.
    
    Result types classify the level and scope of results in the IATI framework.
    UNHCR uses Output (activity-level), Outcome (country-level), and Impact (global-level) results.
    
    Returns:
        Dictionary mapping result type codes to their metadata including:
        - name: Human-readable name
        - description: Full description of the result type
        - level: Hierarchical level (activity, country/operation, global)
        - unhcr_level: UNHCR-specific level description
        - example: Example of this type of result
        - url: Reference URL (if available)
        - status: Active/inactive status
        
    Example:
        {
            "1": {
                "name": "Output",
                "description": "Results that came about as a direct effect...",
                "level": "activity",
                "unhcr_level": "Short-term deliverables"
            },
            "2": {
                "name": "Outcome",
                "level": "country/operation",
                "unhcr_level": "Medium-term results"
            },
            ...
        }
    """
    return RESULT_TYPE_METADATA


@mcp.resource("unhcr://indicator_measures")
async def indicator_measures() -> Dict[str, Dict[str, Any]]:
    """
    Get metadata about IATI indicator measure codes.
    
    Indicator measures define how an indicator's value is measured.
    Understanding the measure type is critical for correct analysis and aggregation.
    
    Returns:
        Dictionary mapping measure codes to their metadata including:
        - name: Human-readable name
        - description: Full description
        - is_quantitative: Boolean indicating if quantitative
        - example: Example of usage
        - url: Reference URL (if available)
        - status: Active/inactive status
        
    Example:
        {
            "1": {
                "name": "Unit",
                "is_quantitative": true,
                "example": "Number of individuals"
            },
            "2": {
                "name": "Percentage", 
                "is_quantitative": true,
                "example": "Percentage of population with access"
            },
            "5": {
                "name": "Qualitative",
                "is_quantitative": false,
                "example": "Description of quality"
            }
        }
    """
    return INDICATOR_MEASURE_METADATA


@mcp.resource("unhcr://result_areas")
async def result_areas() -> Dict[str, Dict[str, Any]]:
    """
    Get UNHCR's 16 Operational Areas (OA) at the outcome level.
    
    These are UNHCR-specific result areas that categorize outcome-level results.
    Each OA represents a strategic focus area for UNHCR's work.
    
    Returns:
        Dictionary mapping OA codes to their metadata including:
        - name: Operational Area name
        - description: Full description
        - level: Result level (always "Outcome" for OAs)
        - category: Broad category grouping
        
    Example:
        {
            "OA1": {
                "name": "Protection",
                "description": "Ensure that all persons of concern to UNHCR can exercise their rights...",
                "level": "Outcome",
                "category": "protection"
            },
            "OA2": {
                "name": "Solutions",
                "category": "solutions"
            },
            ...
        }
    """
    return UNHCR_RESULT_AREAS


@mcp.resource("unhcr://result_analysis_guidelines")
async def result_analysis_guidelines() -> Dict[str, Any]:
    """
    Get comprehensive guidelines for correctly analyzing IATI result data.
    
    This resource provides essential rules, best practices, common mistakes, and
    formulas for working with IATI result framework data.
    
    Returns:
        Dictionary containing:
        - framework_structure: Hierarchical structure of result types
        - best_practices: Recommended practices for result analysis
        - common_mistakes: Frequently encountered errors and fixes
        - progress_calculation: Formulas and notes for progress tracking
        
    Example:
        {
            "framework_structure": {
                "levels": {
                    "impact": {"code": "3", "level": "Global", ...},
                    "outcome": {"code": "2", "level": "Country/Operation", ...},
                    "output": {"code": "1", "level": "Activity", ...}
                }
            },
            "best_practices": {...},
            "common_mistakes": {...},
            "progress_calculation": {...}
        }
    """
    return RESULT_ANALYSIS_GUIDELINES


@mcp.resource("unhcr://disaggregation_dimensions")
async def disaggregation_dimensions() -> Dict[str, Dict[str, Any]]:
    """
    Get metadata about common disaggregation dimensions used in IATI indicator data.
    
    Disaggregation dimensions allow indicators to be broken down by population
    characteristics, enabling analysis of disparities and ensuring no one is left behind.
    
    Returns:
        Dictionary mapping dimension names to their metadata including:
        - name: Dimension name
        - description: Full description
        - category: Dimension category (demographic, geographic, strategic)
        - common_values: Common values for this dimension
        - is_standard: Whether this is a standard IATI dimension
        - is_unhcr_specific: Whether this is UNHCR-specific
        
    Example:
        {
            "sex": {
                "name": "Sex",
                "category": "demographic",
                "common_values": ["Male", "Female", "Other"],
                "is_standard": true
            },
            "age": {
                "name": "Age",
                "category": "demographic",
                "common_values": ["0-4", "5-11", "12-17", "18-59", "60+"]
            },
            ...
        }
    """
    return COMMON_DISAGGREGATION_DIMENSIONS


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_result_type_name(result_type_code: str) -> str:
    """
    Get the human-readable name for a result type code.
    
    Args:
        result_type_code: The result type code (e.g., "1", "2", "3", "9")
        
    Returns:
        The name of the result type, or "Unknown" if not found.
    """
    return RESULT_TYPE_METADATA.get(result_type_code, {}).get("name", "Unknown")


def get_indicator_measure_name(measure_code: str) -> str:
    """
    Get the human-readable name for an indicator measure code.
    
    Args:
        measure_code: The measure code (e.g., "1", "2", "3", "4", "5")
        
    Returns:
        The name of the measure, or "Unknown" if not found.
    """
    return INDICATOR_MEASURE_METADATA.get(measure_code, {}).get("name", "Unknown")


def is_quantitative_measure(measure_code: str) -> bool:
    """
    Check if an indicator measure is quantitative.
    
    Args:
        measure_code: The measure code to check
        
    Returns:
        True if quantitative (Unit, Percentage, Nominal, Ordinal), False if qualitative.
    """
    return INDICATOR_MEASURE_METADATA.get(measure_code, {}).get("is_quantitative", False)


def calculate_progress_percentage(
    baseline_value: Optional[float],
    target_value: Optional[float],
    actual_value: Optional[float]
) -> Optional[float]:
    """
    Calculate the progress percentage for an indicator.
    
    Formula: (actual - baseline) / (target - baseline) * 100
    
    Args:
        baseline_value: The baseline value
        target_value: The target value
        actual_value: The actual value achieved
        
    Returns:
        The progress percentage, or None if calculation is not possible.
    """
    if baseline_value is None or target_value is None or actual_value is None:
        return None
    
    if target_value == baseline_value:
        # Avoid division by zero
        if actual_value >= target_value:
            return 100.0
        else:
            return 0.0
    
    try:
        progress = ((actual_value - baseline_value) / (target_value - baseline_value)) * 100
        return min(max(progress, 0.0), 100.0)  # Clamp to 0-100 range
    except (TypeError, ZeroDivisionError):
        return None


def calculate_deviation_from_target(
    target_value: Optional[float],
    actual_value: Optional[float]
) -> Optional[float]:
    """
    Calculate the deviation from target for an indicator.
    
    Formula: actual - target
    
    Args:
        target_value: The target value
        actual_value: The actual value achieved
        
    Returns:
        The deviation, or None if calculation is not possible.
    """
    if target_value is None or actual_value is None:
        return None
    
    try:
        return actual_value - target_value
    except TypeError:
        return None


def validate_indicator_data(
    indicator_measure: str,
    baseline_value: Optional[str],
    target_value: Optional[str],
    actual_value: Optional[str]
) -> Dict[str, Any]:
    """
    Validate indicator data for consistency and completeness.
    
    Args:
        indicator_measure: The measure code
        baseline_value: The baseline value
        target_value: The target value
        actual_value: The actual value
        
    Returns:
        Dictionary with validation results including:
        - valid: Whether the data is valid
        - errors: List of error messages
        - warnings: List of warning messages
    """
    errors = []
    warnings = []
    
    # Check measure code
    if indicator_measure not in INDICATOR_MEASURE_METADATA:
        errors.append(f"Invalid measure code: {indicator_measure}")
    
    # Check for quantitative indicators with non-numeric values
    if is_quantitative_measure(indicator_measure):
        for field_name, value in [("baseline", baseline_value), ("target", target_value), ("actual", actual_value)]:
            if value is not None:
                try:
                    float(value)
                except (ValueError, TypeError):
                    errors.append(f"Non-numeric {field_name} value for quantitative indicator: {value}")
    
    # Check if baseline is provided
    if baseline_value is None:
        warnings.append("Missing baseline value")
    
    # Check if target is provided
    if target_value is None:
        warnings.append("Missing target value")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }
