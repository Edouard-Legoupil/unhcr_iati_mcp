# UNHCR IATI MCP Server

A Model Context Protocol (MCP) server for accessing UNHCR's IATI (International Aid Transparency Initiative) data from the official IATI Datastore API.

## Overview

This MCP server provides AI agents and applications with structured access to UNHCR's humanitarian aid data, including:

- **Activities**: Projects and programs
- **Transactions**: Financial movements and disbursements  
- **Budgets**: Planned funding allocations
- **Donors**: Funding organizations
- **Countries**: Recipient countries and regions
- **Sectors**: Humanitarian sectors (health, education, WASH, etc.)
- **SDGs**: Sustainable Development Goals mapping

## Table of Contents

1. [Architecture](#architecture)
2. [Project Structure](#project-structure)
3. [Quick Start](#quick-start)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [API Reference](#api-reference)
7. [Data Models](#data-models)
8. [Observability](#observability)
9. [Code Review Findings](#code-review-findings)
10. [Development](#development)
11. [Deployment](#deployment)
12. [Troubleshooting](#troubleshooting)
13. [License](#license)

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
│       ├── resources/                  # MCP resources (static reference data)
│       │   ├── __init__.py
│       │   ├── donors.py                # Donor code to name mapping
│       │   ├── countries.py             # Country reference data
│       │   ├── sectors.py               # Sector reference data
│       │   ├── sdgs.py                  # SDG reference data
│       │   ├── glossary.py              # IATI terminology glossary
│       │   ├── portfolio.py             # UNHCR portfolio metadata
│       │   └── schemas.py               # Data schema definitions
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
| `unhcr://sectors` | Sector code to name mapping | JSON object |
| `unhcr://sdgs` | Sustainable Development Goals mapping | JSON object |
| `unhcr://glossary` | IATI terminology glossary | JSON object |
| `unhcr://portfolio` | UNHCR portfolio metadata | JSON object |
| `unhcr://schemas` | Data schema definitions | JSON object |

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

Represents an IATI activity (project/program):

```python
from unhcr_iati_mcp.models.activity import Activity

class Activity(BaseModel):
    iati_identifier: str                          # Unique identifier
    title_narrative: List[str] = []               # Titles in multiple languages
    description_narrative: List[str] = []         # Descriptions
    recipient_country_code: List[str] = []        # ISO country codes
    sector_code: List[str] = []                   # Sector codes
    reporting_org_ref: List[str] = []             # Publishing organization
```

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

## Code Review Findings

### Executive Summary

This code review identified **16 issues** across the codebase, categorized as:
- **5 Critical Issues**: Must be fixed before production deployment
- **6 High Priority Issues**: Should be fixed for stability and reliability
- **5 Medium Priority Issues**: Nice-to-have improvements

The codebase has a **solid architectural foundation** with clean separation of concerns, good use of type safety, and excellent retry logic. However, there are **import and dependency issues** that prevent the server from running correctly.

---

### ✅ Strengths

1. **Clean Architecture**: Well-separated concerns with clear layers:
   - Client layer (HTTP interaction)
   - Tool layer (MCP capabilities)
   - Resource layer (static data)
   - Observability layer (monitoring)

2. **Type Safety**: Good use of Pydantic models for data validation

3. **Retry Logic**: Excellent implementation using tenacity:
   - Exponential backoff (1s to 16s)
   - 5 retry attempts
   - Handles timeouts, connection errors, rate limits, server errors

4. **Error Handling**: Custom error hierarchy for different failure modes

5. **Configuration**: Pydantic Settings with environment variable support

6. **Logging**: Structured logging with structlog and JSON output

7. **HTTP Client**: Properly configured with connection pooling (50 max, 20 keepalive)

8. **Project Structure**: Logical organization following best practices

---

### ❌ Critical Issues (Must Fix - Blocks Deployment)

#### Issue 1: Circular Import Problem

**Severity**: CRITICAL | **Files**: All tool files, server.py

**Description**:
The tool files import `mcp`, `iati_client`, and `unhcr_filter` from `server.py`, but `server.py` imports tools. This creates a circular import that causes `ImportError` at runtime.

**Evidence**:
```python
# server.py
from unhcr_iati_mcp import tools  # This triggers tool imports

# tools/activities.py
from unhcr_iati_mcp.server import mcp, iati_client, unhcr_filter
```

**Impact**:
- Server fails to start
- ImportError when trying to load tools

**Fix**:
Create a separate context module to hold shared state:

```python
# src/unhcr_iati_mcp/context.py (NEW FILE)
from fastmcp import FastMCP
from unhcr_iati_mcp.client import IATIClient
from unhcr_iati_mcp.config import settings

# Initialize shared state
mcp = FastMCP(name="unhcr-iati-mcp", description="IATI Datastore for UNHCR")
iati_client = IATIClient()

def unhcr_filter() -> str:
    return f'reporting_org_ref:"{settings.unhcr_publisher_ref}"'
```

Then update server.py:
```python
# server.py
from unhcr_iati_mcp.context import mcp, iati_client, unhcr_filter
from unhcr_iati_mcp.observability.logging import configure_logging

configure_logging()

# Register tools and resources
from unhcr_iati_mcp import tools
from unhcr_iati_mcp import resources

def main():
    mcp.run()
```

And update all tool files:
```python
# tools/activities.py
from unhcr_iati_mcp.context import mcp, iati_client, unhcr_filter
```

---

#### Issue 2: Undefined Variables in Tool Files

**Severity**: CRITICAL | **Files**: Multiple tool files

**Description**:
Tool files reference undefined variables: `client`, `publisher_filter()`, `UNHCR_REF`.

**Evidence**:
```python
# tools/activities.py (line 25)
return await client.activity_search(q=publisher_filter(), rows=rows, start=start)

# tools/donors.py (line 17)
tx = await client.fetch_all(collection="transaction", q=publisher_filter())

# tools/countries.py (line 9)
activities = await client.fetch_all(collection="activity", q=publisher_filter())
```

**Impact**:
- NameError at runtime
- Tools fail to execute

**Fix**:
Use the proper variables from context/server:
```python
# Use iati_client instead of client
# Use unhcr_filter() instead of publisher_filter()
# Use settings.unhcr_publisher_ref instead of UNHCR_REF

# Example fix for tools/activities.py:
return await iati_client.query(
    collection="activity",
    q=unhcr_filter(),
    rows=rows,
    start=start
)
```

---

#### Issue 3: Empty Files That Are Referenced

**Severity**: CRITICAL | **Files**: Multiple files

**Description**:
Several files are empty but are imported or referenced elsewhere in the codebase.

**Evidence**:
1. `src/unhcr_iati_mcp/observability/metrics.py` - Empty but referenced in `tools/health.py`
2. `src/unhcr_iati_mcp/tools/export.py` - Empty but imported in `tools/__init__.py`
3. `src/unhcr_iati_mcp/resources/countries.py` - Empty but imported in `resources/__init__.py`
4. `src/unhcr_iati_mcp/models/transaction.py` - Empty but model is referenced
5. `src/unhcr_iati_mcp/models/__init__.py` - Empty (should export models)

**Impact**:
- ImportError when trying to import from these files
- Missing functionality (metrics, export, caching)

**Fix**:
Either implement the missing functionality or remove the references:
- Implement metrics.py with Prometheus metrics
- Implement export.py with export tools
- Implement countries.py resource
- Implement transaction.py model
- Populate models/__init__.py with exports

---

#### Issue 4: Import Name Mismatches

**Severity**: CRITICAL | **Files**: tools/__init__.py

**Description**:
The `__init__.py` imports modules that don't exist or have different names.

**Evidence**:
```python
# tools/__init__.py
from . import activities
from . import transactions
from . import budgets
from . import donors
from . import sectors
from . import countries
from . import sdgs          # ❌ No such file (should be sectors?)
from . import analytics
from . import exports       # ❌ File is named export.py (singular)
from . import health
```

**Impact**:
- ImportError: cannot import name 'exports'
- ImportError: cannot import name 'sdgs'

**Fix**:
```python
# tools/__init__.py
from . import activities
from . import transactions
from . import budgets
from . import donors
from . import sectors
from . import countries
# from . import sdgs          # Comment out or create sdgs.py
from . import analytics
# from . import exports       # Comment out or rename export.py to exports.py
from . import health
```

---

#### Issue 5: Missing mcp Import in Resource Files

**Severity**: CRITICAL | **Files**: resources/countries.py, resources/sectors.py, resources/sdgs.py

**Description**:
Resource files use `@mcp.resource` decorator but don't import `mcp`.

**Evidence**:
```python
# resources/countries.py (EMPTY - but if it had content)
@mcp.resource("unhcr://countries")  # ❌ mcp is not defined
async def countries():
    return {}
```

**Impact**:
- NameError: name 'mcp' is not defined

**Fix**:
```python
# resources/countries.py
from unhcr_iati_mcp.server import mcp

@mcp.resource("unhcr://countries")
async def countries():
    return {}  # Implement or return empty for now
```

---

### ⚠️ High Priority Issues (Should Fix for Production)

#### Issue 6: Missing Cache Implementation

**Severity**: HIGH | **Files**: tools/health.py

**Description**:
Health tools reference `cache` and `redis` but no cache module exists.

**Evidence**:
```python
# tools/health.py (line 32)
return await cache.statistics()
```

**Impact**:
- NameError: name 'cache' is not defined
- cache_stats tool will fail

**Fix**:
Either implement caching or remove cache references:

**Option A**: Implement Redis cache
```python
# src/unhcr_iati_mcp/cache.py (NEW FILE)
import redis.asyncio as redis
from unhcr_iati_mcp.config import settings

class Cache:
    def __init__(self):
        self.client = redis.from_url(settings.redis_url)
    
    async def statistics(self) -> dict:
        info = await self.client.info()
        return {
            "keys": info.get("db0", {}).get("keys", 0),
            "memory_used": info.get("memory", {}).get("used_memory_human", "unknown")
        }

cache = Cache()
```

**Option B**: Remove cache references (simpler for now)
```python
# tools/health.py - Remove cache_stats tool or comment it out
```

---

#### Issue 7: Metrics Not Implemented

**Severity**: HIGH | **Files**: observability/metrics.py, tools/health.py

**Description**:
The metrics.py file is empty but tools/health.py references metrics functions.

**Evidence**:
```python
# tools/health.py (line 8-10)
from unhcr_iati_mcp.observability.metrics import (
    prometheus_metrics,
)

# tools/health.py (line 16)
return {"prometheus": prometheus_metrics().decode("utf-8")}
```

**Impact**:
- ImportError or AttributeError
- metrics tool will fail

**Fix**:
Implement metrics.py:

```python
# src/unhcr_iati_mcp/observability/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Request counters
datastore_requests = Counter(
    'iati_datastore_requests_total',
    'Total number of IATI Datastore requests',
    ['collection', 'status']
)

datastore_errors = Counter(
    'iati_datastore_errors_total',
    'Total number of IATI Datastore errors',
    ['collection', 'error_type']
)

# Latency tracking
datastore_latency = Histogram(
    'iati_datastore_latency_seconds',
    'Latency of IATI Datastore requests in seconds',
    ['collection']
)

def monitor_datastore(collection: str):
    """Called when a datastore request starts."""
    datastore_requests.labels(collection=collection, status='started').inc()

def complete_datastore(collection: str, status: str):
    """Called when a datastore request completes."""
    datastore_requests.labels(collection=collection, status=status).inc()

def datastore_error(collection: str, error_type: str):
    """Called when a datastore request fails."""
    datastore_errors.labels(collection=collection, error_type=error_type).inc()

def prometheus_metrics() -> bytes:
    """Generate Prometheus metrics."""
    return generate_latest()
```

---

#### Issue 8: Inconsistent Publisher Filter Usage

**Severity**: HIGH | **Files**: Multiple tool files

**Description**:
Different tool files use different methods for filtering UNHCR data:
- Some use `publisher_filter()` (undefined)
- Some use `unhcr_filter()` (from server.py)
- Some hardcode the filter string

**Evidence**:
```python
# tools/activities.py (line 13)
def publisher_filter() -> str:
    return f'reporting_org_ref:"XM-DAC-41121"'

# tools/donors.py (line 19)
q=publisher_filter()

# tools/transactions.py (line 15)
q = f'reporting_org_ref:"XM-DAC-41121"'

# server.py (line 21-25)
def unhcr_filter() -> str:
    return f'reporting_org_ref:"{settings.unhcr_publisher_ref}"'
```

**Impact**:
- Inconsistent filtering
- Potential data leakage if hardcoded value is wrong
- Duplicated code

**Fix**:
Standardize on `unhcr_filter()` from context/server:
```python
# Remove publisher_filter() from tools/activities.py
# Use unhcr_filter() everywhere

# tools/activities.py:
from unhcr_iati_mcp.context import mcp, iati_client, unhcr_filter

@mcp.tool(...)
async def unhcr_activities(rows: int = 100, start: int = 0):
    return await iati_client.query(
        collection="activity",
        q=unhcr_filter(),
        rows=rows,
        start=start
    )
```

---

#### Issue 9: Missing Type Hints

**Severity**: HIGH | **Files**: Multiple tool files

**Description**:
Many tool functions lack type annotations, making it harder to:
- Catch errors early
- Get IDE autocompletion
- Understand expected inputs/outputs

**Evidence**:
```python
# tools/donors.py (line 13-14)
async def unhcr_top_donors(top_n: int = 20):  # ❌ Missing return type

# tools/sectors.py (line 14)
async def unhcr_sector_summary():  # ❌ Missing parameter and return types

# tools/analytics.py (line 13)
async def unhcr_portfolio_summary():  # ❌ Missing return type
```

**Impact**:
- Reduced code quality
- Potential runtime errors
- Poor developer experience

**Fix**:
Add proper type hints:
```python
# tools/donors.py
from typing import Any, List, Tuple

@mcp.tool()
async def unhcr_top_donors(top_n: int = 20) -> List[Tuple[str, float]]:
    ...

# tools/sectors.py
from typing import Dict

@mcp.tool()
async def unhcr_sector_summary() -> Dict[str, int]:
    ...

# tools/analytics.py
from typing import Dict

@mcp.tool()
async def unhcr_portfolio_summary() -> Dict[str, int]:
    ...
```

---

#### Issue 10: Incomplete Error Handling

**Severity**: HIGH | **Files**: tools/analytics.py, tools/transactions.py, tools/budgets.py

**Description**:
Many tool functions lack try/except blocks, so API errors will propagate and crash the server.

**Evidence**:
```python
# tools/analytics.py (line 15-28)
async def unhcr_portfolio_summary():
    activities = await client.fetch_all("activity", publisher_filter())
    budgets = await client.fetch_all("budget", publisher_filter())
    transactions = await client.fetch_all("transaction", publisher_filter())
    return {
        "activities": len(activities),
        "budgets": len(budgets),
        "transactions": len(transactions)
    }
    # ❌ No error handling
```

**Impact**:
- Unhandled exceptions will crash the tool call
- Poor user experience
- No graceful degradation

**Fix**:
Add error handling with appropriate responses:
```python
from unhcr_iati_mcp.client import IATIError
from unhcr_iati_mcp.observability.logging import get_logger

logger = get_logger(__name__)

@mcp.tool()
async def unhcr_portfolio_summary():
    try:
        activities = await iati_client.fetch_all("activity", unhcr_filter())
        budgets = await iati_client.fetch_all("budget", unhcr_filter())
        transactions = await iati_client.fetch_all("transaction", unhcr_filter())
        return {
            "activities": len(activities),
            "budgets": len(budgets),
            "transactions": len(transactions)
        }
    except IATIError as e:
        logger.error("Portfolio summary failed", error=str(e))
        return {"error": str(e), "activities": 0, "budgets": 0, "transactions": 0}
    except Exception as e:
        logger.exception("Unexpected error in portfolio summary")
        return {"error": "Internal server error", "activities": 0, "budgets": 0, "transactions": 0}
```

---

### 📋 Medium Priority Issues (Nice to Fix)

#### Issue 11: Docker Configuration Incomplete

**Severity**: MEDIUM | **Files**: Dockerfile, docker-compose.yml

**Description**:
Docker configuration lacks several production-ready features.

**Evidence**:
```dockerfile
# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["python","-m","unhcr_iati_mcp.server"]
```

**Issues**:
- No environment variable passing
- No port exposure
- No non-root user
- No health checks
- No cleanup of apt cache

**Fix**:
```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy application code
COPY src/ src/
COPY .env .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Run the server
CMD ["python", "-m", "unhcr_iati_mcp.server"]
```

---

#### Issue 12: Incomplete Test Suite

**Severity**: MEDIUM | **Files**: tests/test_smoke.py

**Description**:
The test suite only has a trivial `assert True` test.

**Evidence**:
```python
# tests/test_smoke.py
def test_smoke():
    assert True
```

**Impact**:
- No actual test coverage
- No verification of functionality
- No regression protection

**Fix**:
Add comprehensive tests:

```python
# tests/test_client.py
import pytest
from unittest.mock import AsyncMock, patch
from unhcr_iati_mcp.client import IATIClient, IATIAuthenticationError

@pytest.mark.asyncio
async def test_client_query_success():
    """Test successful query."""
    mock_response = {"response": {"numFound": 5, "docs": [{"id": "1"}]}}
    
    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response
        
        client = IATIClient()
        result = await client.query("activity", "*", rows=10)
        
        assert result["response"]["numFound"] == 5
        assert len(result["response"]["docs"]) == 1

@pytest.mark.asyncio
async def test_client_authentication_error():
    """Test authentication error handling."""
    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 401
        
        client = IATIClient()
        
        with pytest.raises(IATIAuthenticationError):
            await client.query("activity", "*", rows=10)

# tests/test_tools.py
import pytest
from unhcr_iati_mcp.tools.activities import unhcr_activities

@pytest.mark.asyncio
async def test_unhcr_activities():
    """Test activities tool."""
    # Mock iati_client and mcp
    # Test tool execution
    pass
```

---

#### Issue 13: Resource URI Inconsistency

**Severity**: MEDIUM | **Files**: resources/*.py

**Description**:
Resource URIs should follow a consistent scheme. Currently some exist, some don't.

**Evidence**:
```python
# resources/donors.py
@mcp.resource("unhcr://donors")

# resources/glossary.py
@mcp.resource("unhcr://glossary")

# resources/portfolio.py
@mcp.resource("unhcr://portfolio")

# resources/countries.py (empty - URI unknown)
# resources/sectors.py (empty - URI unknown)
# resources/sdgs.py (empty - URI unknown)
```

**Impact**:
- Inconsistent resource discovery
- Potential conflicts

**Fix**:
Standardize URI scheme:
```python
# All resources should use: unhcr://<category>/<name>
# Or: unhcr://<name>

# resources/countries.py
@mcp.resource("unhcr://countries")

# resources/sectors.py
@mcp.resource("unhcr://sectors")

# resources/sdgs.py
@mcp.resource("unhcr://sdgs")
```

---

#### Issue 14: Model Generation Script References Missing Files

**Severity**: MEDIUM | **Files**: scripts/generate_models.py

**Description**:
The model generation script references sample files that don't exist.

**Evidence**:
```python
# scripts/generate_models.py
generate(
    input_="samples/activity.json",  # ❌ samples/ directory doesn't exist
    ...
)
```

**Impact**:
- Script won't run without creating samples directory and files

**Fix**:
Create samples directory and add sample files, or document the requirement:

```python
# scripts/generate_models.py
import os
from pathlib import Path

# Create samples directory if it doesn't exist
Path("samples").mkdir(exist_ok=True)

# Check if sample files exist, otherwise download them
def ensure_samples():
    sample_files = [
        "samples/activity.json",
        "samples/transaction.json", 
        "samples/budget.json"
    ]
    
    for file in sample_files:
        if not os.path.exists(file):
            # Download sample from IATI Datastore
            # Or provide instructions
            print(f"Sample file {file} not found. Please download sample data first.")
            print("Run: python scripts/download_samples.py")

ensure_samples()
```

---

#### Issue 15: Duplicate Dependency in pyproject.toml

**Severity**: MEDIUM | **Files**: pyproject.toml

**Description**:
The `structlog` dependency is listed twice.

**Evidence**:
```toml
# pyproject.toml
dependencies=[
  "fastmcp",
  "httpx",
  "pydantic",
  "pydantic-settings",
  "structlog",
  "prometheus-client",
  "tenacity",
  "redis",
  "structlog",  # ❌ Duplicate
  "python-dotenv"
]
```

**Impact**:
- None (pip handles duplicates)
- Minor cleanup issue

**Fix**:
```toml
dependencies=[
  "fastmcp",
  "httpx",
  "pydantic",
  "pydantic-settings",
  "structlog",
  "prometheus-client",
  "tenacity",
  "redis",
  "python-dotenv"
]
```

---

#### Issue 16: No Async Context Management for Cleanup

**Severity**: MEDIUM | **Files**: server.py

**Description**:
The IATIClient is created but never properly closed, leading to resource leaks.

**Evidence**:
```python
# server.py
iati_client = IATIClient()

# No cleanup on shutdown
```

**Impact**:
- HTTP connections may not be properly closed
- Resource leaks over time

**Fix**:
Use FastMCP's lifespan feature or add cleanup handler:

```python
# server.py
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastMCP):
    # Startup
    app.state.iati_client = IATIClient()
    yield
    # Shutdown
    await app.state.iati_client.close()

mcp = FastMCP(
    name="unhcr-iati-mcp",
    description="IATI Datastore for UNHCR",
    lifespan=lifespan
)

def unhcr_filter() -> str:
    return f'reporting_org_ref:"{settings.unhcr_publisher_ref}"'

def main():
    mcp.run()
```

---

## Code Review Summary

### Statistics

| Category | Count | Percentage |
|----------|-------|------------|
| Total Issues | 16 | 100% |
| Critical | 5 | 31.25% |
| High Priority | 6 | 37.5% |
| Medium Priority | 5 | 31.25% |

### Severity Breakdown

| Severity | Issues | Fix Priority |
|----------|--------|--------------|
| 🔴 CRITICAL | 5 | Must fix before deployment |
| 🟡 HIGH | 6 | Should fix for production |
| 🟢 MEDIUM | 5 | Nice to fix |

### Files Affected

| File | Issues |
|------|--------|
| `server.py` | 1 (circular import structure) |
| `tools/__init__.py` | 1 (import mismatches) |
| `tools/activities.py` | 2 (undefined variables) |
| `tools/donors.py` | 2 (undefined variables, type hints) |
| `tools/countries.py` | 2 (undefined variables, type hints) |
| `tools/sectors.py` | 2 (undefined variables, type hints) |
| `tools/analytics.py` | 2 (error handling, type hints) |
| `tools/transactions.py` | 2 (undefined variables, error handling) |
| `tools/budgets.py` | 2 (undefined variables, type hints) |
| `tools/health.py` | 2 (missing cache, metrics) |
| `tools/export.py` | 1 (empty file) |
| `observability/metrics.py` | 1 (empty file) |
| `resources/countries.py` | 1 (empty file) |
| `resources/sectors.py` | 1 (empty file) |
| `resources/sdgs.py` | 1 (empty file) |
| `models/transaction.py` | 1 (empty file) |
| `models/__init__.py` | 1 (empty file) |
| `Dockerfile` | 1 (incomplete config) |
| `docker-compose.yml` | 1 (incomplete config) |
| `pyproject.toml` | 1 (duplicate dependency) |
| `scripts/generate_models.py` | 1 (missing samples) |
| `tests/test_smoke.py` | 1 (incomplete tests) |

---

## Recommended Fix Order

1. **Fix Circular Imports** (Issue #1) - Creates a context module
2. **Fix Undefined Variables** (Issue #2) - Use proper imports from context
3. **Fix Import Mismatches** (Issue #4) - Correct tool __init__.py
4. **Fix Missing mcp Import** (Issue #5) - Add mcp import to resource files
5. **Implement metrics.py** (Issue #7) - Add Prometheus metrics
6. **Fix Publisher Filter** (Issue #8) - Standardize on unhcr_filter()
7. **Add Type Hints** (Issue #9) - Improve code quality
8. **Add Error Handling** (Issue #10) - Prevent crashes
9. **Fix Cache References** (Issue #6) - Implement or remove
10. **Implement Missing Files** (Issue #3) - export.py, transaction.py, etc.
11. **Update Docker Config** (Issue #11) - Production ready
12. **Add Tests** (Issue #12) - Improve coverage
13. **Fix Resource URIs** (Issue #13) - Standardize scheme
14. **Fix Model Generation** (Issue #14) - Add sample files
15. **Fix Dependencies** (Issue #15) - Remove duplicate
16. **Add Async Cleanup** (Issue #16) - Proper resource management

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

## Alternative Implementation Review

> **📚 See Also:** [docs/ALTERNATIVE_IMPLEMENTATION_REVIEW.md](docs/ALTERNATIVE_IMPLEMENTATION_REVIEW.md)

This project reviewed an alternative TypeScript/JavaScript implementation of an IATI MCP server located at `.arc/mcp-iati-main/`. That implementation provides several advanced features that could be incorporated into this Python implementation.

### Key Features from TypeScript Implementation

| Feature | Status | Priority | Description |
|---------|--------|----------|-------------|
| **HTTP Transport Mode** | ❌ Not Implemented | 🔴 High | Enables remote deployment over HTTP |
| **Built-in OAuth Server** | ❌ Not Implemented | 🔴 High | OAuth 2.1 with client credentials grant |
| **X-API-Key Header Support** | ❌ Not Implemented | 🔴 High | Compatibility with HuggingChat, etc. |
| **Health Check Endpoint** | ❌ Not Implemented | 🔴 High | Production monitoring |
| **Protected Resource Metadata** | ❌ Not Implemented | 🟡 Medium | OAuth spec compliance (RFC 9728) |
| **Dual Authentication** | ❌ Not Implemented | 🟡 Medium | Both OAuth and API key support |
| **Natural Language Documentation** | ✅ Partially | 🟡 Medium | Better user guidance |

### Recommended Implementation Plan

#### Phase 1: HTTP Transport Mode (2-4 hours)
Add support for HTTP-based MCP communication alongside the current STDIO mode:

```bash
# Use HTTP mode
MCP_TRANSPORT=http PORT=8000 python -m unhcr_iati_mcp.server

# Use STDIO mode (default)
python -m unhcr_iati_mcp.server
```

Benefits:
- Enables remote deployment
- Allows server to run as a standalone service
- Required for production use cases

#### Phase 2: Authentication (4-8 hours)
Implement OAuth 2.1 with built-in server and X-API-Key fallback:

```bash
# With built-in OAuth
USE_BUILTIN_OAUTH=true python -m unhcr_iati_mcp.server

# With X-API-Key header support
# Clients can use: Authorization: Bearer <token> OR X-API-Key: <api_key>
```

Benefits:
- Standards-compliant authentication
- Works with all MCP clients
- Simplified deployment (no external auth service needed)

#### Phase 3: Production Features (4-8 hours)
- Health check endpoint (`/health`)
- Protected Resource Metadata endpoint (`/.well-known/oauth-protected-resource`)
- Enhanced error handling with proper HTTP status codes
- Rate limiting and request logging

#### Phase 4: Documentation (2-4 hours)
- [ ] `docs/DEPLOYMENT.md` - Production deployment guide
- [ ] `docs/AUTHENTICATION.md` - Authentication documentation
- [ ] `docs/GETTING_STARTED.md` - Quick start for users
- [ ] Enhanced tool examples in `docs/TOOLS.md`

### Comparison: TypeScript vs Python Implementation

| Aspect | TypeScript | Python | Notes |
|--------|------------|--------|-------|
| **Language** | TypeScript/Node.js | Python | Both are production-ready |
| **Transport** | STDIO + HTTP | STDIO only | HTTP mode needed for production |
| **Authentication** | OAuth 2.1 + X-API-Key | Environment vars | OAuth needed for multi-tenant |
| **Hosted Service** | Yes (mcp-iati.baobabtech.ai) | No | Requires infrastructure |
| **HTTP Server** | Express.js | Could use FastAPI | FastAPI recommended for Python |
| **OAuth Library** | Custom implementation | Use authlib | Python has mature OAuth libraries |
| **API Client** | Facade pattern | Facade pattern | ✅ Both well-designed |
| **Retry Logic** | Not shown | Tenacity library | ✅ Python has better retry support |
| **Type Safety** | TypeScript types | Pydantic models | ✅ Both provide type safety |
| **Error Handling** | Comprehensive | Basic | Room for improvement in Python |
| **Health Checks** | HTTP endpoint | None | Add for production |
| **Documentation** | Extensive | Good | Could be enhanced |

### Files to Create

1. **`src/unhcr_iati_mcp/server_http.py`** - HTTP server implementation
2. **`src/unhcr_iati_mcp/auth/__init__.py`** - Auth package
3. **`src/unhcr_iati_mcp/auth/oauth.py`** - OAuth 2.1 server
4. **`src/unhcr_iati_mcp/auth/middleware.py`** - Authentication middleware
5. **`docs/DEPLOYMENT.md`** - Deployment guide
6. **`docs/AUTHENTICATION.md`** - Authentication documentation
7. **`docs/GETTING_STARTED.md`** - Getting started guide

### Files to Modify

1. **`src/unhcr_iati_mcp/server.py`** - Add transport mode detection
2. **`src/unhcr_iati_mcp/config.py`** - Add new environment variables
3. **`src/unhcr_iati_mcp/client.py`** - Add token-based auth support
4. **`Dockerfile`** - Add HTTP/OAuth dependencies
5. **`docker-compose.yml`** - Add HTTP mode configuration

For detailed analysis and implementation guidance, see [docs/ALTERNATIVE_IMPLEMENTATION_REVIEW.md](docs/ALTERNATIVE_IMPLEMENTATION_REVIEW.md).

---

## Future Enhancements

### Short-term (Next 1-2 Months)

1. **HTTP Transport Mode**
   - Add FastAPI-based HTTP server
   - Support MCP JSON-RPC over HTTP
   - Add health check endpoint

2. **Authentication**
   - Implement OAuth 2.1 client credentials flow
   - Add X-API-Key header support
   - Create token validation middleware

3. **Performance**
   - Add Redis caching for frequent queries
   - Implement request/response logging
   - Add rate limiting

### Medium-term (2-6 Months)

4. **Query Optimization**
   - Add query result caching
   - Implement batch requests
   - Add parallel query support

5. **Data Enhancement**
   - Add more reference data (regions, themes, etc.)
   - Implement data validation on ingestion
   - Add data quality checks

6. **Monitoring**
   - Add Prometheus metrics for HTTP endpoints
   - Implement request tracing
   - Add performance metrics

### Long-term (6+ Months)

7. **Hosted Service**
   - Deploy public hosted service
   - Add user registration and management
   - Implement API key rotation

8. **Advanced Features**
   - Add notification system for data changes
   - Implement webhook support
   - Add scheduled reports

9. **Integration**
   - Add database sync for offline mode
   - Implement change data capture (CDC)
   - Add export to data warehouse support

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

## Support

For issues, questions, or contributions:

- **GitHub Issues**: [Repository URL]/issues
- **IATI Documentation**: https://iatistandard.org/en/guidance/
- **FastMCP Documentation**: https://github.com/modelcontextprotocol/fastmcp

---

## Changelog

### 0.0.1 (Initial Release - July 2024)
- Basic MCP server structure with FastMCP
- IATI Client with retry logic and error handling
- Activity, Transaction, Budget tools
- Donor, Country, Sector analysis tools
- Health check and monitoring tools
- Pydantic models for data validation
- Structured logging with structlog
- Docker support
- Environment variable configuration

---

**Maintained by**: UNHCR Data Team
**Version**: 0.0.1
**Last Updated**: July 2024
