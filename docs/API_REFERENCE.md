# API Reference

This document provides comprehensive API reference for the UNHCR IATI MCP Server.

## IATIClient API

The `IATIClient` class in `client.py` provides the core API interaction layer:

### Basic Usage

```python
from unhcr_iati_mcp.client import IATIClient

client = IATIClient()
```

### Query Methods

#### Query with Pagination

```python
# Returns: dict with 'response' key containing 'docs' array and 'numFound'
data = await client.query(
    collection="activity",
    q='reporting_org_ref:"XM-DAC-41121"',
    rows=100,
    start=0,
    fl="*"  # or specific fields: "iati_identifier,title_narrative"
)
```

#### Fetch All Results

Handles pagination automatically:

```python
data = await client.fetch_all(
    collection="transaction",
    q='reporting_org_ref:"XM-DAC-41121"',
    max_records=500  # optional limit
)
```

#### Fetch a Single Page

```python
data = await client.fetch_page(
    collection="budget",
    q='reporting_org_ref:"XM-DAC-41121"',
    page=0  # 0-indexed page number
)
```

#### Convenience Methods

```python
# Shortcut methods for specific collections
activities = await client.activities(q='reporting_org_ref:"XM-DAC-41121"')
transactions = await client.transactions(q='reporting_org_ref:"XM-DAC-41121"')
budgets = await client.budgets(q='reporting_org_ref:"XM-DAC-41121"')
```

### Retry Logic

The client uses `tenacity` for automatic retry with exponential backoff:

- **Max attempts**: 5
- **Wait strategy**: Exponential backoff (1s, 2s, 4s, 8s, 16s)
- **Retry conditions**: Timeout, connection errors, server errors (5xx), rate limits (429)
- **Retryable exceptions**: `httpx.TimeoutException`, `httpx.ConnectError`, `IATIServerError`, `IATIRateLimitError`

### Error Handling

Custom exception hierarchy:

```python
from unhcr_iati_mcp.client import (
    IATIError,              # Base exception
    IATIAuthenticationError, # 401/403 errors
    IATIRateLimitError,      # 429 rate limit exceeded
    IATIServerError,         # 5xx server errors
)
```

### Configuration Options

The `IATIClient` accepts the following configuration:

```python
client = IATIClient(
    api_key=os.getenv("IATI_API_KEY"),
    base_url="https://api.iatistandard.org/datastore",
    timeout=120,  # seconds
    page_size=1000,  # default records per page
    publisher_ref="XM-DAC-41121"  # UNHCR's publisher reference
)
```

## MCP Tools Reference

All tools are prefixed with `unhcr_` and automatically filter results to UNHCR's data.

### Activity Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `unhcr_activities` | List UNHCR activities with pagination | `rows`, `start` |
| `unhcr_activity` | Get a specific activity by IATI identifier | `iati_identifier` |
| `unhcr_activity_by_country` | Filter activities by country code (ISO 2-letter) | `country_code`, `rows` |
| `unhcr_activity_by_sector` | Filter activities by sector code | `sector_code`, `rows` |
| `unhcr_activity_by_year` | Filter activities by year | `year` |
| `unhcr_activity_by_identifier` | Filter by IATI identifier components | `year`, `programme`, `country_code`, `operation` |

### Transaction Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `unhcr_transactions` | List all UNHCR transactions | `year` (optional) |
| `unhcr_transaction_search` | Search transactions with custom Solr query | `query` |

### Budget Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `unhcr_budgets` | List all UNHCR budgets | `year` (optional) |

### Analysis Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `unhcr_top_donors` | Get top N donors by contribution amount | `top_n` |
| `unhcr_top_countries` | Get top N countries by activity count | `top_n` |
| `unhcr_sector_summary` | Get sector distribution across activities | - |
| `unhcr_most_funded_sectors` | Get most funded sectors per country | `country_code`, `top_n`, `year` |
| `unhcr_top_donors_by_country` | Get main donors by country | `country_code`, `top_n`, `year` |
| `unhcr_portfolio_summary` | Get aggregate counts (activities, budgets, transactions) | - |
| `unhcr_analytical_questions_summary` | Get summary of all 7 core analytical questions | `country_code`, `year` |

### Sector Analysis Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `unhcr_implementing_partners` | Get main implementing partners by country | `country_code`, `top_n` |
| `unhcr_earmarking_breakdown` | Get earmarking type breakdown for transactions | `country_code`, `year` |
| `unhcr_budget_vs_expenditure` | Compare budget vs expenditure | `country_code`, `year` |
| `unhcr_indicator_trends` | Track indicator evolution over time | `country_code`, `indicator_ref`, `start_year`, `end_year` |
| `unhcr_partnership_analysis` | Analyze partnership levels across activities | `country_code` |

### Export Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `unhcr_export_json` | Export data as JSON | `collection`, `query` |
| `unhcr_export_csv` | Export data as CSV | `collection`, `query` |
| `unhcr_bulk_extract` | Bulk extract from multiple collections | `collections`, `format` |

### Health & Monitoring Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `health_check` | Server health status | - |
| `system_status` | System component status | - |
| `datastore_ping` | Test IATI Datastore connection | - |
| `api_limits` | API rate limit information | - |
| `metrics` | Prometheus metrics endpoint | - |
| `cache_stats` | Cache statistics | - |

