"""
IATI Code Tables as MCP Resources

This module exposes all 41 IATI code lookup tables from .arc/R-analysis/ as MCP resources.
These tables are critical for data interpretation, validation, and human-readable output.

The RData files are loaded using pyreadr and cached in memory for performance.
Essential tables are pre-loaded at module import time, while others are lazy-loaded.

Resource URI Scheme:
    unhcr://codes/{category}/{subcategory}  - For code tables
    unhcr://mappings/{name}                - For mapping tables

Categories:
    - activity: date type, scope, status
    - organisation: identifier, registration agency, role, type
    - geographic: country, region
    - financial: aid type, budget, flow type, earmarking, etc.
    - sector: sector, category, vocabulary
    - policy: policy marker, humanitarian scope, clusters
    - result: indicator, result types
    - other: currency, description type, etc.
"""

import pyreadr
from pathlib import Path
from functools import lru_cache
from typing import List, Dict, Any

from unhcr_iati_mcp.context import mcp

# Directory containing RData files
RDATA_DIR = Path(__file__).parent.parent.parent.parent / ".arc" / "R-analysis"

# Cache for loaded code tables
_code_table_cache: Dict[str, List[Dict[str, Any]]] = {}

# Essential tables to pre-load (frequently accessed)
ESSENTIAL_TABLES = [
    "codeCountry",
    "codeRegion",
    "codeSector",
    "codeSectorCategory",
    "codeSectorVocabulary",
    "codeOrganisationRole",
    "codeOrganisationType",
    "codeActivityStatus",
    "codeActivityScope",
    "codeActivityDateType",
    "codeAidType",
    "codeFlowType",
    "codePolicyMarker",
]


def _load_code_table(filename: str) -> List[Dict[str, Any]]:
    """
    Load an RData file and return as list of dictionaries.
    
    Args:
        filename: The filename without .RData extension (e.g., "codeCountry")
    
    Returns:
        List of dictionaries representing the code table entries
    """
    if filename in _code_table_cache:
        return _code_table_cache[filename]
    
    filepath = RDATA_DIR / f"{filename}.RData"
    
    # Load the RData file
    result = pyreadr.read_r(str(filepath))
    
    # Get the first (and typically only) dataframe
    df = list(result.values())[0]
    
    # Convert to list of dicts (JSON-serializable)
    data = df.to_dict(orient="records")
    
    # Clean up - convert numpy types to Python native types
    cleaned_data = []
    for entry in data:
        cleaned_entry = {}
        for key, value in entry.items():
            # Convert numpy float/int to Python types
            if hasattr(value, 'item'):
                cleaned_entry[key] = value.item() if value.item() != value.item() else None
            # Convert numpy NaN to None
            elif value != value:  # NaN check
                cleaned_entry[key] = None
            else:
                cleaned_entry[key] = value
        cleaned_data.append(cleaned_entry)
    
    _code_table_cache[filename] = cleaned_data
    return cleaned_data


# Pre-load essential tables at module import time
for table in ESSENTIAL_TABLES:
    _load_code_table(table)


# =============================================================================
# ACTIVITY CODES
# =============================================================================

@mcp.resource("unhcr://codes/activity/date_type")
async def code_activity_date_type():
    """
    IATI Activity Date Type codes.
    
    Defines the types of dates that can be associated with an activity
    (e.g., start date, end date, actual start/end dates).
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeActivityDateType")


@mcp.resource("unhcr://codes/activity/scope")
async def code_activity_scope():
    """
    IATI Activity Scope codes.
    
    Defines the geographic or operational scope of an activity.
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeActivityScope")


