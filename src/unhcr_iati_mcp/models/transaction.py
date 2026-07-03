"""
Transaction model for UNHCR IATI MCP Server.

This module defines the Pydantic model for IATI transaction data.
"""

from pydantic import BaseModel
from typing import List


class Transaction(BaseModel):
    """
    Represents an IATI transaction (financial movement or disbursement).
    
    Attributes:
        iati_identifier: Unique identifier for the linked activity
        transaction_type: Type of transaction (e.g., "1" for incoming funds)
        transaction_value: Amount(s) of the transaction
        transaction_value_currency: Currency code(s) for the transaction
        transaction_date: Date(s) of the transaction in ISO format
        provider_org_ref: Reference(s) to the providing organization
        receiver_org_ref: Reference(s) to the receiving organization
        description_narrative: Description(s) of the transaction
    """
    iati_identifier: str
    transaction_type: List[str] = []
    transaction_value: List[float] = []
    transaction_value_currency: List[str] = []
    transaction_date: List[str] = []
    provider_org_ref: List[str] = []
    receiver_org_ref: List[str] = []
    description_narrative: List[str] = []
