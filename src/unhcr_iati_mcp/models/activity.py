"""
Activity model for UNHCR IATI MCP Server.

This module defines the Pydantic model for IATI activity data based on
the actual IATI Datastore schema from UNHCR activities.
"""

from typing import List, Optional, Union, Any, Dict

from pydantic import BaseModel, Field, model_validator


class Activity(BaseModel):
    """
    Represents an IATI activity (project/programme).
    
    Based on actual IATI Datastore schema. Uses Union types for fields
    that can be either strings or lists.
    """
    
    # Core identifiers
    iati_identifier: str = Field(..., description="Unique IATI identifier for the activity")
    iati_identifier_exact: Optional[Union[str, List[str]]] = Field(None, description="Exact IATI identifier")
    id: Optional[str] = Field(None, description="Internal document ID")
    
    # Titles and descriptions
    title_narrative: Union[str, List[str]] = Field(default_factory=list, description="Activity titles in multiple languages")
    description_narrative: Union[str, List[str]] = Field(default_factory=list, description="Activity descriptions")
    
    # Reporting organization
    reporting_org_ref: Union[str, List[str]] = Field(default_factory=list, description="Reporting organization references")
    reporting_org_type: Optional[str] = Field(None, description="Reporting organization type code")
    reporting_org_narrative: Union[str, List[str]] = Field(default_factory=list, description="Reporting organization names")
    
    # Recipient countries
    recipient_country_code: Union[str, List[str]] = Field(default_factory=list, description="Recipient country codes (ISO3)")
    
    # Sector information
    sector_code: Union[str, List[str]] = Field(default_factory=list, description="Sector codes")
    sector_narrative: Union[str, List[str]] = Field(default_factory=list, description="Sector narratives")
    sector_vocabulary: Union[str, List[str]] = Field(default_factory=list, description="Sector vocabulary codes")
    sector_percentage: Union[float, List[float]] = Field(default_factory=list, description="Sector percentage allocations")
    
    # Status and dates
    activity_status_code: Optional[str] = Field(None, description="Activity status code")
    activity_scope_code: Optional[str] = Field(None, description="Activity scope code")
    activity_date_iso_date: Union[str, List[str]] = Field(default_factory=list, description="Activity dates in ISO format")
    activity_date_type: Union[str, List[str]] = Field(default_factory=list, description="Activity date type codes")
    
    # Budget information
    budget_value: Union[float, List[float]] = Field(default_factory=list, description="Budget values")
    budget_value_currency: Union[str, List[str]] = Field(default_factory=list, description="Budget currency codes")
    budget_value_value_date: Union[str, List[str]] = Field(default_factory=list, description="Budget value dates")
    budget_period_start_iso_date: Union[str, List[str]] = Field(default_factory=list, description="Budget period start dates")
    budget_period_end_iso_date: Union[str, List[str]] = Field(default_factory=list, description="Budget period end dates")
    capital_spend_percentage: Optional[float] = Field(None, description="Capital spending percentage")
    
    # Humanitarian information
    humanitarian: Optional[bool] = Field(None, description="Humanitarian flag")
    humanitarian_scope_type: Union[str, List[str]] = Field(default_factory=list, description="Humanitarian scope types")
    humanitarian_scope_code: Union[str, List[str]] = Field(default_factory=list, description="Humanitarian scope codes")
    humanitarian_scope_narrative: Union[str, List[str]] = Field(default_factory=list, description="Humanitarian scope narratives")
    humanitarian_scope_vocabulary: Union[str, List[str]] = Field(default_factory=list, description="Humanitarian scope vocabularies")
    
    # Default values
    default_currency: Optional[str] = Field(None, description="Default currency code")
    default_aid_type_code: Union[str, List[str]] = Field(default_factory=list, description="Default aid type codes")
    default_finance_type_code: Optional[str] = Field(None, description="Default finance type code")
    default_flow_type_code: Optional[str] = Field(None, description="Default flow type code")
    default_tied_status_code: Optional[str] = Field(None, description="Default tied status code")
    
    # Metadata
    hierarchy: Optional[int] = Field(None, description="Activity hierarchy level")
    dataset_version: Optional[str] = Field(None, description="IATI dataset version")
    last_updated_datetime: Optional[str] = Field(None, description="Last update datetime")
    indexed_datetime: Optional[str] = Field(None, description="Indexed datetime")
    xml_lang: Optional[str] = Field(None, description="Default XML language")
    
    # Internal datastore fields
    version: Optional[int] = Field(None, alias="_version_", description="Internal version number")
    
    @model_validator(mode='before')
    @classmethod
    def _convert_fields_to_lists(cls, data: Any) -> Any:
        """Convert string fields to lists where the model expects lists."""
        if not isinstance(data, dict):
            return data
        
        # List of fields that should be lists but might be strings in the input
        list_fields = [
            # Note: iati_identifier_exact is Optional[str], not a list
            'title_narrative',
            'description_narrative',
            'reporting_org_ref',
            'reporting_org_narrative',
            'recipient_country_code',
            'sector_code',
            'sector_narrative',
            'sector_vocabulary',
            'sector_percentage',
            'activity_date_iso_date',
            'activity_date_type',
            'budget_value',
            'budget_value_currency',
            'budget_value_value_date',
            'budget_period_start_iso_date',
            'budget_period_end_iso_date',
            'default_aid_type_code',
            'humanitarian_scope_type',
            'humanitarian_scope_code',
            'humanitarian_scope_narrative',
            'humanitarian_scope_vocabulary',
            'participating_org_ref',
            'participating_org_type',
            'participating_org_role',
            'participating_org_narrative',
            'contact_info_type',
            'contact_info_email',
            'contact_info_website',
            'document_link_url',
            'document_link_format',
            'document_link_title_narrative',
            'related_activity_ref',
            'related_activity_type',
        ]
        
        # Remove fields that should NOT be lists
        
        result = dict(data)
        for field in list_fields:
            if field in result and result[field] is not None and not isinstance(result[field], list):
                result[field] = [result[field]]
        
        return result
    
    def get_sector_info(self) -> List[Dict[str, Any]]:
        """
        Get sector information as a list of structured dictionaries.
        
        This method pairs up sector_code, sector_narrative, sector_vocabulary,
        and sector_percentage into a list of sector info objects.
        
        Returns:
            List of dictionaries containing:
            - sector_code: The sector code
            - sector_narrative: The human-readable sector name
            - sector_vocabulary: The vocabulary code
            - sector_percentage: The percentage allocation
            
        CRITICAL: This data spans multiple vocabularies. NEVER aggregate
        across vocabularies without filtering first.
        """
        sector_info = []
        
        # Get the lengths of each list
        codes = self.sector_code if isinstance(self.sector_code, list) else [self.sector_code] if self.sector_code else []
        narratives = self.sector_narrative if isinstance(self.sector_narrative, list) else [self.sector_narrative] if self.sector_narrative else []
        vocabularies = self.sector_vocabulary if isinstance(self.sector_vocabulary, list) else [self.sector_vocabulary] if self.sector_vocabulary else []
        percentages = self.sector_percentage if isinstance(self.sector_percentage, list) else [self.sector_percentage] if self.sector_percentage else []
        
        # Determine the maximum length
        max_len = max(len(codes), len(narratives), len(vocabularies), len(percentages))
        
        for i in range(max_len):
            sector_info.append({
                'sector_code': codes[i] if i < len(codes) else None,
                'sector_narrative': narratives[i] if i < len(narratives) else None,
                'sector_vocabulary': vocabularies[i] if i < len(vocabularies) else None,
                'sector_percentage': percentages[i] if i < len(percentages) else None
            })
        
        # Filter out entries with None for all fields
        return [s for s in sector_info if any(v is not None for v in s.values())]
    
    def get_sectors_by_vocabulary(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get sector information grouped by vocabulary.
        
        This is the SAFEST way to work with sector data from an activity,
        as it prevents mixing codes from different vocabularies.
        
        Returns:
            Dictionary mapping vocabulary codes to lists of sector info
            for that vocabulary.
            
        Example:
            {
                "98": [
                    {"sector_code": "10", "sector_narrative": "Protection", "sector_percentage": 40.0},
                    {"sector_code": "111", "sector_narrative": "Law and Policy", "sector_percentage": 10.0}
                ],
                "10": [
                    {"sector_code": "1", "sector_narrative": "Protection Cluster", "sector_percentage": 50.0}
                ]
            }
        """
        sectors_by_vocab = {}
        
        for sector in self.get_sector_info():
            vocab = sector.get('sector_vocabulary')
            if vocab is None:
                # Use a special key for sectors without vocabulary
                vocab = "__unknown__"
            
            if vocab not in sectors_by_vocab:
                sectors_by_vocab[vocab] = []
            sectors_by_vocab[vocab].append(sector)
        
        return sectors_by_vocab
    
    def get_unhcr_sectors(self) -> List[Dict[str, Any]]:
        """
        Get only UNHCR-specific sectors (vocabulary 98) from this activity.
        
        UNHCR's primary sector classification uses vocabulary 98.
        This method filters to only those sectors.
        
        Returns:
            List of sector info dictionaries for UNHCR-specific sectors.
        """
        return self.get_sectors_by_vocabulary().get("98", [])
    
    def has_mixed_vocabularies(self) -> bool:
        """
        Check if this activity has sectors from multiple vocabularies.
        
        Returns:
            True if the activity has sectors from more than one vocabulary,
            False otherwise.
        """
        vocabularies = self.get_sectors_by_vocabulary().keys()
        return len(vocabularies) > 1
    
    def validate_sector_aggregation(self, target_vocabulary: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate if sector data from this activity can be safely aggregated.
        
        Args:
            target_vocabulary: Optional specific vocabulary to check against.
                            If None, checks if all sectors are from a single vocabulary.
        
        Returns:
            Dictionary with validation result including:
            - valid: Whether aggregation is safe
            - vocabularies: List of vocabularies present
            - error: Error message if invalid
            - recommendation: Suggested fix
        """
        from unhcr_iati_mcp.resources.sectors import SECTOR_VOCABULARY_METADATA
        
        sectors_by_vocab = self.get_sectors_by_vocabulary()
        vocabularies = list(sectors_by_vocab.keys())
        
        # Remove the unknown vocabulary marker
        vocabularies = [v for v in vocabularies if v != "__unknown__"]
        
        if not vocabularies:
            return {
                'valid': True,
                'vocabularies': [],
                'message': 'No sectors with known vocabularies'
            }
        
        if target_vocabulary:
            # Check if all sectors are from the target vocabulary
            if len(vocabularies) == 1 and vocabularies[0] == target_vocabulary:
                return {
                    'valid': True,
                    'vocabularies': vocabularies,
                    'message': f'All sectors are from vocabulary {target_vocabulary}'
                }
            else:
                return {
                    'valid': False,
                    'vocabularies': vocabularies,
                    'error': f'Activity has sectors from vocabularies {vocabularies}, cannot aggregate with target {target_vocabulary}',
                    'severity': 'CRITICAL',
                    'recommendation': f'Filter to only sectors from vocabulary {target_vocabulary} before aggregation'
                }
        
        # Check if all sectors are from a single vocabulary
        if len(vocabularies) == 1:
            vocab_code = vocabularies[0]
            vocab_name = SECTOR_VOCABULARY_METADATA.get(vocab_code, {}).get('name', vocab_code)
            return {
                'valid': True,
                'vocabularies': vocabularies,
                'vocabulary_name': vocab_name,
                'message': f'All sectors are from vocabulary {vocab_code} ({vocab_name})'
            }
        
        # Multiple vocabularies - cannot safely aggregate without filtering
        vocab_names = [SECTOR_VOCABULARY_METADATA.get(v, {}).get('name', v) for v in vocabularies]
        return {
            'valid': False,
            'vocabularies': vocabularies,
            'vocabulary_names': vocab_names,
            'error': f'Activity has sectors from multiple vocabularies: {vocab_names}',
            'severity': 'CRITICAL',
            'recommendation': 'Filter to a single vocabulary before aggregation. For UNHCR analysis, use vocabulary 98.'
        }


class ActivitySummary(BaseModel):
    """
    Simplified Activity model for summaries and listings.
    
    Contains the most commonly used fields from IATI activity data.
    """
    iati_identifier: str = Field(..., description="Unique IATI identifier")
    iati_identifier_exact: Optional[str] = Field(None, description="Exact IATI identifier")
    title_narrative: Union[str, List[str]] = Field(default_factory=list, description="Activity titles")
    description_narrative: Union[str, List[str]] = Field(default_factory=list, description="Activity descriptions")
    reporting_org_ref: Union[str, List[str]] = Field(default_factory=list, description="Reporting organization references")
    recipient_country_code: Union[str, List[str]] = Field(default_factory=list, description="Recipient country codes")
    sector_code: Union[str, List[str]] = Field(default_factory=list, description="Sector codes")
    activity_status_code: Optional[str] = Field(None, description="Activity status code")
    activity_date_iso_date: Union[str, List[str]] = Field(default_factory=list, description="Activity dates")
    budget_value: Union[float, List[float]] = Field(default_factory=list, description="Budget values")
    budget_value_currency: Union[str, List[str]] = Field(default_factory=list, description="Budget currencies")
    humanitarian: Optional[bool] = Field(None, description="Humanitarian flag")
    hierarchy: Optional[int] = Field(None, description="Activity hierarchy level")
    last_updated_datetime: Optional[str] = Field(None, description="Last update datetime")
