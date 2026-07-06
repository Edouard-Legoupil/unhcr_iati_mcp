"""
Transaction model for UNHCR IATI MCP Server.

This module defines the Pydantic model for IATI transaction data.
"""

from typing import List, Optional, Union, Any

from pydantic import BaseModel, Field, model_validator


class Transaction(BaseModel):
    """
    Represents an IATI transaction (financial movement or disbursement).
    
    Based on actual IATI Datastore schema.
    """
    
    # Core identifiers
    iati_identifier: Optional[str] = Field(None, description="Linked activity identifier")
    id: Optional[str] = Field(None, description="Internal document ID")
    
    # Transaction type
    transaction_type: Union[str, List[str]] = Field(default_factory=list, description="Transaction type codes")
    
    # Transaction values
    transaction_value: Union[float, List[float]] = Field(default_factory=list, description="Transaction values")
    transaction_value_currency: Union[str, List[str]] = Field(default_factory=list, description="Transaction currencies")
    transaction_value_value_date: Union[str, List[str]] = Field(default_factory=list, description="Transaction value dates")
    
    # Transaction dates
    transaction_date: Union[str, List[str]] = Field(default_factory=list, description="Transaction dates")
    
    # Provider organization
    provider_org_ref: Union[str, List[str]] = Field(default_factory=list, description="Provider organization references")
    provider_org_type: Union[str, List[str]] = Field(default_factory=list, description="Provider organization types")
    provider_org_narrative: Union[str, List[str]] = Field(default_factory=list, description="Provider organization names")
    provider_org_provider_activity_id: Union[str, List[str]] = Field(default_factory=list, description="Provider activity IDs")
    
    # Receiver organization
    receiver_org_ref: Union[str, List[str]] = Field(default_factory=list, description="Receiver organization references")
    receiver_org_type: Union[str, List[str]] = Field(default_factory=list, description="Receiver organization types")
    receiver_org_narrative: Union[str, List[str]] = Field(default_factory=list, description="Receiver organization names")
    
    # Aid type
    aid_type_code: Union[str, List[str]] = Field(default_factory=list, description="Aid type codes")
    aid_type_vocabulary: Union[str, List[str]] = Field(default_factory=list, description="Aid type vocabularies")
    
    # References and descriptions
    transaction_ref: Union[str, List[str]] = Field(default_factory=list, description="Transaction references")
    description_narrative: Union[str, List[str]] = Field(default_factory=list, description="Transaction descriptions")
    
    # UNHCR-specific values
    unhcr_value_USD: Union[str, List[str]] = Field(default_factory=list, description="UNHCR values in USD (as strings)")
    
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
            'transaction_type',
            'transaction_value',
            'transaction_value_currency',
            'transaction_value_value_date',
            'transaction_date',
            'provider_org_ref',
            'provider_org_type',
            'provider_org_narrative',
            'provider_org_provider_activity_id',
            'receiver_org_ref',
            'receiver_org_type',
            'receiver_org_narrative',
            'aid_type_code',
            'aid_type_vocabulary',
            'transaction_ref',
            'description_narrative',
            'unhcr_value_USD',
        ]
        
        result = dict(data)
        for field in list_fields:
            if field in result and result[field] is not None and not isinstance(result[field], list):
                result[field] = [result[field]]
        
        return result


class TransactionSummary(BaseModel):
    """
    Simplified Transaction model for summaries and listings.
    """
    iati_identifier: Optional[str] = Field(None, description="Linked activity identifier")
    transaction_type: Union[str, List[str]] = Field(default_factory=list, description="Transaction type codes")
    transaction_value: Union[float, List[float]] = Field(default_factory=list, description="Transaction values")
    transaction_value_currency: Union[str, List[str]] = Field(default_factory=list, description="Transaction currencies")
    transaction_date: Union[str, List[str]] = Field(default_factory=list, description="Transaction dates")
    provider_org_ref: Union[str, List[str]] = Field(default_factory=list, description="Provider organization references")
    receiver_org_ref: Union[str, List[str]] = Field(default_factory=list, description="Receiver organization references")
    aid_type_code: Union[str, List[str]] = Field(default_factory=list, description="Aid type codes")
    unhcr_value_USD: Union[str, List[str]] = Field(default_factory=list, description="UNHCR values in USD")
    description_narrative: Union[str, List[str]] = Field(default_factory=list, description="Transaction descriptions")
