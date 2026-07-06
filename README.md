# UNHCR IATI MCP Server

A Model Context Protocol (MCP) server for accessing UNHCR's IATI (International Aid Transparency Initiative) data from the official IATI Datastore API.

## Overview

This MCP server provides AI agents and applications with structured access to UNHCR's humanitarian aid data, including:

- **Activities**: Projects and programs
- **Transactions**: Financial movements and disbursements  
- **Budgets**: Planned funding allocations
- **Donors**: Funding organizations
- **Countries**: Recipient countries and regions
- **Sectors**: Humanitarian sectors (health, education, WASH, etc.) with **vocabulary management**
- **Results**: Complete IATI result framework (Output, Outcome, Impact levels) with indicators
- **SDGs**: Sustainable Development Goals mapping

## 🎯 Key Features

### ✅ Sector Vocabulary Management

**CRITICAL**: Sector codes have different meanings across IATI vocabularies. The same code (e.g., "10") in vocabulary 10 (IASC) means something different from code "10" in vocabulary 98 (UNHCR-specific).

**Supported Vocabularies:**
- **98**: UNHCR-specific sectors (PRIMARY for UNHCR analysis)
- **10**: IASC Humanitarian Clusters
- **1**: OECD DAC CRS Purpose Codes (5-digit)
- **2**: OECD DAC CRS Purpose Codes (3-digit)
- **99**: Reporting Organisation (organisation-specific)

**Safety Features:**
- ✅ Automatic vocabulary detection and warnings
- ✅ Methods to group sectors by vocabulary (`get_sectors_by_vocabulary()`)
- ✅ Validation to prevent cross-vocabulary aggregation
- ✅ Comprehensive guidelines for correct analysis

### ✅ Result Framework Support

Complete support for IATI's hierarchical result framework:

**Result Levels:**
- **Impact (3)**: Long-term outcomes (global level)
- **Outcome (2)**: Medium-term results (country/operation level) - **16 UNHCR Operational Areas**
- **Output (1)**: Short-term deliverables (activity level)
- **Other (9)**: Another type of result

**UNHCR's 16 Operational Areas:**
1. Protection (OA1) | 2. Solutions (OA2) | 3. Health (OA3) | 4. Education (OA4)
5. Livelihoods (OA5) | 6. Shelter and Settlements (OA6) | 7. WASH (OA7) | 8. Food Security (OA8)
9. Multi-sector (OA9) | 10. Leadership/Coordination (OA10) | 11. Emergency Response (OA11) | 12. Advocacy/Legal (OA12)
13. Community Empowerment (OA13) | 14. Inclusion (OA14) | 15. Gender Equality (OA15) | 16. Age and Diversity (OA16)

**Indicator Support:**
- ✅ 5 measure types: Unit, Percentage, Nominal, Ordinal, Qualitative
- ✅ Baseline, target, and actual values
- ✅ Disaggregation dimensions (sex, age, disability, location, etc.)
- ✅ Progress percentage and deviation calculations
- ✅ Quantitative vs qualitative filtering

### ✅ Comprehensive Code Tables

All **41 IATI code lookup tables** are now embedded in the package:
- Activity codes (date type, scope, status)
- Organisation codes (identifier, registration agency, role, type)
- Geographic codes (country, region, location class)
- Financial codes (aid type, budget, flow type, earmarking, currency)
- Sector codes (sector, category, vocabulary)
- Policy codes (policy marker, humanitarian scope, clusters)
- Result codes (indicator, result types, indicator vocabulary)
- SDG codes (goals, targets)

**Features:**
- ✅ Pre-loaded essential tables at startup
- ✅ Lazy loading for all other tables
- ✅ In-memory caching for performance
- ✅ MCP resources for introspection (`unhcr://codes/metadata`, `unhcr://codes/available`, etc.)

## Table of Contents