@mcp.resource("unhcr://codes/activity/status")
async def code_activity_status():
    """
    IATI Activity Status codes.
    
    Defines the current status of an activity (e.g., Pipeline, Implementation, Closed).
    
    Common codes:
    - 1: Pipeline/identification
    - 2: Implementation
    - 3: Finalisation
    - 4: Closed
    - 5: Cancelled
    - 6: Suspended
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeActivityStatus")


# =============================================================================
# ORGANISATION CODES
# =============================================================================

@mcp.resource("unhcr://codes/organisation/identifier")
async def code_organisation_identifier():
    """
    IATI Organisation Identifier codes.
    
    Contains registered organisation identifiers and their metadata.
    
    Fields: code, name, type, registration_agency, category, url, status
    """
    return _load_code_table("codeOrganisationIdentifier")


@mcp.resource("unhcr://codes/organisation/registration_agency")
async def code_organisation_registration_agency():
    """
    IATI Organisation Registration Agency codes.
    
    Lists the agencies that can register organisations in IATI.
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeOrganisationRegistrationAgency")


@mcp.resource("unhcr://codes/organisation/role")
async def code_organisation_role():
    """
    IATI Organisation Role codes.
    
    Defines the role of an organisation in an activity.
    
    Common roles:
    - 1: Funding - The government or organisation which provides funds
    - 2: Accountable - Organisation responsible for oversight
    - 3: Extending - Organisation managing budget on behalf of funder
    - 4: Implementing - Organisation physically carrying out the activity
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeOrganisationRole")


@mcp.resource("unhcr://codes/organisation/type")
async def code_organisation_type():
    """
    IATI Organisation Type codes.
    
    Classifies organisations by type (e.g., Government, NGO, Multilateral).
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeOrganisationType")


@mcp.resource("unhcr://codes/organisation/iati_identifier")
async def code_iati_organisation_identifier():
    """
    IATI Organisation Identifier codes (alternative format).
    
    Contains IATI-specific organisation identifiers.
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeIATIOrganisationIdentifier")


# =============================================================================
# GEOGRAPHIC CODES
# =============================================================================

@mcp.resource("unhcr://codes/geographic/country")
async def code_country():
    """
    IATI Country codes.
    
    Maps ISO 2-letter and 3-letter country codes to country names.
    Contains 251+ countries and territories.
    
    Example entries:
    - AF: Afghanistan
    - SYR: Syrian Arab Republic
    - KEN: Kenya
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeCountry")


@mcp.resource("unhcr://codes/geographic/region")
async def code_region():
    """
    IATI Region codes.
    
    Defines geographic regions used in IATI data.
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeRegion")


@mcp.resource("unhcr://codes/geographic/location_class")
async def code_geographic_location_class():
    """
    IATI Geographic Location Class codes.
    
    Classifies locations by type (e.g., Country, Region, Administrative).
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeGeographicLocationClass")


# =============================================================================
# FINANCIAL CODES
# =============================================================================

@mcp.resource("unhcr://codes/financial/aid_type")
async def code_aid_type():
    """
    IATI Aid Type codes.
    
    Classifies types of aid/financial flows.
    Contains 500+ aid type codes.
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeAidType")


@mcp.resource("unhcr://codes/financial/aid_type_category")
async def code_aid_type_category():
    """
    IATI Aid Type Category codes.
    
    Groups aid types into broader categories.
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeAidTypeCategory")


@mcp.resource("unhcr://codes/financial/aid_type_vocabulary")
async def code_aid_type_vocabulary():
    """
    IATI Aid Type Vocabulary codes.
    
    Defines the vocabulary/standard used for aid type classification.
    
    Common vocabularies:
    - 1: OECD DAC CRS
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeAidTypeVocabulary")


@mcp.resource("unhcr://codes/financial/budget_identifier")
async def code_budget_identifier():
    """
    IATI Budget Identifier codes.
    
    Identifies budget lines and classifications.
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeBudgetIdentifier")


@mcp.resource("unhcr://codes/financial/budget_identifier_sector")
async def code_budget_identifier_sector():
    """
    IATI Budget Identifier Sector codes.
    
    Maps budget identifiers to sectors.
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeBudgetIdentifierSector")


@mcp.resource("unhcr://codes/financial/budget_status")
async def code_budget_status():
    """
    IATI Budget Status codes.
    
    Defines the status of a budget (e.g., Planned, Committed, Disbursed).
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeBudgetStatus")


