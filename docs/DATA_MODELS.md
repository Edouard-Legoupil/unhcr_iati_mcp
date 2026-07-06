# Data Models

This document describes the Pydantic data models used in the UNHCR IATI MCP Server.

## Overview

The server uses Pydantic models for type-safe data parsing and validation. All models are located in the `src/unhcr_iati_mcp/models/` directory.

## Core Models

### Activity

Represents an IATI activity (project/program) with full result framework support:

```python
from unhcr_iati_mcp.models.activity import Activity

class Activity(BaseModel):
    iati_identifier: str                          # Unique identifier
    title_narrative: List[str] = []               # Titles in multiple languages
    description_narrative: List[str] = []         # Descriptions
    recipient_country_code: List[str] = []        # ISO country codes
    sector_code: List[str] = []                   # Sector codes
    sector_vocabulary: List[str] = []            # Sector vocabulary codes (1, 2, 10, 98, 99)
    sector_percentage: List[float] = []          # Sector percentage allocations
    reporting_org_ref: List[str] = []             # Publishing organization
    
    # Result Framework Data
    result_type: List[str] = []                  # Result type codes (1=Output, 2=Outcome, 3=Impact)
    result_title_narrative: List[str] = []       # Result titles
    result_indicator_ref: List[str] = []          # Indicator references
    result_indicator_title_narrative: List[str] = []  # Indicator titles
    result_indicator_measure: List[str] = []      # Indicator measure types (1-5)
    result_indicator_baseline_value: List[str] = []  # Baseline values
    result_indicator_period_target_value: List[str] = []  # Target values
    result_indicator_period_actual_value: List[str] = []  # Actual values
```

**Activity Methods:**
- `get_sector_info()` - Get structured sector data
- `get_sectors_by_vocabulary()` - Group sectors by vocabulary (SAFEST approach)
- `get_unhcr_sectors()` - Filter to UNHCR vocabulary 98
- `has_mixed_vocabularies()` - Check for multiple vocabularies
- `validate_sector_aggregation()` - Validate before aggregating
- `get_result_info()` - Get structured result data
- `get_indicator_info()` - Get structured indicator data
- `get_results_with_indicators()` - Results with associated indicators
- `get_indicators_by_type()` - Group indicators by result type
- `get_quantitative_indicators()` - Filter to quantitative indicators
- `get_qualitative_indicators()` - Filter to qualitative indicators
- `has_results_framework()` - Check if activity has result data

### Budget

Represents planned funding allocations:

```python
from unhcr_iati_mcp.models.budget import Budget

class Budget(BaseModel):
    budget_value: List[float] = []               # Budget amounts
    budget_value_currency: List[str] = []         # Currency codes
    budget_period_start: List[str] = []          # Start dates (ISO format)
    budget_period_end: List[str] = []            # End dates (ISO format)
    budget_type: List[str] = []                  # Budget type codes
    budget_status: List[str] = []                # Budget status codes
```

### Transaction

Represents financial movements:

```python
from unhcr_iati_mcp.models.transaction import Transaction

class Transaction(BaseModel):
    transaction_value: List[float] = []           # Transaction amounts
    transaction_value_currency: List[str] = []   # Currency codes
    transaction_date: List[str] = []              # Dates (ISO format)
    transaction_type: List[str] = []              # Type codes
    provider_org_ref: List[str] = []              # Providing organization
    receiver_org_ref: List[str] = []              # Receiving organization
    flow_type: List[str] = []                    # Flow type codes
    aid_type: List[str] = []                      # Aid type codes
    earmarking_category: List[str] = []           # Earmarking categories
```

## Sector Models

Comprehensive sector data with vocabulary management:

```python
from unhcr_iati_mcp.models.sector import (
    SectorInfo, SectorSummary, SectorVocabularySummary,
    SectorAnalysisResult, SectorValidationResult, CrossVocabularySectorPair
)

class SectorInfo(BaseModel):
    sector_code: str
    sector_narrative: str
    sector_vocabulary: str  # CRITICAL: Always check this field!
    sector_percentage: float

class SectorSummary(BaseModel):
    vocabulary: str
    code: str
    name: str
    count: int
    percentage: float

class SectorVocabularySummary(BaseModel):
    vocabulary: str
    vocabulary_name: str
    total_sectors: int
    total_activities: int
    warning: str  # Vocabulary-specific warning

class SectorAnalysisResult(BaseModel):
    vocabularies_found: List[str]
    sectors_by_vocabulary: Dict[str, List[SectorSummary]]
    mixed_vocabulary_warning: bool
    recommendations: List[str]

class CrossVocabularySectorPair(BaseModel):
    code: str
    vocabularies: List[str]
    names: Dict[str, str]  # vocabulary -> name mapping
    warning: str

class SectorValidationResult(BaseModel):
    is_valid: bool
    issues: List[str]
    recommendations: List[str]
```

## Result Framework Models

Complete IATI result framework support:

