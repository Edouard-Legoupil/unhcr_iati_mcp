"""
Sector models for UNHCR IATI MCP Server.

This module defines Pydantic models for sector-related data, including
comprehensive sector information with vocabulary metadata to prevent
incorrect cross-vocabulary aggregation.
"""

from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class SectorInfo(BaseModel):
    """
    Represents a single sector classification for an activity.
    
    Contains the sector code, its human-readable name, the vocabulary it belongs to,
    and the percentage allocation. This structure is essential for preventing
    cross-vocabulary aggregation errors.
    """
    sector_code: str = Field(..., description="The sector code (e.g., '10', '111', '72010')")
    sector_narrative: str = Field(..., description="Human-readable sector name")
    sector_vocabulary: str = Field(..., description="Vocabulary code (e.g., '98' for UNHCR-specific)")
    sector_percentage: float = Field(..., description="Percentage allocation for this sector")
    
    @property
    def is_unhcr_vocabulary(self) -> bool:
        """Check if this sector uses UNHCR's primary vocabulary (98)."""
        from unhcr_iati_mcp.resources.sectors import SECTOR_VOCABULARY_METADATA
        return SECTOR_VOCABULARY_METADATA.get(self.sector_vocabulary, {}).get("is_unhcr_primary", False)
    
    @property
    def vocabulary_name(self) -> str:
        """Get the human-readable name for this sector's vocabulary."""
        from unhcr_iati_mcp.resources.sectors import SECTOR_VOCABULARY_METADATA
        return SECTOR_VOCABULARY_METADATA.get(self.sector_vocabulary, {}).get("name", "Unknown")


class SectorSummary(BaseModel):
    """
    Summary of sector data for a single sector code within a single vocabulary.
    
    This model is used for aggregated sector analysis and includes critical
    metadata to prevent cross-vocabulary aggregation errors.
    """
    sector_code: str = Field(..., description="The sector code")
    sector_vocabulary: str = Field(..., description="The vocabulary this sector belongs to")
    sector_narrative: Optional[str] = Field(None, description="Human-readable sector name")
    
    activity_count: int = Field(..., description="Number of activities with this sector")
    total_budget: float = Field(..., description="Total budget allocated to this sector")
    average_percentage: Optional[float] = Field(None, description="Average percentage allocation")
    
    @property
    def vocabulary_name(self) -> str:
        """Get the human-readable name for this sector's vocabulary."""
        from unhcr_iati_mcp.resources.sectors import SECTOR_VOCABULARY_METADATA
        return SECTOR_VOCABULARY_METADATA.get(self.sector_vocabulary, {}).get("name", "Unknown")


class SectorVocabularySummary(BaseModel):
    """
    Summary of sector data grouped by vocabulary.
    
    This is the safest way to present sector analysis data, as it prevents
    mixing of codes from different vocabularies.
    """
    vocabulary_code: str = Field(..., description="The vocabulary code (e.g., '98')")
    vocabulary_name: str = Field(..., description="Human-readable vocabulary name")
    sectors: List[SectorSummary] = Field(default_factory=list, description="List of sector summaries for this vocabulary")
    total_activities: int = Field(..., description="Total number of activities in this vocabulary")
    total_budget: float = Field(..., description="Total budget across all sectors in this vocabulary")


class SectorAnalysisResult(BaseModel):
    """
    Complete sector analysis result with vocabulary separation.
    
    This model ensures that sector data is always presented with vocabulary
    context, preventing incorrect aggregation.
    """
    by_vocabulary: Dict[str, SectorVocabularySummary] = Field(
        default_factory=dict,
        description="Sector data grouped by vocabulary"
    )
    total_activities: int = Field(..., description="Total number of activities analyzed")
    total_budget: float = Field(..., description="Total budget across all vocabularies")
    warning: str = Field(
        default="NEVER aggregate across vocabularies - each vocabulary uses a different classification system",
        description="Critical warning about cross-vocabulary aggregation"
    )


class SectorValidationResult(BaseModel):
    """
    Result of validating sector aggregation for correctness.
    
    Used to check if planned sector aggregations would violate the
    cross-vocabulary aggregation rule.
    """
    valid: bool = Field(..., description="Whether the aggregation is valid")
    vocabulary: Optional[str] = Field(None, description="The single vocabulary being used (if valid)")
    error: Optional[str] = Field(None, description="Error message if invalid")
    severity: Optional[str] = Field(None, description="Severity level (ERROR, CRITICAL, WARNING)")
    recommendation: Optional[str] = Field(None, description="Recommended fix for invalid aggregations")
    message: Optional[str] = Field(None, description="Success message if valid")


class CrossVocabularySectorPair(BaseModel):
    """
    Represents a pair of sector codes from different vocabularies that should NOT be aggregated.
    
    Used for documenting and preventing common cross-vocabulary mistakes.
    """
    sector_code: str = Field(..., description="The sector code")
    vocabulary_a: str = Field(..., description="First vocabulary code")
    vocabulary_b: str = Field(..., description="Second vocabulary code")
    name_a: str = Field(..., description="Name in vocabulary A")
    name_b: str = Field(..., description="Name in vocabulary B")
    warning: str = Field(
        default="These codes have different meanings in different vocabularies",
        description="Warning about mixing these codes"
    )