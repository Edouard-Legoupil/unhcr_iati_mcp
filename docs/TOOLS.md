# UNHCR IATI MCP Server - Tools Documentation

This document provides comprehensive documentation for all tools available in the UNHCR IATI MCP Server. Each tool is designed to help you query, analyze, and export UNHCR's IATI data efficiently.

## Table of Contents

1. [How Natural Language Works](#how-natural-language-works)
2. [Tool Categories](#tool-categories)
3. [Tool Reference](#tool-reference)
4. [Query Syntax Reference](#query-syntax-reference)
5. [Field Names Reference](#field-names-reference)
6. [Tips for Effective Queries](#tips-for-effective-queries)

---

## How Natural Language Works

The UNHCR IATI MCP Server is designed to work seamlessly with AI assistants (like Claude, ChatGPT, or HuggingChat). When you ask questions in plain English, the AI assistant automatically converts your requests into the appropriate tool calls with the correct parameters.

### Examples

Instead of learning Solr query syntax or tool parameters, you can simply ask:

- **Simple questions:**
  - "Show me UNHCR projects in Afghanistan"
  - "What health projects does UNHCR have?"
  - "Get the latest activities from UNHCR"

- **Complex queries:**
  - "Find UNHCR education projects in Kenya with budgets over $1 million"
  - "Show me health and WASH projects in Syria from 2024"
  - "What are the top 10 donors to UNHCR's refugee programs?"

- **Specific lookups:**
  - "Get activity XM-DAC-41121-ACT-001"
  - "Show me details for project GB-GOV-1-12345"
  - "What is UNHCR's total budget for 2024?"

The AI assistant understands your intent and automatically:
1. Identifies which tool(s) to use
2. Constructs the appropriate query
3. Handles pagination and filtering
4. Returns the results in a structured format

---

## Tool Categories

| Category | Tools | Purpose |
|----------|-------|---------|
| **Activity** | 6 tools | Query and filter UNHCR activities |
| **Transaction** | 2 tools | Access and search financial transactions |
| **Budget** | 1 tool | Access planned funding allocations |
| **Donor Analysis** | 4 tools | Analyze donor contributions and patterns |
| **Country Analysis** | 5 tools | Analyze activities by country/region |
| **Sector Analysis** | 3 tools | Analyze activities by humanitarian sector |
| **SDG Analysis** | 2 tools | Analyze Sustainable Development Goals alignment |
| **Portfolio** | 2 tools | Get overview and summary statistics |
| **Export** | 4 tools | Export data in various formats |
| **Health & Monitoring** | 6 tools | Monitor server and API health |

**Total: 35 tools**

---

## Tool Reference

### Activity Tools

#### `unhcr_activities`
List all UNHCR activities with pagination.

**Parameters:** `rows` (default: 100), `start` (default: 0)

**Example:** `unhcr_activities(rows=10)` - Get first 10 activities

---

#### `unhcr_activity`
Get a specific activity by IATI identifier.

**Parameters:** `iati_identifier` (required)

**Example:** `unhcr_activity(iati_identifier="XM-DAC-41121-ACT-001")`

---

#### `unhcr_activity_by_country`
Filter activities by recipient country code.

**Parameters:** `country_code` (required), `rows` (default: 100), `start` (default: 0)

**Example:** `unhcr_activity_by_country(country_code="AF", rows=50)` - Afghanistan activities

---

#### `unhcr_activity_by_region`
Filter activities by geographic region.

**Parameters:** `region` (required), `rows` (default: 100)

**Example:** `unhcr_activity_by_region(region="Middle East")`

---

#### `unhcr_activity_by_sector`
Filter activities by sector code.

**Parameters:** `sector_code` (required), `rows` (default: 100)

**Example:** `unhcr_activity_by_sector(sector_code="12220")` - Health sector

---

#### `unhcr_activity_by_year`
Filter activities by year.

**Parameters:** `year` (required), `rows` (default: 100)

**Example:** `unhcr_activity_by_year(year=2024)`

---

#### `unhcr_activity_search`
Advanced Solr queries on activities.

**Parameters:** `query` (required), `rows` (default: 10), `start` (default: 0), `fields`, `sort`

**Example:** `unhcr_activity_search(query="recipient_country_code:KE AND sector_code:122*", rows=50)`

---

### Transaction Tools

#### `unhcr_transactions`
List all UNHCR transactions.

**Parameters:** `year`, `rows` (default: 100), `start` (default: 0)

**Example:** `unhcr_transactions(year=2024, rows=50)`

---

#### `unhcr_transaction_search`
Search transactions with custom Solr query.

**Parameters:** `query` (required), `rows` (default: 10), `start` (default: 0)

**Example:** `unhcr_transaction_search(query="provider_org_ref:DEU")` - From Germany

---

### Budget Tools

#### `unhcr_budgets`
List all UNHCR budgets.

**Parameters:** `year`, `rows` (default: 100), `start` (default: 0)

**Example:** `unhcr_budgets(year=2024)`

---

### Donor Analysis Tools

#### `unhcr_donors`
Get information about donors to UNHCR.

**Parameters:** `rows` (default: 50)

---

#### `unhcr_top_donors`
Get top N donors by contribution amount.

**Parameters:** `top_n` (default: 10)

**Example:** `unhcr_top_donors(top_n=10)`

---

#### `unhcr_donor_breakdown`
Get donor contribution breakdown.

**Parameters:** `year`

---

#### `unhcr_donor_trends`
Analyze donor contribution trends over time.

**Parameters:** `years` (default: 5), `top_n` (default: 10)

---

### Country Analysis Tools

#### `unhcr_countries`
Get information about countries where UNHCR operates.

**Parameters:** `rows` (default: 50)

---

#### `unhcr_country_summary`
Get summary statistics by country.

**Parameters:** `year`

---

#### `unhcr_country_financing`
Get financial information by country.

**Parameters:** `year`

---

#### `unhcr_country_dashboard`
Get comprehensive country dashboard.

**Parameters:** `country_code` (required)

**Example:** `unhcr_country_dashboard(country_code="AF")`

---

#### `unhcr_top_countries`
Get top N countries by activity count or funding.

**Parameters:** `top_n` (default: 10), `by` ("count" or "value")

---

### Sector Analysis Tools

#### `unhcr_sectors`
Get information about humanitarian sectors.

**Parameters:** `rows` (default: 50)

---

#### `unhcr_sector_summary`
Get summary statistics by sector.

**Parameters:** `year`

---

#### `unhcr_top_sectors`
Get top N sectors by activity count or funding.

**Parameters:** `top_n` (default: 10), `by` ("count" or "value")

---

### SDG Analysis Tools

#### `unhcr_sdgs`
Get information about Sustainable Development Goals.

**Parameters:** `rows` (default: 17)

---

#### `unhcr_sdg_summary`
Get summary of UNHCR activities by SDG.

**Parameters:** `year`

---

### Portfolio Tools

#### `unhcr_portfolio_summary`
Get aggregate counts across all UNHCR data.

**Parameters:** None

---

#### `unhcr_dashboard`
Get comprehensive portfolio dashboard.

**Parameters:** None

---

### Export Tools

#### `unhcr_export_json`
Export data as JSON.

**Parameters:** `collection` (required), `query` (required), `rows` (default: 1000), `filename`

**Example:** `unhcr_export_json(collection="activity", query="reporting_org_ref:XM-DAC-41121", rows=5000)`

---

#### `unhcr_export_csv`
Export data as CSV.

**Parameters:** `collection` (required), `query` (required), `rows` (default: 1000), `fields`

---

#### `unhcr_export_xml`
Export data as XML.

**Parameters:** `collection` (required), `query` (required), `rows` (default: 1000)

---

#### `unhcr_bulk_extract`
Bulk extract from multiple collections.

**Parameters:** `collections` (required), `format` (required), `query`, `rows` (default: 1000)

**Example:** `unhcr_bulk_extract(collections="activity,transaction,budget", format="json")`

---

### Health & Monitoring Tools

#### `health_check`
Server health status.

**Parameters:** None

---

#### `system_status`
System component status.

**Parameters:** None

---

#### `datastore_ping`
Test IATI Datastore connection.

**Parameters:** None

---

#### `api_limits`
API rate limit information.

**Parameters:** None

---

#### `metrics`
Prometheus metrics endpoint.

**Parameters:** None

---

#### `cache_stats`
Cache statistics.

**Parameters:** None

---

## Query Syntax Reference

### Basic Queries

| Pattern | Example | Description |
|---------|---------|-------------|
| Field search | `reporting_org_ref:XM-DAC-41121` | Search specific field |
| All documents | `*:*` | Match all documents |
| Field exists | `reporting_org_ref:*` | Field must exist |

### Wildcard Searches

| Pattern | Example | Description |
|---------|---------|-------------|
| Prefix match | `title_narrative:health*` | Starts with "health" |
| Suffix match | `title_narrative:*refugee` | Ends with "refugee" |
| Contains | `title_narrative:*health*` | Contains "health" |

### Boolean Operators

| Pattern | Example | Description |
|---------|---------|-------------|
| AND | `country:AF AND sector:12220` | Both must match |
| OR | `country:AF OR country:KE` | Either must match |
| NOT | `sector:12220 NOT country:SYR` | First yes, second no |

### Range Queries

| Pattern | Example | Description |
|---------|---------|-------------|
| Numeric | `transaction_value:[1000000 TO *]` | >= 1,000,000 |
| Bounded | `transaction_value:[1000000 TO 5000000]` | 1M to 5M |
| Date | `last_updated_datetime:[2024-01-01 TO 2024-12-31]` | 2024 dates |
| Relative | `last_updated_datetime:[NOW-30DAYS TO NOW]` | Last 30 days |

### Special

| Pattern | Example | Description |
|---------|---------|-------------|
| Phrase | `title_narrative:"climate change"` | Exact phrase |
| Group | `country:(AF OR KE OR SYR)` | OR group |
| Boost | `title_narrative:climate^2` | Boost relevance |

---

## Field Names Reference

### Common Fields

| Category | Fields |
|----------|--------|
| **Identifiers** | `iati_identifier`, `reporting_org_ref` |
| **Titles** | `title_narrative` |
| **Descriptions** | `description_narrative` |
| **Countries** | `recipient_country_code`, `recipient_country_narrative` |
| **Sectors** | `sector_code`, `sector_narrative` |
| **Financial** | `transaction_value`, `budget_value` |
| **Dates** | `last_updated_datetime`, `activity_date` |
| **Status** | `activity_status_code` (1-6) |

---

## Tips for Effective Queries

1. **Start simple** - Ask clear, direct questions
2. **Be specific** - Include relevant details (country, sector, year)
3. **Iterate** - Refine queries based on initial results
4. **Use known identifiers** - Include codes when available
5. **Combine criteria** - Mix multiple filters for precision
6. **Use pagination** - Handle large result sets efficiently
7. **Check data quality** - Be aware of missing/incomplete data

---

*Last Updated: July 3, 2024*