@mcp.resource("unhcr://codes/financial/budget_type")
async def code_budget_type():
    """
    IATI Budget Type codes.
    
    Classifies budgets by type.
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeBudgetType")


@mcp.resource("unhcr://codes/financial/cash_voucher_modalities")
async def code_cash_voucher_modalities():
    """
    IATI Cash and Voucher Modalities codes.
    
    Defines modalities for cash and voucher assistance.
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeCashandVoucherModalities")


@mcp.resource("unhcr://codes/financial/currency")
async def code_currency():
    """
    IATI Currency codes.
    
    ISO currency codes used in IATI data.
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeCurrency")


@mcp.resource("unhcr://codes/financial/earmarking_category")
async def code_earmarking_category():
    """
    IATI Earmarking Category codes.
    
    Defines how funds are earmarked (e.g., Core, Non-core, Thematic).
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeEarmarkingCategory")


@mcp.resource("unhcr://codes/financial/flow_type")
async def code_flow_type():
    """
    IATI Flow Type codes.
    
    Defines the type of financial flow (e.g., ODA, OOF, Private).
    
    Common codes:
    - 10: ODA (Official Development Assistance)
    - 20: OOF (Other Official Flows)
    - 30: Private
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeFlowType")


@mcp.resource("unhcr://codes/financial/transaction_type")
async def code_transaction_type():
    """
    IATI Transaction Type codes.
    
    Defines types of financial transactions.
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeTransactionType")


# =============================================================================
# SECTOR CODES
# =============================================================================

@mcp.resource("unhcr://codes/sector")
async def code_sector():
    """
    IATI Sector codes.
    
    The primary sector classification table with 323+ sector codes.
    
    Example entries:
    - 11110: Education policy and administrative management
    - 12220: Basic health care
    - 72040: Emergency food assistance
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeSector")


@mcp.resource("unhcr://codes/sector/category")
async def code_sector_category():
    """
    IATI Sector Category codes.
    
    Groups sectors into broader categories.
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeSectorCategory")


@mcp.resource("unhcr://codes/sector/vocabulary")
async def code_sector_vocabulary():
    """
    IATI Sector Vocabulary codes.
    
    Defines the vocabulary/standard used for sector classification.
    
    Common vocabularies:
    - 1: OECD DAC CRS (most common)
    - 2: OECD DAC CRS (5-digit)
    - 99: Reporting Organisation
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeSectorVocabulary")


# =============================================================================
# POLICY AND HUMANITARIAN CODES
# =============================================================================

@mcp.resource("unhcr://codes/policy/collaboration_type")
async def code_collaboration_type():
    """
    IATI Collaboration Type codes.
    
    Defines types of collaboration between organisations.
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeCollaborationType")


@mcp.resource("unhcr://codes/policy/marker")
async def code_policy_marker():
    """
    IATI Policy Marker codes.
    
    Flags for policy relevance (e.g., Gender, Environment, Human Rights).
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codePolicyMarker")


@mcp.resource("unhcr://codes/policy/humanitarian_scope_type")
async def code_humanitarian_scope_type():
    """
    IATI Humanitarian Scope Type codes.
    
    Defines the type of humanitarian scope.
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeHumanitarianScopeType")


@mcp.resource("unhcr://codes/policy/humanitarian_scope_vocabulary")
async def code_humanitarian_scope_vocabulary():
    """
    IATI Humanitarian Scope Vocabulary codes.
    
    Defines the vocabulary used for humanitarian scope classification.
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeHumanitarianScopeVocabulary")


@mcp.resource("unhcr://codes/policy/humanitarian_cluster")
async def code_humanitarian_cluster():
    """
    IATI Humanitarian Cluster codes.
    
    UN humanitarian clusters for coordination.
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeHumCluster")


# =============================================================================
# RESULT FRAMEWORK CODES
# =============================================================================

@mcp.resource("unhcr://codes/result/indicator_measure")
async def code_indicator_measure():
    """
    IATI Indicator Measure codes.
    
    Defines types of indicator measures.
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeIndicatorMeasure")


@mcp.resource("unhcr://codes/result/indicator_vocabulary")
async def code_indicator_vocabulary():
    """
    IATI Indicator Vocabulary codes.
    
    Defines vocabularies used for indicators.
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeIndicatorVocabulary")