```python
from unhcr_iati_mcp.models.result import (
    Result, ResultSummary, Indicator, IndicatorSummary,
    IndicatorPeriod, Dimension, DimensionGroup,
    ResultFrameworkSummary, ResultIndicatorAnalysis,
    ResultValidationResult, UNHCRResultArea, UNHCRIndicator
)

class Result(BaseModel):
    result_type: str  # 1=Output, 2=Outcome, 3=Impact, 9=Other
    result_title_narrative: str
    result_aggregation_status: Optional[bool]
    result_description_narrative: Optional[str]

class Indicator(BaseModel):
    indicator_ref: Optional[str]
    indicator_title_narrative: str
    indicator_measure: str  # 1=Unit, 2=Percentage, 3=Nominal, 4=Ordinal, 5=Qualitative
    baseline_value: Optional[str]
    baseline_year: Optional[str]
    period_start: Optional[str]
    period_end: Optional[str]
    period_target_value: Optional[str]
    period_actual_value: Optional[str]
    period_actual_comment: Optional[str]

class IndicatorPeriod(BaseModel):
    period_start: str
    period_end: str
    target_value: Optional[str]
    actual_value: Optional[str]
    comment: Optional[str]

class Dimension(BaseModel):
    name: str
    value: str

class DimensionGroup(BaseModel):
    dimension: List[Dimension]

class UNHCRResultArea(BaseModel):
    code: str  # OA1-OA16
    name: str  # Protection, Solutions, Health, Education, etc.
    description: str
    level: str = "Outcome"  # Result level (Outcome for OA)

class UNHCRIndicator(BaseModel):
    ref: str
    title: str
    measure: str
    oa_code: str  # Which Operational Area this indicator belongs to
    baseline: Optional[float]
    target: Optional[float]
    actual: Optional[float]

class ResultSummary(BaseModel):
    result_type: str
    count: int
    percentage: float

class ResultFrameworkSummary(BaseModel):
    outputs: ResultSummary
    outcomes: ResultSummary
    impacts: ResultSummary
    others: ResultSummary
    total_results: int

class ResultIndicatorAnalysis(BaseModel):
    by_type: Dict[str, int]  # measure type -> count
    by_oa: Dict[str, int]  # OA code -> count
    quantitative: int
    qualitative: int
    with_disaggregation: int

class ResultValidationResult(BaseModel):
    is_valid: bool
    issues: List[str]
    has_mixed_types: bool
    has_invalid_measure_types: bool
```

## Response Models

```python
from unhcr_iati_mcp.models.responses import APIResponse
from unhcr_iati_mcp.models.errors import ErrorResponse

# Generic API response wrapper
class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    message: str | None = None
    pagination: dict | None = None

# Error response
class ErrorResponse(BaseModel):
    error_type: str
    message: str
    details: dict = {}
    timestamp: str
```

## Pagination Models

```python
from unhcr_iati_mcp.models.pagination import PaginationInfo, PaginatedResponse

class PaginationInfo(BaseModel):
    start: int
    rows: int
    numFound: int
    total_pages: int
    current_page: int

class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    pagination: PaginationInfo
```

## Donor and Country Models

```python
from unhcr_iati_mcp.models.donor import Donor, DonorSummary
from unhcr_iati_mcp.models.country import Country, CountrySummary

class Donor(BaseModel):
    code: str
    name: str
    type: Optional[str]
    total_contributions: Optional[float]
    currency: Optional[str]

class DonorSummary(BaseModel):
    donor_code: str
    donor_name: str
    total_amount: float
    currency: str
    transaction_count: int
    ranking: int

class Country(BaseModel):
    code: str  # ISO 2-letter or 3-letter
    name: str
    region: Optional[str]
    income_level: Optional[str]

class CountrySummary(BaseModel):
    country_code: str
    country_name: str
    activity_count: int
    total_budget: Optional[float]
    total_transactions: Optional[float]
```

## Code Table Models

```python
from unhcr_iati_mcp.models.codes import (
    CodeEntry, CodeTableMetadata, CodeTableCacheStatus
)

class CodeEntry(BaseModel):
    code: str
    name: str
    description: Optional[str]
    category: Optional[str]
    parent: Optional[str]

class CodeTableMetadata(BaseModel):
    table_name: str
    display_name: str
    description: str
    code_type: str  # activity, organisation, geographic, financial, sector, policy, result
    is_essential: bool  # Pre-loaded at startup
    is_lazy: bool  # Loaded on-demand
    entry_count: int

class CodeTableCacheStatus(BaseModel):
    cache_size: int
    loaded_tables: List[str]
    pending_tables: List[str]
    last_updated: str
```

## Analytics Models

```python
from unhcr_iati_mcp.models.analytics import (
    PortfolioSummary, SectorDistribution, DonorBreakdown,
    CountryBreakdown, YearlyTrends, TopItems
)

class PortfolioSummary(BaseModel):
    total_activities: int
    total_budgets: int
    total_transactions: int
    total_budget_value: float
    total_transaction_value: float
    currency: str

class SectorDistribution(BaseModel):
    sector_code: str
    sector_name: str
    vocabulary: str
    activity_count: int
    percentage: float

class DonorBreakdown(BaseModel):
    donor_code: str
    donor_name: str
    contribution_count: int
    total_amount: float
    percentage: float

class CountryBreakdown(BaseModel):
    country_code: str
    country_name: str
    activity_count: int
    total_budget: float
    percentage: float

class YearlyTrends(BaseModel):
    year: int
    activity_count: int
    budget_value: float
    transaction_value: float

class TopItems(BaseModel, Generic[T]):
    items: List[T]
    total_count: int
```

## Export Models

```python
from unhcr_iati_mcp.models.export import (
    ExportRequest, ExportResult, BulkExportRequest
)

class ExportRequest(BaseModel):
    collection: str  # activity, transaction, budget
    query: str = "*"  # Solr query
    fields: List[str] = []  # Fields to include
    max_records: int = 500

class ExportResult(BaseModel):
    format: str  # json, csv
    data: Union[str, bytes]  # Exported data
    record_count: int
    timestamp: str

class BulkExportRequest(BaseModel):
    collections: List[str]
    format: str = "json"
    max_records_per_collection: int = 500
```