### Code Resolution Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `resolve_code` | Resolve an IATI code to human-readable name | `code_type`, `code`, `table` |
| `validate_code` | Validate if an IATI code exists | `code_type`, `code`, `table` |
| `search_code_table` | Search an IATI code table | `code_type`, `query`, `limit`, `table` |
| `list_code_table` | List all entries in a code table | `code_type`, `limit`, `offset`, `table` |
| `batch_resolve_codes` | Resolve multiple codes in a single call | `code_type`, `codes`, `table` |

## MCP Resources

Static and reference data accessible via MCP resource URIs:

### Core Resources

| URI | Description | Format |
|-----|-------------|--------|
| `unhcr://donors` | Donor code to name mapping | JSON object |
| `unhcr://countries` | Country reference data | JSON object |
| `unhcr://sectors` | UNHCR-specific sector code to name mapping (Vocabulary 98) | JSON object |
| `unhcr://glossary` | IATI terminology glossary | JSON object |
| `unhcr://portfolio` | UNHCR portfolio metadata | JSON object |
| `unhcr://schemas` | Data schema definitions | JSON object |
| `unhcr://sdgs` | Sustainable Development Goals mapping | JSON object |

### Sector Resources

| URI | Description | Format |
|-----|-------------|--------|
| `unhcr://sector_vocabularies` | Metadata about all IATI sector vocabularies with warnings | JSON object |
| `unhcr://sector_analysis_guidelines` | Comprehensive guidelines for correct sector data analysis | JSON object |
| `unhcr://sector_vocabulary_warnings` | Quick-reference warnings for each vocabulary | JSON object |

### Result Framework Resources

| URI | Description | Format |
|-----|-------------|--------|
| `unhcr://result_types` | IATI result type codes (Output, Outcome, Impact, Other) | JSON object |
| `unhcr://indicator_measures` | IATI indicator measure codes (Unit, Percentage, Nominal, Ordinal, Qualitative) | JSON object |
| `unhcr://result_areas` | UNHCR's 16 Operational Areas (OA) at outcome level | JSON object |
| `unhcr://result_analysis_guidelines` | Guidelines for correct result data analysis | JSON object |
| `unhcr://disaggregation_dimensions` | Common disaggregation dimensions (sex, age, disability, etc.) | JSON object |

### Code Tables

> **Note:** Code tables are accessed via **Code Resolution Tools** (not as direct MCP resources).

All 41 IATI code lookup tables are available through the code resolution tools:

- **`resolve_code(code_type, code)`** - Resolve a code to human-readable name
- **`validate_code(code_type, code)`** - Check if a code exists
- **`list_code_table(code_type)`** - List all entries in a code table
- **`search_code_table(code_type, query)`** - Search code table by name/description
- **`batch_resolve_codes(code_type, codes)`** - Resolve multiple codes at once

**Supported code types:**
- Activity: `activity_status`, `activity_scope`, `activity_date_type`
- Organisation: `organisation_role`, `organisation_type`, `organisation_identifier`
- Geographic: `country`, `region`
- Financial: `aid_type`, `budget`, `flow_type`, `currency`, `earmarking`
- Sector: `sector`, `sector_category`, `sector_vocabulary`
- Policy: `policy_marker`, `humanitarian_scope`
- Result: `result_type`, `indicator_measure`
- SDG: `sdg_goals`, `sdg_targets`
- And 20+ more IATI standard code tables

**Note:** Code tables use on-demand (lazy) loading and are cached for performance.

## Solr Query Syntax

The underlying IATI Datastore uses Solr for querying. Here's a quick reference:

| Query Type | Example | Description |
|------------|---------|-------------|
| Field search | `reporting_org_ref:XM-DAC-41121` | Search specific field |
| Wildcard | `title_narrative:health*` | Match prefix |
| Boolean AND | `country:AF AND sector:12220` | Both conditions |
| Boolean OR | `country:AF OR country:KE` | Either condition |
| Boolean NOT | `sector:12220 NOT country:SYR` | Exclude condition |
| Range query | `transaction_value:[1000000 TO *]` | Numeric range |
| Date range | `last_updated_datetime:[2024-01-01 TO 2024-12-31]` | Date range |
| Phrase search | `title_narrative:"climate change"` | Exact phrase |
| Required field | `reporting_org_ref:*` | Field must exist |

### Common IATI Field Names

| Category | Fields |
|----------|--------|
| **Identifiers** | `iati_identifier`, `reporting_org_ref`, `activity_status_code` |
| **Titles** | `title_narrative` |
| **Descriptions** | `description_narrative` |
| **Countries** | `recipient_country_code`, `recipient_country_narrative` |
| **Sectors** | `sector_code`, `sector_narrative`, `sector_vocabulary` |
| **Financial** | `transaction_value`, `transaction_value_currency`, `budget_value` |
| **Dates** | `activity_date`, `last_updated_datetime`, `transaction_date` |
| **Organizations** | `participating_org_ref`, `provider_org_ref`, `receiver_org_ref` |
| **Status** | `activity_status_code` (1-6) |
| **Results** | `result_type`, `result_title_narrative`, `result_indicator_*` |