@mcp.resource("unhcr://codes/result/type")
async def code_result_type():
    """
    IATI Result Type codes.
    
    Classifies results by type (Impact, Outcome, Output).
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeResultType")


# =============================================================================
# OTHER CODES
# =============================================================================

@mcp.resource("unhcr://codes/description_type")
async def code_description_type():
    """
    IATI Description Type codes.
    
    Defines types of descriptions in IATI data.
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeDescriptionType")


# =============================================================================
# MAPPING TABLES
# =============================================================================

@mcp.resource("unhcr://mappings/indicator")
async def mapping_indicator():
    """
    IATI Indicator to Result mapping.
    
    Maps indicators to UNHCR outcome areas and results framework.
    
    Fields: indicator, result_area, result_code, description
    """
    return _load_code_table("mapping_indicator")


@mcp.resource("unhcr://mappings/result")
async def mapping_result():
    """
    IATI Result mapping table.
    
    Maps UNHCR results framework components.
    
    Fields vary by mapping type
    """
    return _load_code_table("mapping_result")


@mcp.resource("unhcr://mappings/sdg")
async def mapping_sdg():
    """
    UNHCR Outcome Areas to SDG mapping.
    
    Maps UNHCR's 16 Outcome Areas (OA1-OA16) to Sustainable Development Goals.
    
    Example mappings:
    - OA1 (Access to Territory) → SDG 16 (Peace, justice and strong institutions)
    - OA4 (Sexual and Gender-based Violence) → SDG 5 (Gender Equality)
    
    Fields: area, sdg
    """
    return _load_code_table("mapping_sdg")


@mcp.resource("unhcr://mappings/sector")
async def mapping_sector():
    """
    Sector mapping table.
    
    Additional sector mappings beyond the standard IATI codes.
    
    Fields vary by mapping type
    """
    return _load_code_table("mapping_sector")


# =============================================================================
# UN SDG CODES
# =============================================================================

