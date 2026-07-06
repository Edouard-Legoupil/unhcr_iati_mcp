"""
Result and Indicator models for UNHCR IATI MCP Server.

This module defines Pydantic models for IATI result framework data,
including results, indicators, and their period data (baselines, targets, actuals).

The IATI result framework includes:
- Results: Output, Outcome, Impact levels
- Indicators: Measurable metrics within results
- Periods: Time-bound measurements (baseline, target, actual)
- Dimensions: Disaggregation dimensions (sex, age, location, etc.)

UNHCR's Results Framework:
- Impact: Long-term outcomes (global level)
- Outcome: Medium-term results (country/operation level) - 16 OA areas
- Output: Short-term deliverables (activity level)
"""

from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


# =============================================================================
# RESULT TYPE CODES
# =============================================================================
# From codeResultType.RData:
# 1: Output - Results that came about as a direct effect
# 2: Outcome - Results that produce an effect on communities
# 3: Impact - Long term effects of outcomes
# 9: Other - Another type of result

RESULT_TYPE_CODES: Dict[str, str] = {
    "1": "Output",
    "2": "Outcome", 
    "3": "Impact",
    "9": "Other"
}


# =============================================================================
# INDICATOR MEASURE CODES
# =============================================================================
# From codeIndicatorMeasure.RData:
# 1: Unit - The indicator is measured in units
# 2: Percentage - The indicator is measured in percentages
# 3: Nominal - Quantitative nominal scale
# 4: Ordinal - Quantitative ordinal scale
# 5: Qualitative - The indicator is qualitative

INDICATOR_MEASURE_CODES: Dict[str, str] = {
    "1": "Unit",
    "2": "Percentage",
    "3": "Nominal",
    "4": "Ordinal",
    "5": "Qualitative"
}


# =============================================================================
# RESULT MODELS
# =============================================================================

class Result(BaseModel):
    """
    Represents a single result within an IATI activity.
    
    Results are classified by type (Output, Outcome, Impact) and contain
    indicators that measure progress toward the result.
    """
    result_type: str = Field(..., description="Result type code (1=Output, 2=Outcome, 3=Impact, 9=Other)")
    result_title_narrative: str = Field(..., description="Human-readable title of the result")
    result_aggregation_status: Optional[bool] = Field(None, description="Whether result values should be aggregated")
    
    @property
    def result_type_name(self) -> str:
        """Get the human-readable name for the result type."""
        return RESULT_TYPE_CODES.get(self.result_type, "Unknown")


class ResultSummary(BaseModel):
    """
    Summary of a result with aggregated indicator information.
    """
    result_type: str = Field(..., description="Result type code")
    result_title: str = Field(..., description="Result title")
    result_type_name: str = Field(..., description="Human-readable result type name")
    
    indicator_count: int = Field(..., description="Number of indicators for this result")
    baseline_value: Optional[str] = Field(None, description="Baseline value")
    target_value: Optional[str] = Field(None, description="Target value")
    actual_value: Optional[str] = Field(None, description="Actual value achieved")
    
    progress_percentage: Optional[float] = Field(None, description="Percentage of target achieved")
    deviation_from_target: Optional[float] = Field(None, description="Difference from target")


# =============================================================================
# INDICATOR MODELS
# =============================================================================

