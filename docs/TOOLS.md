# UNHCR IATI MCP Server - Tools Documentation

This document provides comprehensive documentation for all tools available in the UNHCR IATI MCP Server. Each tool is designed to help you query, analyze, and export UNHCR's IATI data efficiently.

## Table of Contents

1. [How Natural Language Works](#how-natural-language-works)
2. [Tool Categories](#tool-categories)
3. [Tool Reference](#tool-reference)
4. [Query Syntax Reference](#query-syntax-reference)
5. [Field Names Reference](#field-names-reference)
6. [Tips for Effective Queries](#tips-for-effective-queries)
7. [Context Window Optimization](#context-window-optimization)

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
| **Export** | 3 tools | Export data in various formats |
| **Health & Monitoring** | 5 tools | Monitor server and API health |
| **Code Resolution** | 6 tools | Resolve and validate IATI codes |

**Total: 33 tools**

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

#### `unhcr_activity_by_sector`
Filter activities by sector code.

**Parameters:** `sector_code` (required), `rows` (default: 100), `start` (default: 0)

**Example:** `unhcr_activity_by_sector(sector_code="12220")` - Health sector

---

#### `unhcr_activity_by_year`
Filter activities by year.

**Parameters:** `year` (required), `max_records` (default: 10000)

**Example:** `unhcr_activity_by_year(year=2024)`

---

#### `unhcr_activity_by_identifier`
Filter by IATI identifier components.

**Parameters:** `year`, `programme`, `country_code`, `operation`, `rows` (default: 100), `start` (default: 0)

**Example:** `unhcr_activity_by_identifier(year=2024, programme="MENA")`

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

#### `unhcr_top_donors`
Get top N donors by contribution amount.

**Parameters:** `top_n` (default: 20), `max_records` (default: 10000)

**Example:** `unhcr_top_donors(top_n=10)`

---

#### `unhcr_top_donors_by_country`
Get main donors by country with contribution amounts.

**Parameters:** `country_code`, `top_n` (default: 10), `year`, `max_records` (default: 10000)

**Example:** `unhcr_top_donors_by_country(country_code="SY", top_n=5)`

---

### Country Analysis Tools

#### `unhcr_top_countries`
Get top N countries by activity count.

**Parameters:** `top_n` (default: 20), `max_records` (default: 10000)

**Example:** `unhcr_top_countries(top_n=10)`

---

### Sector Analysis Tools

#### `unhcr_sector_summary`
Get sector distribution across UNHCR activities.

**Parameters:** `max_records` (default: 10000)

**Example:** `unhcr_sector_summary()`

---

#### `unhcr_most_funded_sectors`
Get most funded sectors per country with funding amounts.

**Parameters:** `country_code`, `top_n` (default: 10), `year`, `max_records` (default: 10000)

**Example:** `unhcr_most_funded_sectors(country_code="SY", top_n=5)`

---

### Result Framework Tools

#### `unhcr_budget_vs_expenditure`
Compare budget vs expenditure for financial tracking.

**Parameters:** `year`, `country_code`, `max_records` (default: 10000)

**Example:** `unhcr_budget_vs_expenditure(year=2025, country_code="SY")`

---

#### `unhcr_indicator_trends`
Track indicator evolution over time for performance monitoring.

**Parameters:** `indicator_ref`, `country_code`, `start_year` (default: 2020), `end_year` (default: 2025), `max_records` (default: 10000)

**Example:** `unhcr_indicator_trends(country_code="SY", start_year=2023)`

---

#### `unhcr_partnership_analysis`
Analyze partnership levels across activities.

**Parameters:** `country_code`, `max_records` (default: 10000)

**Example:** `unhcr_partnership_analysis(country_code="SY")`

---

#### `unhcr_earmarking_breakdown`
Get earmarking type breakdown for transactions.

**Parameters:** `year`, `country_code`, `max_records` (default: 10000)

**Example:** `unhcr_earmarking_breakdown(year=2025)`

---

#### `unhcr_implementing_partners`
Get main implementing partners by country.

**Parameters:** `country_code`, `top_n` (default: 10), `max_records` (default: 10000)

**Example:** `unhcr_implementing_partners(country_code="SY", top_n=5)`

---

#### `unhcr_analytical_questions_summary`
Get summary of all 7 core analytical questions.

**Parameters:** `country_code`, `year`

**Example:** `unhcr_analytical_questions_summary(country_code="SY", year=2024)`

---



### Export Tools

#### `unhcr_export_json`
Export UNHCR data as JSON.

**Parameters:** `collection` (required), `query` (optional), `max_records` (default: 10000)

**Example:** `unhcr_export_json(collection="activity", max_records=5000)`

---

#### `unhcr_export_csv`
Export UNHCR data as CSV.

**Parameters:** `collection` (required), `query` (optional), `max_records` (default: 10000)

**Example:** `unhcr_export_csv(collection="activity", max_records=5000)`

---

#### `unhcr_bulk_extract`
Bulk extract data from multiple IATI collections.

**Parameters:** `collections` (required), `format` (default: "json"), `max_records_per_collection` (default: 10000)

**Example:** `unhcr_bulk_extract(collections=["activity", "transaction"], format="json")`

---

### Health & Monitoring Tools

#### `health_check`
Check the health status of the server.

**Parameters:** None

**Example:** `health_check()`

---

#### `system_status`
Check the status of all system components.

**Parameters:** None

**Example:** `system_status()`

---

#### `datastore_ping`
Test connection to IATI Datastore.

**Parameters:** None

**Example:** `datastore_ping()`

---

#### `api_limits`
Get API rate limit information.

**Parameters:** None

**Example:** `api_limits()`

---

#### `metrics`
Get Prometheus metrics for the server.

**Parameters:** None

**Example:** `metrics()`

---

### Code Resolution Tools

Access IATI code lookup tables (41 tables) to resolve codes to human-readable values.

#### `resolve_code`
Resolve an IATI code to its human-readable name and metadata.

**Parameters:** `code_type` (required), `code` (required), `table` (optional)

**Example:** `resolve_code(code_type="country", code="SYR")` → `{"code": "SYR", "name": "Syrian Arab Republic", ...}`

---

#### `validate_code`
Validate if an IATI code exists in a code table.

**Parameters:** `code_type` (required), `code` (required), `table` (optional)

**Example:** `validate_code(code_type="sector", code="12220")` → `{"valid": true, "name": "Basic health care"}`

---

#### `search_code_table`
Search an IATI code table by name or description.

**Parameters:** `code_type` (required), `query` (required), `limit` (default: 20), `table` (optional)

**Example:** `search_code_table(code_type="sector", query="health")` → Finds all health-related sectors

---

#### `list_code_table`
List all entries in an IATI code table with pagination.

**Parameters:** `code_type` (required), `limit` (default: 100), `offset` (default: 0), `table` (optional)

**Example:** `list_code_table(code_type="country", limit=10)` → First 10 countries

---

#### `batch_resolve_codes`
Resolve multiple IATI codes in a single call.

**Parameters:** `code_type` (required), `codes` (required), `table` (optional)

**Example:** `batch_resolve_codes(code_type="country", codes=["SYR", "KEN", "ETH"])` → Resolves 3 country codes

**Note:** Code tables are loaded on-demand (lazy loading) and cached for performance. The 41 IATI code tables include: country, sector, organisation, financial, geographic, policy, result framework, and SDG codes.

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

## Context Window Optimization

The MCP server has been optimized to minimize context window usage when loading tools:

- **~55K tokens** total for all tool and resource definitions (reduced from ~91K tokens)
- **33 tools** with concise 1-2 sentence docstrings
- **17 resources** (reduced from 63 by consolidating code table access)

### Key Optimizations:

1. **Short docstrings**: All tool docstrings reduced from 500-1000+ characters to <100 characters
2. **Removed redundant resources**: 44 code table resources removed (access via code resolution tools instead)
3. **Lazy loading**: Code tables load on-demand when first accessed, not at startup

### For Small Context Windows:

If you're using a model with a small context window (32K-64K tokens):
- Use specific tools by name rather than listing all tools
- Access code tables via `resolve_code`, `list_code_table`, etc. (not as direct resources)
- Request smaller result sets using `max_records` parameters
- Avoid calling `list_tools` or `list_resources` unless necessary

### Available:
- **Tools**: 33 total (~40K tokens)
- **Resources**: 17 total (~15K tokens)
- **Total**: ~55K tokens for definitions, leaving room for conversation

---

*Last Updated: July 6, 2025*