@mcp.resource("unhcr://codes/sdg/goals")
async def code_sdg_goals():
    """
    UN Sustainable Development Goals.
    
    All 17 SDGs as defined in IATI.
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeUNSDGGoals")


@mcp.resource("unhcr://codes/sdg/targets")
async def code_sdg_targets():
    """
    UN Sustainable Development Goal Targets.
    
    All SDG targets as defined in IATI.
    
    Fields: code, name, description, category, url, status
    """
    return _load_code_table("codeUNSDGTargets")


# =============================================================================
# UTILITY: Get all available code tables
# =============================================================================

@mcp.resource("unhcr://codes/_all_tables")
async def all_code_tables():
    """
    List all available IATI code tables.
    
    Returns metadata about all 41 code and mapping tables, including:
    - Table name
    - Resource URI
    - Number of entries
    - Category
    """
    all_tables = [
        # Activity
        {"name": "codeActivityDateType", "uri": "unhcr://codes/activity/date_type", "category": "activity"},
        {"name": "codeActivityScope", "uri": "unhcr://codes/activity/scope", "category": "activity"},
        {"name": "codeActivityStatus", "uri": "unhcr://codes/activity/status", "category": "activity"},
        
        # Organisation
        {"name": "codeOrganisationIdentifier", "uri": "unhcr://codes/organisation/identifier", "category": "organisation"},
        {"name": "codeOrganisationRegistrationAgency", "uri": "unhcr://codes/organisation/registration_agency", "category": "organisation"},
        {"name": "codeOrganisationRole", "uri": "unhcr://codes/organisation/role", "category": "organisation"},
        {"name": "codeOrganisationType", "uri": "unhcr://codes/organisation/type", "category": "organisation"},
        {"name": "codeIATIOrganisationIdentifier", "uri": "unhcr://codes/organisation/iati_identifier", "category": "organisation"},
        
        # Geographic
        {"name": "codeCountry", "uri": "unhcr://codes/geographic/country", "category": "geographic"},
        {"name": "codeRegion", "uri": "unhcr://codes/geographic/region", "category": "geographic"},
        {"name": "codeGeographicLocationClass", "uri": "unhcr://codes/geographic/location_class", "category": "geographic"},
        
        # Financial
        {"name": "codeAidType", "uri": "unhcr://codes/financial/aid_type", "category": "financial"},
        {"name": "codeAidTypeCategory", "uri": "unhcr://codes/financial/aid_type_category", "category": "financial"},
        {"name": "codeAidTypeVocabulary", "uri": "unhcr://codes/financial/aid_type_vocabulary", "category": "financial"},
        {"name": "codeBudgetIdentifier", "uri": "unhcr://codes/financial/budget_identifier", "category": "financial"},
        {"name": "codeBudgetIdentifierSector", "uri": "unhcr://codes/financial/budget_identifier_sector", "category": "financial"},
        {"name": "codeBudgetStatus", "uri": "unhcr://codes/financial/budget_status", "category": "financial"},
        {"name": "codeBudgetType", "uri": "unhcr://codes/financial/budget_type", "category": "financial"},
        {"name": "codeCashandVoucherModalities", "uri": "unhcr://codes/financial/cash_voucher_modalities", "category": "financial"},
        {"name": "codeCurrency", "uri": "unhcr://codes/financial/currency", "category": "financial"},
        {"name": "codeEarmarkingCategory", "uri": "unhcr://codes/financial/earmarking_category", "category": "financial"},
        {"name": "codeFlowType", "uri": "unhcr://codes/financial/flow_type", "category": "financial"},
        {"name": "codeTransactionType", "uri": "unhcr://codes/financial/transaction_type", "category": "financial"},
        
        # Sector
        {"name": "codeSector", "uri": "unhcr://codes/sector", "category": "sector"},
        {"name": "codeSectorCategory", "uri": "unhcr://codes/sector/category", "category": "sector"},
        {"name": "codeSectorVocabulary", "uri": "unhcr://codes/sector/vocabulary", "category": "sector"},
        
        # Policy
        {"name": "codeCollaborationType", "uri": "unhcr://codes/policy/collaboration_type", "category": "policy"},
        {"name": "codePolicyMarker", "uri": "unhcr://codes/policy/marker", "category": "policy"},
        {"name": "codeHumanitarianScopeType", "uri": "unhcr://codes/policy/humanitarian_scope_type", "category": "policy"},
        {"name": "codeHumanitarianScopeVocabulary", "uri": "unhcr://codes/policy/humanitarian_scope_vocabulary", "category": "policy"},
        {"name": "codeHumCluster", "uri": "unhcr://codes/policy/humanitarian_cluster", "category": "policy"},
        
        # Result Framework
        {"name": "codeIndicatorMeasure", "uri": "unhcr://codes/result/indicator_measure", "category": "result"},
        {"name": "codeIndicatorVocabulary", "uri": "unhcr://codes/result/indicator_vocabulary", "category": "result"},
        {"name": "codeResultType", "uri": "unhcr://codes/result/type", "category": "result"},
        
        # Other
        {"name": "codeDescriptionType", "uri": "unhcr://codes/description_type", "category": "other"},
        
        # Mappings
        {"name": "mapping_indicator", "uri": "unhcr://mappings/indicator", "category": "mapping"},
        {"name": "mapping_result", "uri": "unhcr://mappings/result", "category": "mapping"},
        {"name": "mapping_sdg", "uri": "unhcr://mappings/sdg", "category": "mapping"},
        {"name": "mapping_sector", "uri": "unhcr://mappings/sector", "category": "mapping"},
        
        # SDG
        {"name": "codeUNSDGGoals", "uri": "unhcr://codes/sdg/goals", "category": "sdg"},
        {"name": "codeUNSDGTargets", "uri": "unhcr://codes/sdg/targets", "category": "sdg"},
    ]
    
    # Add entry counts
    for table in all_tables:
        table_name = table["name"]
        try:
            data = _load_code_table(table_name)
            table["entry_count"] = len(data)
        except Exception:
            table["entry_count"] = 0
    
    return all_tables
