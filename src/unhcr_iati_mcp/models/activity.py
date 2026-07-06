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
    
    # Result framework data
    result_type: Union[str, List[str]] = Field(default_factory=list, description="Result type codes (1=Output, 2=Outcome, 3=Impact, 9=Other)")
    result_title_narrative: Union[str, List[str]] = Field(default_factory=list, description="Result titles")
    result_aggregation_status: Union[bool, List[bool]] = Field(default_factory=list, description="Result aggregation status flags")
    
    # Indicator data
    result_indicator_ref: Union[str, List[str]] = Field(default_factory=list, description="Indicator references")
    result_indicator_title_narrative: Union[str, List[str]] = Field(default_factory=list, description="Indicator titles")
    result_indicator_description_narrative: Union[str, List[str]] = Field(default_factory=list, description="Indicator descriptions")
    result_indicator_measure: Union[str, List[str]] = Field(default_factory=list, description="Indicator measure types (1=Unit, 2=Percentage, 3=Nominal, 4=Ordinal, 5=Qualitative)")
    
    # Indicator baseline data
    result_indicator_baseline_year: Union[int, List[int]] = Field(default_factory=list, description="Baseline years")
    result_indicator_baseline_value: Union[str, List[str]] = Field(default_factory=list, description="Baseline values")
    result_indicator_baseline_location_ref: Union[str, List[str]] = Field(default_factory=list, description="Baseline location references")
    result_indicator_baseline_dimension_name: Union[str, List[str], List[List[str]]] = Field(default_factory=list, description="Baseline disaggregation dimension names")
    result_indicator_baseline_dimension_value: Union[str, List[str], List[List[str]]] = Field(default_factory=list, description="Baseline disaggregation dimension values")
    
    # Indicator target period data
    result_indicator_period_target_value: Union[str, List[str]] = Field(default_factory=list, description="Target period values")
    result_indicator_period_target_location_ref: Union[str, List[str]] = Field(default_factory=list, description="Target period location references")
    result_indicator_period_target_dimension_name: Union[str, List[str], List[List[str]]] = Field(default_factory=list, description="Target period disaggregation dimension names")
    result_indicator_period_target_dimension_value: Union[str, List[str], List[List[str]]] = Field(default_factory=list, description="Target period disaggregation dimension values")
    
    # Indicator actual period data
    result_indicator_period_actual_value: Union[str, List[str]] = Field(default_factory=list, description="Actual period values")
    result_indicator_period_actual_location_ref: Union[str, List[str]] = Field(default_factory=list, description="Actual period location references")
    result_indicator_period_actual_dimension_name: Union[str, List[str], List[List[str]]] = Field(default_factory=list, description="Actual period disaggregation dimension names")
    result_indicator_period_actual_dimension_value: Union[str, List[str], List[List[str]]] = Field(default_factory=list, description="Actual period disaggregation dimension values")
    
    # Indicator period dates
    result_indicator_period_start_iso_date: Union[str, List[str]] = Field(default_factory=list, description="Indicator period start dates")
    result_indicator_period_end_iso_date: Union[str, List[str]] = Field(default_factory=list, description="Indicator period end dates")
    
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
            # Result framework fields
            'result_type',
            'result_title_narrative',
            'result_aggregation_status',
            'result_indicator_ref',
            'result_indicator_title_narrative',
            'result_indicator_description_narrative',
            'result_indicator_measure',
            'result_indicator_baseline_year',
            'result_indicator_baseline_value',
            'result_indicator_baseline_location_ref',
            'result_indicator_baseline_dimension_name',
            'result_indicator_baseline_dimension_value',
            'result_indicator_period_target_value',
            'result_indicator_period_target_location_ref',
            'result_indicator_period_target_dimension_name',
            'result_indicator_period_target_dimension_value',
            'result_indicator_period_actual_value',
            'result_indicator_period_actual_location_ref',
            'result_indicator_period_actual_dimension_name',
            'result_indicator_period_actual_dimension_value',
            'result_indicator_period_start_iso_date',
            'result_indicator_period_end_iso_date',
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
    
    # =============================================================================
    # RESULT FRAMEWORK METHODS
    # =============================================================================
    
    def get_result_info(self) -> List[Dict[str, Any]]:
        """
        Get result information as a list of structured dictionaries.
        
        This method pairs up result_type, result_title_narrative, and
        result_aggregation_status into a list of result info objects.
        
        Returns:
            List of dictionaries containing:
            - result_type: Result type code (1=Output, 2=Outcome, 3=Impact, 9=Other)
            - result_title_narrative: Human-readable result title
            - result_aggregation_status: Whether result values should be aggregated
            - indicator_count: Number of indicators for this result
            
        Note: Results can have multiple indicators. Use get_indicators_by_result()
        to get the indicators for each result.
        """
        result_info = []
        
        types = self.result_type if isinstance(self.result_type, list) else [self.result_type] if self.result_type else []
        titles = self.result_title_narrative if isinstance(self.result_title_narrative, list) else [self.result_title_narrative] if self.result_title_narrative else []
        agg_statuses = self.result_aggregation_status if isinstance(self.result_aggregation_status, list) else [self.result_aggregation_status] if self.result_aggregation_status else []
        
        max_len = max(len(types), len(titles), len(agg_statuses))
        
        for i in range(max_len):
            result_info.append({
                'result_type': types[i] if i < len(types) else None,
                'result_title_narrative': titles[i] if i < len(titles) else None,
                'result_aggregation_status': agg_statuses[i] if i < len(agg_statuses) else None
            })
        
        return [r for r in result_info if any(v is not None for v in r.values())]
    
    def get_indicator_info(self) -> List[Dict[str, Any]]:
        """
        Get indicator information as a list of structured dictionaries.
        
        This method pairs up all indicator-related fields into a list of
        indicator info objects with their baseline, target, and actual values.
        
        Returns:
            List of dictionaries containing:
            - indicator_ref: Unique indicator reference
            - indicator_title_narrative: Human-readable indicator title
            - indicator_description_narrative: Indicator description
            - indicator_measure: Measure type code (1=Unit, 2=Percentage, 3=Nominal, 4=Ordinal, 5=Qualitative)
            - baseline_year: Baseline year
            - baseline_value: Baseline value
            - baseline_location_ref: Baseline location
            - baseline_dimension_name: Baseline disaggregation dimensions
            - baseline_dimension_value: Baseline disaggregation dimension values
            - period_target_value: Target value
            - period_target_location_ref: Target location
            - period_target_dimension_name: Target disaggregation dimensions
            - period_target_dimension_value: Target disaggregation dimension values
            - period_actual_value: Actual value
            - period_actual_location_ref: Actual location
            - period_actual_dimension_name: Actual disaggregation dimensions
            - period_actual_dimension_value: Actual disaggregation dimension values
            - period_start_iso_date: Period start date
            - period_end_iso_date: Period end date
            
        Note: IATI Datastore stores these as separate list fields, so we
        reconstruct the structure by aligning indices.
        """
        indicator_info = []
        
        # Get all indicator fields
        refs = self.result_indicator_ref if isinstance(self.result_indicator_ref, list) else [self.result_indicator_ref] if self.result_indicator_ref else []
        titles = self.result_indicator_title_narrative if isinstance(self.result_indicator_title_narrative, list) else [self.result_indicator_title_narrative] if self.result_indicator_title_narrative else []
        descriptions = self.result_indicator_description_narrative if isinstance(self.result_indicator_description_narrative, list) else [self.result_indicator_description_narrative] if self.result_indicator_description_narrative else []
        measures = self.result_indicator_measure if isinstance(self.result_indicator_measure, list) else [self.result_indicator_measure] if self.result_indicator_measure else []
        
        # Baseline fields
        baseline_years = self.result_indicator_baseline_year if isinstance(self.result_indicator_baseline_year, list) else [self.result_indicator_baseline_year] if self.result_indicator_baseline_year else []
        baseline_values = self.result_indicator_baseline_value if isinstance(self.result_indicator_baseline_value, list) else [self.result_indicator_baseline_value] if self.result_indicator_baseline_value else []
        baseline_locations = self.result_indicator_baseline_location_ref if isinstance(self.result_indicator_baseline_location_ref, list) else [self.result_indicator_baseline_location_ref] if self.result_indicator_baseline_location_ref else []
        baseline_dim_names = self.result_indicator_baseline_dimension_name if isinstance(self.result_indicator_baseline_dimension_name, list) else [self.result_indicator_baseline_dimension_name] if self.result_indicator_baseline_dimension_name else []
        baseline_dim_values = self.result_indicator_baseline_dimension_value if isinstance(self.result_indicator_baseline_dimension_value, list) else [self.result_indicator_baseline_dimension_value] if self.result_indicator_baseline_dimension_value else []
        
        # Target period fields
        target_values = self.result_indicator_period_target_value if isinstance(self.result_indicator_period_target_value, list) else [self.result_indicator_period_target_value] if self.result_indicator_period_target_value else []
        target_locations = self.result_indicator_period_target_location_ref if isinstance(self.result_indicator_period_target_location_ref, list) else [self.result_indicator_period_target_location_ref] if self.result_indicator_period_target_location_ref else []
        target_dim_names = self.result_indicator_period_target_dimension_name if isinstance(self.result_indicator_period_target_dimension_name, list) else [self.result_indicator_period_target_dimension_name] if self.result_indicator_period_target_dimension_name else []
        target_dim_values = self.result_indicator_period_target_dimension_value if isinstance(self.result_indicator_period_target_dimension_value, list) else [self.result_indicator_period_target_dimension_value] if self.result_indicator_period_target_dimension_value else []
        
        # Actual period fields
        actual_values = self.result_indicator_period_actual_value if isinstance(self.result_indicator_period_actual_value, list) else [self.result_indicator_period_actual_value] if self.result_indicator_period_actual_value else []
        actual_locations = self.result_indicator_period_actual_location_ref if isinstance(self.result_indicator_period_actual_location_ref, list) else [self.result_indicator_period_actual_location_ref] if self.result_indicator_period_actual_location_ref else []
        actual_dim_names = self.result_indicator_period_actual_dimension_name if isinstance(self.result_indicator_period_actual_dimension_name, list) else [self.result_indicator_period_actual_dimension_name] if self.result_indicator_period_actual_dimension_name else []
        actual_dim_values = self.result_indicator_period_actual_dimension_value if isinstance(self.result_indicator_period_actual_dimension_value, list) else [self.result_indicator_period_actual_dimension_value] if self.result_indicator_period_actual_dimension_value else []
        
        # Period dates
        period_starts = self.result_indicator_period_start_iso_date if isinstance(self.result_indicator_period_start_iso_date, list) else [self.result_indicator_period_start_iso_date] if self.result_indicator_period_start_iso_date else []
        period_ends = self.result_indicator_period_end_iso_date if isinstance(self.result_indicator_period_end_iso_date, list) else [self.result_indicator_period_end_iso_date] if self.result_indicator_period_end_iso_date else []
        
        max_len = max(
            len(refs), len(titles), len(descriptions), len(measures),
            len(baseline_years), len(baseline_values), len(baseline_locations),
            len(target_values), len(target_locations),
            len(actual_values), len(actual_locations),
            len(period_starts), len(period_ends)
        )
        
        for i in range(max_len):
            indicator_info.append({
                'indicator_ref': refs[i] if i < len(refs) else None,
                'indicator_title_narrative': titles[i] if i < len(titles) else None,
                'indicator_description_narrative': descriptions[i] if i < len(descriptions) else None,
                'indicator_measure': measures[i] if i < len(measures) else None,
                'baseline_year': baseline_years[i] if i < len(baseline_years) else None,
                'baseline_value': baseline_values[i] if i < len(baseline_values) else None,
                'baseline_location_ref': baseline_locations[i] if i < len(baseline_locations) else None,
                'baseline_dimension_name': baseline_dim_names[i] if i < len(baseline_dim_names) else None,
                'baseline_dimension_value': baseline_dim_values[i] if i < len(baseline_dim_values) else None,
                'period_target_value': target_values[i] if i < len(target_values) else None,
                'period_target_location_ref': target_locations[i] if i < len(target_locations) else None,
                'period_target_dimension_name': target_dim_names[i] if i < len(target_dim_names) else None,
                'period_target_dimension_value': target_dim_values[i] if i < len(target_dim_values) else None,
                'period_actual_value': actual_values[i] if i < len(actual_values) else None,
                'period_actual_location_ref': actual_locations[i] if i < len(actual_locations) else None,
                'period_actual_dimension_name': actual_dim_names[i] if i < len(actual_dim_names) else None,
                'period_actual_dimension_value': actual_dim_values[i] if i < len(actual_dim_values) else None,
                'period_start_iso_date': period_starts[i] if i < len(period_starts) else None,
                'period_end_iso_date': period_ends[i] if i < len(period_ends) else None
            })
        
        return [i for i in indicator_info if any(v is not None for v in i.values())]
    
    def get_results_with_indicators(self) -> Dict[str, Any]:
        """
        Get results with their associated indicators.
        
        This is the SAFEST way to work with result/indicator data from an activity,
        as it properly associates indicators with their parent results.
        
        Returns:
            Dictionary with:
            - results: List of result info
            - indicators: List of indicator info
            - results_by_type: Results grouped by type (Output, Outcome, Impact)
            - indicators_by_result: Indicators grouped by result index
            
        Note: The IATI Datastore stores results and indicators as separate
        list fields. This method reconstructs the hierarchy by index.
        """
        results = self.get_result_info()
        indicators = self.get_indicator_info()
        
        # Group indicators by result (assuming 1:n relationship by index)
        indicators_by_result = {}
        for i, indicator in enumerate(indicators):
            # Find the result index for this indicator
            # In IATI, indicators typically follow their parent results
            result_idx = min(i, len(results) - 1) if results else 0
            if result_idx not in indicators_by_result:
                indicators_by_result[result_idx] = []
            indicators_by_result[result_idx].append(indicator)
        
        # Group results by type
        results_by_type = {"1": [], "2": [], "3": [], "9": []}
        for result in results:
            rtype = result.get('result_type', '9')
            if rtype in results_by_type:
                results_by_type[rtype].append(result)
            else:
                results_by_type[rtype] = [result]
        
        return {
            'results': results,
            'indicators': indicators,
            'results_by_type': results_by_type,
            'indicators_by_result': indicators_by_result,
            'total_results': len(results),
            'total_indicators': len(indicators)
        }
    
    def get_indicators_by_type(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get indicators grouped by their result type.
        
        Returns:
            Dictionary mapping result type codes to lists of indicators.
            
        Example:
            {
                "1": [{"indicator_title": "...", ...}],  # Output indicators
                "2": [{"indicator_title": "...", ...}],  # Outcome indicators
                "3": [{"indicator_title": "...", ...}]   # Impact indicators
            }
        """
        results_info = self.get_results_with_indicators()
        results_by_type = results_info['results_by_type']
        indicators_by_result = results_info['indicators_by_result']
        
        indicators_by_type = {"1": [], "2": [], "3": [], "9": []}
        
        for result_idx, result_type in enumerate([r.get('result_type', '9') for r in results_info['results']]):
            if result_idx in indicators_by_result:
                for indicator in indicators_by_result[result_idx]:
                    if result_type in indicators_by_type:
                        indicators_by_type[result_type].append(indicator)
                    else:
                        indicators_by_type[result_type] = [indicator]
        
        return indicators_by_type
    
    def get_quantitative_indicators(self) -> List[Dict[str, Any]]:
        """
        Get only quantitative indicators (Unit, Percentage, Nominal, Ordinal).
        
        Returns:
            List of indicator info dictionaries for quantitative indicators.
        """
        from unhcr_iati_mcp.resources.results import is_quantitative_measure
        
        indicators = self.get_indicator_info()
        quantitative = []
        
        for indicator in indicators:
            measure = indicator.get('indicator_measure')
            if measure and is_quantitative_measure(str(measure)):
                quantitative.append(indicator)
        
        return quantitative
    
    def get_qualitative_indicators(self) -> List[Dict[str, Any]]:
        """
        Get only qualitative indicators.
        
        Returns:
            List of indicator info dictionaries for qualitative indicators.
        """
        indicators = self.get_indicator_info()
        qualitative = []
        
        for indicator in indicators:
            measure = indicator.get('indicator_measure')
            if measure and measure == "5":
                qualitative.append(indicator)
        
        return qualitative
    
    def has_results_framework(self) -> bool:
        """
        Check if this activity has results framework data.
        
        Returns:
            True if the activity has any result or indicator data, False otherwise.
        """
        return (
            len(self.get_result_info()) > 0 or
            len(self.get_indicator_info()) > 0
        )


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