1. [Architecture](#architecture)
2. [Project Structure](#project-structure)
3. [Quick Start](#quick-start)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [API Reference](#api-reference)
7. [Data Models](#data-models)
8. [Observability](#observability)
9. [Development](#development)
10. [Deployment](#deployment)
11. [Troubleshooting](#troubleshooting)
12. [License](#license)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     MCP Client (FastMCP)                        │
├─────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │   Tools      │  │  Resources    │  │   Observability   │ │
│  │              │  │               │  │                    │ │
│  │ - Activities │  │ - Donors     │  │ - Metrics         │ │
│  │ - Budgets    │  │ - Countries   │  │ - Logging         │ │
│  │ - Transactions││ - Portfolio   │  │ - Tracing         │ │
│  │ - Analytics  │  │ - Glossary    │  │                    │ │
│  │ - Health     │  │ - Schemas     │  │                    │ │
│  │ - Export     │  │               │  │                    │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐ │
│  │                IATI Client                           │ │
│  │  ┌────────────────────────────────────────────────┐  │ │
│  │  │  HTTPX Async Client with Retry Logic            │  │ │
│  │  │  - Connection pooling (max 50 connections)        │  │ │
│  │  │  - Rate limiting handling                        │  │ │
│  │  │  - Authentication (Ocp-Apim-Subscription-Key)    │  │ │
│  │  │  - Exponential backoff retries (5 attempts)       │  │ │
│  │  │  - Timeout handling (configurable, default 120s) │  │ │
│  │  └────────────────────────────────────────────────┘  │ │
│  └──────────────────────────────────────────────────────┘ │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐ │
│  │           IATI Datastore API (Solr-based)             │ │
│  │  https://api.iatistandard.org/datastore               │ │
│  │  - Activity collection (projects/programs)            │ │
│  │  - Transaction collection (financial movements)       │ │
│  │  - Budget collection (planned allocations)            │ │
│  │  - Organisation collection (publishing orgs)         │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
unhcr_iati_mcp/
├── src/
│   └── unhcr_iati_mcp/
│       ├── __init__.py                 # Package initialization
│       ├── server.py                   # FastMCP server entry point
│       ├── client.py                   # IATI API client with retry logic
│       ├── config.py                   # Pydantic settings configuration
│       │
│       ├── models/                     # Pydantic data models
│       │   ├── __init__.py
│       │   ├── activity.py              # Activity model
│       │   ├── budget.py                # Budget model
│       │   ├── transaction.py           # Transaction model
│       │   ├── donor.py                 # Donor model
│       │   ├── country.py               # Country model
│       │   ├── sector.py                # Sector model
│       │   ├── pagination.py            # Pagination utilities
│       │   ├── responses.py             # API response wrappers
│       │   ├── errors.py                # Error response models
│       │   └── generated/               # Auto-generated models (from samples)
│       │
│       ├── tools/                      # MCP tools
│       │   ├── __init__.py
│       │   ├── activities.py            # Activity query tools
│       │   ├── transactions.py          # Transaction query tools
│       │   ├── budgets.py               # Budget query tools
│       │   ├── donors.py                # Donor analysis tools
│       │   ├── countries.py             # Country analysis tools
│       │   ├── sectors.py               # Sector analysis tools
│       │   ├── analytics.py             # Portfolio analytics tools
│       │   ├── export.py                # Data export tools (CSV, JSON, XML)
│       │   └── health.py                # Health check and monitoring tools
│       │
│       ├── data/                        # Static data files
│       │   ├── __init__.py
│       │   └── codelists/               # IATI code lookup tables (41 .RData files)
│       │       ├── __init__.py          # Code tables documentation
│       │       └── *.RData              # RData files for all IATI code tables
│       │
│       ├── resources/                  # MCP resources (static reference data)
│       │   ├── __init__.py
│       │   ├── donors.py                # Donor code to name mapping
│       │   ├── countries.py             # Country reference data
│       │   ├── sectors.py               # Sector reference data and vocabulary management
│       │   ├── results.py               # Result framework and indicator resources
│       │   ├── sdgs.py                  # SDG reference data
│       │   ├── glossary.py              # IATI terminology glossary
│       │   ├── portfolio.py             # UNHCR portfolio metadata
│       │   ├── schemas.py               # Data schema definitions
│       │   └── code_tables.py           # All 41 IATI code lookup tables as MCP resources
│       │
│       └── observability/              # Monitoring and observability
│           ├── __init__.py
│           ├── logging.py               # Structured logging (structlog with JSON)
│           └── metrics.py               # Prometheus metrics (COUNTERS, HISTOGRAMS)
│
├── scripts/
│   └── generate_models.py              # Model generation script (datamodel-code-generator)
│
├── tests/
│   └── test_smoke.py                   # Basic test suite
│
├── docs/
│   ├── ARCHITECTURE.md                 # Architecture documentation
│   └── TOOLS.md                       # Tool inventory
│
├── Dockerfile                         # Container image definition
├── docker-compose.yml                 # Development stack (Docker Compose)
├── pyproject.toml                     # Python project configuration
├── .env.example                       # Environment variables template
└── README.md                          # This file
```

---

## Quick Start

### Prerequisites

- **Python**: 3.11+ (recommended: 3.12)
- **Package Manager**: Poetry or pip
- **Container Runtime**: Docker (optional, for containerized deployment)
- **API Key**: IATI Datastore subscription key (required)

### Installation

#### Using pip (recommended for development)

```bash
# Clone the repository
git clone <repository-url>
cd unhcr_iati_mcp

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your IATI API key
```

#### Using Poetry

```bash
# Clone the repository
git clone <repository-url>
cd unhcr_iati_mcp

# Install dependencies
poetry install

# Configure environment
cp .env.example .env
# Edit .env with your IATI API key
```

---

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Required
IATI_API_KEY="your-iati-subscription-key"
IATI_BASE_URL="https://api.iatistandard.org/datastore"
UNHCR_PUBLISHER_REF="XM-DAC-41121"

# Optional (with defaults shown)
TIMEOUT_SECONDS=120
PAGE_SIZE=1000
LOG_LEVEL="INFO"
```

**Note**: UNHCR's publisher reference in IATI is `XM-DAC-41121`. This is the standard identifier for UNHCR in the IATI registry.

### Configuration Options

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `IATI_API_KEY` | string | **Required** | IATI Datastore API subscription key |
| `IATI_BASE_URL` | string | `https://api.iatistandard.org/datastore` | Base URL for IATI Datastore API |
| `UNHCR_PUBLISHER_REF` | string | `XM-DAC-41121` | UNHCR's publisher reference in IATI |
| `TIMEOUT_SECONDS` | integer | `120` | HTTP request timeout in seconds |
| `PAGE_SIZE` | integer | `1000` | Default number of records per page |
| `LOG_LEVEL` | string | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

---

## Running the Server

### Development Mode

```bash
# Run the server
python -m unhcr_iati_mcp.server

# Or with module syntax
python -m src.unhcr_iati_mcp.server

# With explicit logging level
LOG_LEVEL=DEBUG python -m unhcr_iati_mcp.server

# With custom port (if supported by FastMCP)
# Note: FastMCP uses MCP protocol, port configuration depends on client
```

### Docker Deployment

#### Build the Image

```bash
# Build using docker-compose
docker-compose build

# Or build manually
docker build -t unhcr-iati-mcp:latest .
```

#### Run the Container

```bash
# Using docker-compose
docker-compose up -d

# With environment variables
docker-compose run --env-file .env mcp

# Manual docker run
docker run -d \
  --name unhcr-iati-mcp \
  -p 8000:8000 \
  -e IATI_API_KEY=your-key \
  -e IATI_BASE_URL=https://api.iatistandard.org/datastore \
  -e UNHCR_PUBLISHER_REF=XM-DAC-41121 \
  unhcr-iati-mcp:latest
```

---

## Usage

### MCP Client Integration

The server exposes tools and resources via the Model Context Protocol (MCP). MCP clients can interact with the server using standard MCP calls.

#### Tools

All tools are prefixed with `unhcr_` and automatically filter results to UNHCR's data (publisher_ref: `XM-DAC-41121`).

**Activity Tools:**

| Tool | Description | Parameters |
|------|-------------|------------|
| `unhcr_activities` | List UNHCR activities with pagination | `rows`, `start` |
| `unhcr_activity` | Get a specific activity by IATI identifier | `iati_identifier` |
| `unhcr_activity_by_country` | Filter activities by country code (ISO 2-letter) | `country_code`, `rows` |
| `unhcr_activity_by_sector` | Filter activities by sector code | `sector_code`, `rows` |
| `unhcr_activity_by_year` | Filter activities by year | `year` |

**Transaction Tools:**

| Tool | Description | Parameters |
|------|-------------|------------|
| `unhcr_transactions` | List all UNHCR transactions | `year` (optional) |
| `unhcr_transaction_search` | Search transactions with custom Solr query | `query` |

**Budget Tools:**

| Tool | Description | Parameters |
|------|-------------|------------|
| `unhcr_budgets` | List all UNHCR budgets | `year` (optional) |

**Analysis Tools:**

| Tool | Description | Parameters |
|------|-------------|------------|
| `unhcr_top_donors` | Get top N donors by contribution amount | `top_n` |
| `unhcr_top_countries` | Get top N countries by activity count | `top_n` |
| `unhcr_sector_summary` | Get sector distribution across activities | - |
| `unhcr_portfolio_summary` | Get aggregate counts (activities, budgets, transactions) | - |

**Export Tools:**

| Tool | Description | Parameters |
|------|-------------|------------|
| `unhcr_export_json` | Export data as JSON | `collection`, `query` |
| `unhcr_export_csv` | Export data as CSV | `collection`, `query` |
| `unhcr_bulk_extract` | Bulk extract from multiple collections | `collections`, `format` |

**Health & Monitoring Tools:**

| Tool | Description | Parameters |
|------|-------------|------------|
| `health_check` | Server health status | - |
| `system_status` | System component status | - |
| `datastore_ping` | Test IATI Datastore connection | - |
| `api_limits` | API rate limit information | - |
| `metrics` | Prometheus metrics endpoint | - |
| `cache_stats` | Cache statistics (if Redis enabled) | - |

#### Resources

Static and reference data accessible via MCP resource URIs:

| URI | Description | Format |
|-----|-------------|--------|
| `unhcr://donors` | Donor code to name mapping | JSON object |
| `unhcr://countries` | Country reference data | JSON object |
| `unhcr://sectors` | UNHCR-specific sector code to name mapping (Vocabulary 98) | JSON object |
| `unhcr://sector_vocabularies` | Metadata about all IATI sector vocabularies with warnings | JSON object |
| `unhcr://sector_analysis_guidelines` | Comprehensive guidelines for correct sector data analysis | JSON object |
| `unhcr://sector_vocabulary_warnings` | Quick-reference warnings for each vocabulary | JSON object |
| `unhcr://result_types` | IATI result type codes (Output, Outcome, Impact, Other) | JSON object |
| `unhcr://indicator_measures` | IATI indicator measure codes (Unit, Percentage, Nominal, Ordinal, Qualitative) | JSON object |
| `unhcr://result_areas` | UNHCR's 16 Operational Areas (OA) at outcome level | JSON object |
| `unhcr://result_analysis_guidelines` | Guidelines for correct result data analysis | JSON object |
| `unhcr://disaggregation_dimensions` | Common disaggregation dimensions (sex, age, disability, etc.) | JSON object |
| `unhcr://sdgs` | Sustainable Development Goals mapping | JSON object |
| `unhcr://glossary` | IATI terminology glossary | JSON object |
| `unhcr://portfolio` | UNHCR portfolio metadata | JSON object |
| `unhcr://schemas` | Data schema definitions | JSON object |
| `unhcr://codes/metadata` | Metadata about all 41 IATI code tables | JSON object |
| `unhcr://codes/available` | List of all available code table names | JSON array |
| `unhcr://codes/essential` | List of essential (pre-loaded) code tables | JSON array |
| `unhcr://codes/cache_status` | Current status of the code table cache | JSON object |
| `unhcr://codes/*` | All 41 IATI code lookup tables (activity, organisation, geographic, financial, sector, policy, result) | JSON array |

### Example Usage

#### Python (with MCP client library)

```python
import asyncio
from mcp import Client

async def main():
    # Connect to the server (URL depends on your setup)
    client = Client("http://localhost:8000")
    
    # Call a tool
    result = await client.call_tool("unhcr_activities", {"rows": 50})
    print(f"Found {len(result['response']['docs'])} activities")
    
    # Get top donors
    donors = await client.call_tool("unhcr_top_donors", {"top_n": 10})
    print(f"Top donors: {donors}")
    
    # Get portfolio summary
    summary = await client.call_tool("unhcr_portfolio_summary", {})
    print(f"Summary: {summary}")

asyncio.run(main())
```

#### JavaScript/TypeScript (with MCP client)

```javascript
import { Client } from "@modelcontextprotocol/sdk";

const client = new Client("http://localhost:8000");

// Call a tool
const result = await client.callTool("unhcr_activities", { rows: 50 });
console.log(`Found ${result.response.docs.length} activities`);

// Get specific activity
const activity = await client.callTool("unhcr_activity", {
  iati_identifier: "XM-DAC-41121-ACT-001"
});
console.log(activity);
```

---

## API Reference

### IATIClient API

The `IATIClient` class in `client.py` provides the core API interaction layer:

```python
from unhcr_iati_mcp.client import IATIClient

client = IATIClient()

# Query with pagination
# Returns: dict with 'response' key containing 'docs' array and 'numFound'
data = await client.query(
    collection="activity",
    q='reporting_org_ref:"XM-DAC-41121"',
    rows=100,
    start=0,
    fl="*"  # or specific fields: "iati_identifier,title_narrative"
)

# Fetch all results (handles pagination automatically)
data = await client.fetch_all(
    collection="transaction",
    q='reporting_org_ref:"XM-DAC-41121"',
    max_records=10000  # optional limit
)

# Fetch a single page
data = await client.fetch_page(
    collection="budget",
    q='reporting_org_ref:"XM-DAC-41121"',
    page=0  # 0-indexed page number
)

# Convenience methods for specific collections
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

---

## Data Models

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
```

### Sector Models

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
```

### Result Framework Models

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

class Indicator(BaseModel):
    indicator_ref: Optional[str]
    indicator_title_narrative: str
    indicator_measure: str  # 1=Unit, 2=Percentage, 3=Nominal, 4=Ordinal, 5=Qualitative
    baseline_value: Optional[str]
    period_target_value: Optional[str]
    period_actual_value: Optional[str]

class UNHCRResultArea(BaseModel):
    code: str  # OA1-OA16
    name: str  # Protection, Solutions, Health, Education, etc.
```

### Response Models

```python
from unhcr_iati_mcp.models.responses import APIResponse
from unhcr_iati_mcp.models.errors import ErrorResponse

# Generic API response wrapper
class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    message: str | None = None

# Error response
class ErrorResponse(BaseModel):
    error_type: str
    message: str
    details: dict = {}
```

---

## Observability

### Structured Logging

The server uses `structlog` for structured JSON logging:

```python
from unhcr_iati_mcp.observability.logging import get_logger

logger = get_logger(__name__)

# Log with context
logger.info("Processing request", 
            request_id="abc-123", 
            collection="activity",
            start=0,
            rows=100)

# Log errors
logger.error("API error", 
              error="Timeout",
              collection="transaction",
              retry_count=3)
```

**Log Format (JSON):**
```json
{
  "timestamp": "2024-07-03T10:30:00.123456Z",
  "level": "INFO",
  "logger": "unhcr_iati_mcp.client",
  "event": "Querying activity",
  "request_id": "abc-123",
  "collection": "activity",
  "start": 0,
  "rows": 100
}
```

### Prometheus Metrics

Metrics for monitoring server health and performance:

```python
from unhcr_iati_mcp.observability.metrics import (
    monitor_datastore,
    complete_datastore,
    datastore_error,
    prometheus_metrics
)

# These are automatically tracked in client operations
# Access metrics via the 'metrics' tool
```

**Available Metrics:**

| Metric | Type | Description | Labels |
|--------|------|-------------|--------|
| `iati_datastore_requests_total` | Counter | Total API requests | collection, status |
| `iati_datastore_latency_seconds` | Histogram | Request latency | collection |
| `iati_datastore_errors_total` | Counter | Error counts | collection, error_type |



---

## Natural Language Query Examples

The MCP server is designed to work seamlessly with AI assistants that can translate natural language questions into structured tool calls. Here are examples of questions you can ask:

### Activity Queries

**Natural Language:**
- "Show me UNHCR projects in Afghanistan"
- "What are the most recent UNHCR activities?"
- "Find UNHCR health projects in Kenya"
- "Get details for activity XM-DAC-41121-ACT-001"
- "What activities does UNHCR have in Uganda?"

**AI translates to:**
```python
# "Show me UNHCR projects in Afghanistan"
await client.call_tool("unhcr_activity_by_country", {"country_code": "AF"})

# "What are the most recent UNHCR activities?"
await client.call_tool("unhcr_activities", {"rows": 10, "start": 0})

# "Find UNHCR health projects in Kenya"
await client.call_tool("unhcr_activity_search", {
    "query": "recipient_country_code:KE AND sector_code:122*",
    "rows": 50
})
```

### Financial Queries

**Natural Language:**
- "What is the total budget for UNHCR projects in 2024?"
- "Show me transactions from Germany to UNHCR"
- "What are the top donors to UNHCR?"
- "Get budget breakdown by sector"

**AI translates to:**
```python
# "What is the total budget for UNHCR projects in 2024?"
await client.call_tool("unhcr_budgets", {"year": 2024})

# "Show me transactions from Germany to UNHCR"
await client.call_tool("unhcr_transaction_search", {
    "query": "provider_org_ref:DEU"
})

# "What are the top donors to UNHCR?"
await client.call_tool("unhcr_top_donors", {"top_n": 10})
```

### Sector and Geographic Analysis

**Natural Language:**
- "What sectors does UNHCR work in?"
- "Show me UNHCR education projects"
- "Which countries receive the most UNHCR funding?"
- "Get sector distribution for UNHCR activities"
- "What is UNHCR's sector vocabulary 98?"
- "What are the warnings about sector vocabulary aggregation?"

**AI translates to:**
```python
# "What sectors does UNHCR work in?"
await client.call_tool("unhcr_sector_summary", {})

# "Show me UNHCR education projects"
await client.call_tool("unhcr_activity_by_sector", {
    "sector_code": "123",  # 123 = Education
    "rows": 100
})

# "Which countries receive the most UNHCR funding?"
await client.call_tool("unhcr_top_countries", {"top_n": 15})

# "What is UNHCR's sector vocabulary 98?"
# Access the sector_vocabularies resource
vocabularies = await client.read_resource("unhcr://sector_vocabularies")
unhcr_vocab = vocabularies.get("98")

# "What are the warnings about sector vocabulary aggregation?"
guidelines = await client.read_resource("unhcr://sector_analysis_guidelines")
warnings = guidelines.get("general_rules", {}).get("rule_1", {})
```

### Result Framework Queries

**Natural Language:**
- "What are UNHCR's output-level results?"
- "Show me outcome indicators for UNHCR projects"
- "What are the 16 UNHCR Operational Areas?"
- "Get progress tracking for UNHCR indicators"
- "Show me indicators with disaggregation by sex and age"

**AI translates to:**
```python
# "What are UNHCR's output-level results?"
# Filter activities by result type = 1 (Output)
await client.call_tool("unhcr_activities", {"rows": 100})
# Then filter results by type in the response

# "Show me outcome indicators for UNHCR projects"
# Outcome = result type 2
activities = await client.call_tool("unhcr_activities", {"rows": 100})
for activity in activities["response"]["docs"]:
    results_data = activity.get("result_type", [])
    indicators = activity.get("result_indicator_title_narrative", [])
    
# "What are the 16 UNHCR Operational Areas?"
result_areas = await client.read_resource("unhcr://result_areas")

# "Get progress tracking for UNHCR indicators"
# Use the result framework resources
result_types = await client.read_resource("unhcr://result_types")
indicator_measures = await client.read_resource("unhcr://indicator_measures")

# "Show me indicators with disaggregation by sex and age"
# Check disaggregation dimensions resource
dimensions = await client.read_resource("unhcr://disaggregation_dimensions")
```

### Advanced Queries

**Natural Language:**
- "Find UNHCR projects about climate change and refugees"
- "Show me high-budget health projects in Syria"
- "Get activities updated in the last 30 days"
- "What are UNHCR's active projects?"

**Solr Query Syntax for Advanced Users:**

```python
# Full-text search
await client.call_tool("unhcr_activity_search", {
    "query": "title_narrative:climate* AND description_narrative:refugee*"
})

# Budget filter
await client.call_tool("unhcr_activity_search", {
    "query": "recipient_country_code:SYR AND transaction_value:[1000000 TO *]"
})

# Date filter
await client.call_tool("unhcr_activity_search", {
    "query": "last_updated_datetime:[NOW-30DAYS TO NOW]"
})

# Status filter
await client.call_tool("unhcr_activity_search", {
    "query": "activity_status_code:2"  # 2 = Implementation
})
```

### Solr Query Syntax Reference

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
| **Sectors** | `sector_code`, `sector_narrative` |
| **Financial** | `transaction_value`, `transaction_value_currency`, `budget_value` |
| **Dates** | `activity_date`, `last_updated_datetime`, `transaction_date` |
| **Organizations** | `participating_org_ref`, `provider_org_ref`, `receiver_org_ref` |
| **Status** | `activity_status_code` (1-6) |

---

## 📚 Best Practices & Common Pitfalls

### Sector Data Analysis

**❌ DON'T:**
```python
# WRONG: Aggregating across different vocabularies
from collections import Counter
sector_counter = Counter()
for activity in activities:
    for code in activity["sector_code"]:
        sector_counter[code] += 1  # This is WRONG!
```

**✅ DO:**
```python
# CORRECT: Group by vocabulary first
from collections import defaultdict
sectors_by_vocab = defaultdict(lambda: defaultdict(int))
for activity in activities:
    for code, vocab in zip(activity["sector_code"], activity["sector_vocabulary"]):
        sectors_by_vocab[vocab][code] += 1

# Then analyze each vocabulary separately
for vocab, sectors in sectors_by_vocab.items():
    print(f"Vocabulary {vocab}: {dict(sectors)}")
```

### Result Framework Analysis

**✅ DO:**
```python
# Use the Activity model's built-in methods
activity = Activity(**activity_data)

# Get results with their indicators (SAFEST approach)
results_with_indicators = activity.get_results_with_indicators()

# Group indicators by result type
indicators_by_type = activity.get_indicators_by_type()

# Filter to quantitative indicators only
quantitative = activity.get_quantitative_indicators()

# Calculate progress (using utility functions)
from unhcr_iati_mcp.resources.results import calculate_progress_percentage
progress = calculate_progress_percentage(
    baseline=50.0,
    target=100.0,
    actual=75.0
)  # Returns 50.0
```

**❌ DON'T:**
```python
# WRONG: Mixing result types without context
all_indicators = []
for activity in activities:
    all_indicators.extend(activity["result_indicator_measure"])
    all_indicators.extend(activity["result_indicator_baseline_value"])
    # This loses the relationship between indicators and results!
```

### Working with Code Tables

**✅ DO:**
```python
# Access code tables via MCP resources
# Essential tables are pre-loaded
countries = await client.read_resource("unhcr://codes/country")

# Or use the client directly
from unhcr_iati_mcp.resources.code_tables import _load_code_table
countries = _load_code_table("codeCountry")

# Check what tables are available
available = await client.read_resource("unhcr://codes/available")
metadata = await client.read_resource("unhcr://codes/metadata")
```

### Caching and Performance

**✅ DO:**
```python
# Code tables are cached automatically
# First call loads from disk, subsequent calls use cache
countries1 = _load_code_table("codeCountry")  # Loads from disk
countries2 = _load_code_table("codeCountry")  # Returns cached

# Check cache status
cache_status = await client.read_resource("unhcr://codes/cache_status")
print(f"Cache size: {cache_status['cache_size']} entries")
```

**✅ DO:** Use lazy loading for non-essential tables
```python
# Non-essential tables are loaded on-demand
# They are cached after first load
special_table = _load_code_table("codeSomeSpecialTable")
```

---

---

## Troubleshooting

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Server fails to start | Missing `IATI_API_KEY` | Set `IATI_API_KEY` environment variable |
| Import errors | Missing dependencies | Run `pip install -e .` |
| Connection timeout | Network issues | Check connection, increase `TIMEOUT_SECONDS` |
| Rate limit errors | Too many requests | Implement caching, use `fetch_all` with smaller batches |
| Authentication errors | Invalid API key | Verify your IATI API key is correct |
| Empty results | Incorrect filter | Check `UNHCR_PUBLISHER_REF` is set to `XM-DAC-41121` |
| Sector aggregation errors | Mixing vocabularies | Use `get_sectors_by_vocabulary()` to group by vocabulary first |
| Result framework parsing | Missing result fields | Use Activity model's `get_results_with_indicators()` method |
| Code table not found | Table not in data/codelists/ | Check available tables with `unhcr://codes/available` |
| Cache issues | Stale code table data | Use `reload_code_tables()` or restart server |
| Invalid indicator data | Non-numeric values for quantitative | Use `validate_indicator_data()` to check data quality |

### Debug Mode

Enable verbose logging to troubleshoot issues:

```bash
LOG_LEVEL=DEBUG python -m unhcr_iati_mcp.server
```

This will output detailed information about:
- HTTP requests and responses
- Query execution
- Retry attempts
- Error details

### Testing Connection

Test if the IATI API is accessible:

```python
import httpx
import os

async def test_connection():
    api_key = os.getenv("IATI_API_KEY")
    url = "https://api.iatistandard.org/datastore/activity/select"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers={"Ocp-Apim-Subscription-Key": api_key},
            params={"q": "reporting_org_ref:XM-DAC-41121", "rows": 1}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

# Run in Python REPL
import asyncio
asyncio.run(test_connection())
```

### Checking API Key

Verify your IATI API key is valid:

1. Go to https://developer.iatistandard.org/
2. Log in to your account
3. Check your subscription key
4. Test it with a simple curl request:

```bash
curl -H "Ocp-Apim-Subscription-Key: YOUR_API_KEY" \
  "https://api.iatistandard.org/datastore/activity/select?q=*:*&rows=1"
```

### Docker Issues

**Problem: Build fails**
```bash
# Make sure you have the correct Python version
docker --version
python --version

# Clean build
docker-compose build --no-cache
```

**Problem: Container exits immediately**
```bash
# Check logs
docker-compose logs mcp

# Run interactively to see errors
docker-compose run mcp bash
```

**Problem: Port already in use**
```bash
# Change port in docker-compose.yml
ports:
  - "8080:8000"  # Map to different host port
```

---

## Development Guidelines

### Coding Standards

1. **Imports**: Avoid circular imports by using a context module for shared state
2. **Naming**: Use snake_case for variables and functions, PascalCase for classes
3. **Type Hints**: Always include type hints for public functions
4. **Error Handling**: Always wrap external calls in try/except
5. **Logging**: Use structured logging with context
6. **Testing**: Add tests for all new functionality
7. **Documentation**: Update README and docstrings for new features

### Before Committing

- [ ] Run `pytest` to ensure all tests pass
- [ ] Run `python -m unhcr_iati_mcp.server` to verify server starts
- [ ] Test at least one tool manually
- [ ] Check for import errors
- [ ] Verify type hints are correct

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes
# Add tests
# Update documentation

# Run tests
pytest tests/

# Commit with descriptive message
git add .
git commit -m "feat: add your feature description

Generated by Mistral Vibe.
Co-Authored-By: Mistral Vibe <vibe@mistral.ai>"

# Push and create PR
git push origin feature/your-feature
```

---

## License

This project is licensed under the MIT License. See LICENSE file for details.

---
 

## Resources
 
- **IATI Documentation**: https://iatistandard.org/en/guidance/
- **FastMCP Documentation**: https://github.com/modelcontextprotocol/fastmcp
- [IATI Datastore API Documentation](https://developer.iatistandard.org/)
- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [MCP Authorization Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- [IATI Standard](https://iatistandard.org/)