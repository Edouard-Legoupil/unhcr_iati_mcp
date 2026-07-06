"""
Activity model for UNHCR IATI MCP Server.

This module defines the Pydantic model for IATI activity data based on
the actual IATI Datastore schema from UNHCR activities.
"""

from typing import List, Optional, Union, Any

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