class Indicator(BaseModel):
    """
    Represents a single indicator within a result.
    
    Indicators are measurable metrics that track progress toward a result.
    Each indicator has a measure type (Unit, Percentage, Nominal, Ordinal, Qualitative)
    and can have baseline, target, and actual values.
    """
    indicator_ref: Optional[str] = Field(None, description="Unique reference for the indicator")
    indicator_title_narrative: str = Field(..., description="Human-readable title of the indicator")
    indicator_description_narrative: Optional[str] = Field(None, description="Description of the indicator")
    indicator_measure: str = Field(..., description="Measure type code (1=Unit, 2=Percentage, 3=Nominal, 4=Ordinal, 5=Qualitative)")
    
    # Baseline data
    baseline_year: Optional[int] = Field(None, description="Year of baseline measurement")
    baseline_value: Optional[str] = Field(None, description="Baseline value")
    baseline_location_ref: Optional[str] = Field(None, description="Location reference for baseline")
    baseline_dimension_name: Optional[List[str]] = Field(default_factory=list, description="Disaggregation dimension names for baseline")
    baseline_dimension_value: Optional[List[str]] = Field(default_factory=list, description="Disaggregation dimension values for baseline")
    
    # Target period data
    period_target_value: Optional[str] = Field(None, description="Target value")
    period_target_location_ref: Optional[str] = Field(None, description="Location reference for target")
    period_target_dimension_name: Optional[List[str]] = Field(default_factory=list, description="Disaggregation dimension names for target")
    period_target_dimension_value: Optional[List[str]] = Field(default_factory=list, description="Disaggregation dimension values for target")
    
    # Actual period data
    period_actual_value: Optional[str] = Field(None, description="Actual value achieved")
    period_actual_location_ref: Optional[str] = Field(None, description="Location reference for actual")
    period_actual_dimension_name: Optional[List[str]] = Field(default_factory=list, description="Disaggregation dimension names for actual")
    period_actual_dimension_value: Optional[List[str]] = Field(default_factory=list, description="Disaggregation dimension values for actual")
    
    # Period dates
    period_start_iso_date: Optional[str] = Field(None, description="Period start date (ISO format)")
    period_end_iso_date: Optional[str] = Field(None, description="Period end date (ISO format)")
    
    @property
    def indicator_measure_name(self) -> str:
        """Get the human-readable name for the indicator measure."""
        return INDICATOR_MEASURE_CODES.get(self.indicator_measure, "Unknown")
    
    @property
    def is_quantitative(self) -> bool:
        """Check if this is a quantitative indicator."""
        return self.indicator_measure in ["1", "2", "3", "4"]
    
    @property
    def is_qualitative(self) -> bool:
        """Check if this is a qualitative indicator."""
        return self.indicator_measure == "5"
    
    @property
    def is_percentage(self) -> bool:
        """Check if this indicator is measured in percentages."""
        return self.indicator_measure == "2"


class IndicatorSummary(BaseModel):
    """
    Summary of an indicator with aggregated data.
    """
    indicator_ref: Optional[str] = Field(None, description="Indicator reference")
    indicator_title: str = Field(..., description="Indicator title")
    indicator_measure: str = Field(..., description="Measure type code")
    indicator_measure_name: str = Field(..., description="Measure type name")
    
    baseline_value: Optional[str] = Field(None, description="Baseline value")
    baseline_year: Optional[int] = Field(None, description="Baseline year")
    
    target_value: Optional[str] = Field(None, description="Target value")
    actual_value: Optional[str] = Field(None, description="Actual value")
    
    progress_percentage: Optional[float] = Field(None, description="Percentage of target achieved")
    deviation_from_target: Optional[float] = Field(None, description="Difference from target")
    
    period_start: Optional[str] = Field(None, description="Period start date")
    period_end: Optional[str] = Field(None, description="Period end date")
    location: Optional[str] = Field(None, description="Location reference")


class IndicatorPeriod(BaseModel):
    """
    Represents a single period measurement for an indicator.
    
    Periods can be baseline, target, or actual measurements.
    """
    period_type: str = Field(..., description="Type of period (baseline, target, actual)")
    year: Optional[int] = Field(None, description="Year of measurement")
    value: Optional[str] = Field(None, description="Measured value")
    location_ref: Optional[str] = Field(None, description="Location reference")
    
    # Disaggregation dimensions
    dimension_name: Optional[List[str]] = Field(default_factory=list, description="Dimension names")
    dimension_value: Optional[List[str]] = Field(default_factory=list, description="Dimension values")
    
    # For target/actual periods
    start_iso_date: Optional[str] = Field(None, description="Period start date")
    end_iso_date: Optional[str] = Field(None, description="Period end date")


# =============================================================================
# DIMENSION MODELS
# =============================================================================

