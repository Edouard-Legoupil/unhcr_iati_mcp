"""
Budget model for UNHCR IATI MCP Server.

This module defines the Pydantic model for IATI budget data.
"""

from typing import List, Optional, Union, Any

from pydantic import BaseModel, Field, model_validator


class Budget(BaseModel):
    """
    Represents an IATI budget (planned financial allocation).
    
    Based on actual IATI Datastore schema.
    """
    
    # Core identifiers
    iati_identifier: Optional[str] = Field(None, description="Linked activity identifier")
    id: Optional[str] = Field(None, description="Internal document ID")
    
    # Budget values
    budget_value: Union[float, List[float]] = Field(default_factory=list, description="Budget values")
    budget_value_currency: Union[str, List[str]] = Field(default_factory=list, description="Currency codes for budget values")
    budget_value_value_date: Union[str, List[str]] = Field(default_factory=list, description="Value dates for budget values")
    
    # Budget type
    budget_type: Optional[str] = Field(None, description="Budget type code")
    budget_type_vocabulary: Optional[str] = Field(None, description="Budget type vocabulary")
    
    # Budget periods
    budget_period_start_iso_date: Union[str, List[str]] = Field(default_factory=list, description="Budget period start dates")
    budget_period_end_iso_date: Union[str, List[str]] = Field(default_factory=list, description="Budget period end dates")
    
    # Budget lines
    budget_line_ref: Union[str, List[str]] = Field(default_factory=list, description="Budget line references")
    budget_line_narrative: Union[str, List[str]] = Field(default_factory=list, description="Budget line descriptions")
    
    # Reporting organization
    reporting_org_ref: Optional[str] = Field(None, description="Reporting organization reference")
    reporting_org_narrative: Union[str, List[str]] = Field(default_factory=list, description="Reporting organization names")
    
    # Internal datastore fields
    version: Optional[int] = Field(None, alias="_version_", description="Internal version number")
    
    @model_validator(mode='before')
    @classmethod
    def _convert_fields_to_lists(cls, data: Any) -> Any:
        """Convert string fields to lists where the model expects lists."""
        if not isinstance(data, dict):
            return data
        
        list_fields = [
            # Note: iati_identifier is Optional[str], not a list
            'budget_value',
            'budget_value_currency',
            'budget_value_value_date',
            'budget_type',
            'budget_type_vocabulary',
            'budget_period_start_iso_date',
            'budget_period_end_iso_date',
            'budget_line_ref',
            'budget_line_narrative',
            'reporting_org_ref',
            'reporting_org_narrative',
        ]
        
        result = dict(data)
        for field in list_fields:
            if field in result and result[field] is not None and not isinstance(result[field], list):
                result[field] = [result[field]]
        
        return result


class BudgetSummary(BaseModel):
    """
    Simplified Budget model for summaries and listings.
    """
    iati_identifier: Optional[str] = Field(None, description="Linked activity identifier")
    budget_value: Union[float, List[float]] = Field(default_factory=list, description="Budget values")
    budget_value_currency: Union[str, List[str]] = Field(default_factory=list, description="Budget currencies")
    budget_period_start_iso_date: Union[str, List[str]] = Field(default_factory=list, description="Budget period start dates")
    budget_period_end_iso_date: Union[str, List[str]] = Field(default_factory=list, description="Budget period end dates")
    budget_type: Optional[str] = Field(None, description="Budget type code")
    reporting_org_ref: Optional[str] = Field(None, description="Reporting organization reference")