class Dimension(BaseModel):
    """
    Represents a disaggregation dimension for an indicator.
    
    Dimensions allow indicators to be broken down by characteristics like
    sex, age, location, disability status, etc.
    """
    name: str = Field(..., description="Dimension name (e.g., 'Sex', 'Age', 'Location')")
    value: str = Field(..., description="Dimension value (e.g., 'Female', '18-24', 'Argentina')")


class DimensionGroup(BaseModel):
    """
    Represents a complete set of disaggregation dimensions for a measurement.
    """
    dimensions: List[Dimension] = Field(default_factory=list, description="List of dimension name-value pairs")
    
    @property
    def as_dict(self) -> Dict[str, str]:
        """Convert to dictionary format."""
        return {d.name: d.value for d in self.dimensions}


# =============================================================================
# AGGREGATED RESULT MODELS
# =============================================================================

class ResultFrameworkSummary(BaseModel):
    """
    Summary of the complete results framework for an activity or set of activities.
    
    Organizes results and indicators by type (Output, Outcome, Impact).
    """
    outputs: List[ResultSummary] = Field(default_factory=list, description="Output-level results")
    outcomes: List[ResultSummary] = Field(default_factory=list, description="Outcome-level results")
    impacts: List[ResultSummary] = Field(default_factory=list, description="Impact-level results")
    others: List[ResultSummary] = Field(default_factory=list, description="Other results")
    
    total_indicators: int = Field(..., description="Total number of indicators")
    total_quantitative: int = Field(..., description="Number of quantitative indicators")
    total_qualitative: int = Field(..., description="Number of qualitative indicators")
    
    @property
    def all_results(self) -> List[ResultSummary]:
        """Get all results combined."""
        return self.outputs + self.outcomes + self.impacts + self.others


class ResultIndicatorAnalysis(BaseModel):
    """
    Comprehensive analysis of result indicators with progress tracking.
    """
    activity_id: str = Field(..., description="Activity identifier")
    result_type: str = Field(..., description="Result type code")
    result_title: str = Field(..., description="Result title")
    
    indicators: List[IndicatorSummary] = Field(default_factory=list, description="List of indicator summaries")
    
    average_progress: Optional[float] = Field(None, description="Average progress percentage across indicators")
    on_track_count: int = Field(..., description="Number of indicators on track")
    off_track_count: int = Field(..., description="Number of indicators off track")
    completed_count: int = Field(..., description="Number of indicators completed")
    
    baseline_year: Optional[int] = Field(None, description="Baseline year")
    reporting_period: Optional[str] = Field(None, description="Reporting period")


# =============================================================================
# VALIDATION MODELS
# =============================================================================

class ResultValidationResult(BaseModel):
    """
    Result of validating result/indicator data.
    """
    valid: bool = Field(..., description="Whether the data is valid")
    errors: List[str] = Field(default_factory=list, description="List of validation errors")
    warnings: List[str] = Field(default_factory=list, description="List of validation warnings")
    
    missing_fields: List[str] = Field(default_factory=list, description="Missing required fields")
    inconsistent_data: List[str] = Field(default_factory=list, description="Inconsistent data issues")


# =============================================================================
# UNHCR-SPECIFIC MODELS
# =============================================================================

class UNHCRResultArea(BaseModel):
    """
    UNHCR-specific result area information.
    
    UNHCR has 16 Operational Areas (OA) at the outcome level.
    """
    code: str = Field(..., description="UNHCR result area code")
    name: str = Field(..., description="Result area name")
    description: Optional[str] = Field(None, description="Result area description")
    
    # Links to indicators
    indicators: List[str] = Field(default_factory=list, description="List of indicator references")


class UNHCRIndicator(BaseModel):
    """
    UNHCR-specific indicator with additional metadata.
    """
    ref: str = Field(..., description="Indicator reference")
    title: str = Field(..., description="Indicator title")
    measure: str = Field(..., description="Measure type code")
    
    # UNHCR-specific fields
    result_area: Optional[str] = Field(None, description="UNHCR result area code")
    outcome_area: Optional[str] = Field(None, description="UNHCR outcome area code")
    
    baseline: Optional[str] = Field(None, description="Baseline value")
    target: Optional[str] = Field(None, description="Target value")
    actual: Optional[str] = Field(None, description="Actual value")
