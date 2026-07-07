# UNHCR IATI MCP Server

A Model Context Protocol (MCP) server for accessing [UNHCR's IATI (International Aid Transparency Initiative) data](https://www.unhcr.org/iati-international-aid-transparency-initiative) from the official IATI Datastore API.

This project builds upon previous [data exploration done in R](https://github.com/Edouard-Legoupil/iati).

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

**CRITICAL**: Sector codes have different meanings across IATI vocabularies. The server provides comprehensive vocabulary management to prevent cross-vocabulary aggregation errors.

**Supported Vocabularies:**
- **98**: UNHCR-specific sectors (PRIMARY for UNHCR analysis)
- **10**: IASC Humanitarian Clusters
- **1**: OECD DAC CRS Purpose Codes (5-digit)
- **2**: OECD DAC CRS Purpose Codes (3-digit)
- **99**: Reporting Organisation (organisation-specific)

### ✅ Result Framework Support

Complete support for IATI's hierarchical result framework with **16 UNHCR Operational Areas** at the outcome level.

### ✅ Comprehensive Code Tables

All **41 IATI code lookup tables** are embedded in the package with on-demand loading and caching for optimal performance. Access via code resolution tools (`resolve_code`, `list_code_table`, etc.) rather than direct MCP resources.

## Quick Start

### Prerequisites

- **Python**: 3.11+ (recommended: 3.12)
- **Package Manager**: Poetry or pip
- **Container Runtime**: Docker (optional)
- **API Key**: IATI Datastore subscription key (required)

### Installation

#### Using pip

```bash
# Clone the repository
git clone <repository-url>
cd unhcr_iati_mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your IATI API key
```

#### Using Docker

```bash
# Build and run
docker-compose build
docker-compose up -d
```

### Running the Server

```bash
# Development mode
python -m unhcr_iati_mcp.server

# With debug logging
LOG_LEVEL=DEBUG python -m unhcr_iati_mcp.server
```

## Basic Usage

### MCP Client Integration

The server exposes tools and resources via the Model Context Protocol (MCP).

**Available Tools (prefix: `unhcr_`):**
- Activity tools: `unhcr_activities`, `unhcr_activity`, `unhcr_activity_by_country`, etc.
- Transaction tools: `unhcr_transactions`, `unhcr_transaction_search`
- Budget tools: `unhcr_budgets`
- Analysis tools: `unhcr_top_donors`, `unhcr_sector_summary`, etc.
- Export tools: `unhcr_export_json`, `unhcr_export_csv`, `unhcr_bulk_extract`
- Health tools: `health_check`, `system_status`, `datastore_ping`

**Available Resources:**
- `unhcr://sectors`, `unhcr://countries`, `unhcr://donors`
- `unhcr://sector_vocabularies`, `unhcr://sector_analysis_guidelines`
- `unhcr://result_types`, `unhcr://indicator_measures`, `unhcr://result_areas`
- `unhcr://glossary`, `unhcr://portfolio`, `unhcr://schemas`, `unhcr://sdgs`

### Example Usage

#### Python (with MCP client library)

```python
import asyncio
from mcp import Client

async def main():
    client = Client("http://localhost:8000")
    
    # Get activities
    result = await client.call_tool("unhcr_activities", {"rows": 50})
    print(f"Found {len(result['response']['docs'])} activities")
    
    # Get top donors
    donors = await client.call_tool("unhcr_top_donors", {"top_n": 10})
    print(f"Top donors: {donors}")

asyncio.run(main())
```

#### Natural Language (with AI Assistant)

Simply ask in plain English:
- "Show me UNHCR projects in Afghanistan"
- "What are the top donors to UNHCR?"
- "Get UNHCR health projects in Kenya"
- "Show me sector distribution for UNHCR activities"

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Required
IATI_API_KEY="your-iati-subscription-key"
IATI_BASE_URL="https://api.iatistandard.org/datastore"
UNHCR_PUBLISHER_REF="XM-DAC-41121"

# Optional (with defaults)
TIMEOUT_SECONDS=120
PAGE_SIZE=1000
LOG_LEVEL="INFO"
```

**Note**: UNHCR's publisher reference in IATI is `XM-DAC-41121`.

## Project Structure

```
unhcr_iati_mcp/
├── src/
│   └── unhcr_iati_mcp/
│       ├── server.py           # FastMCP server entry point
│       ├── client.py           # IATI API client
│       ├── config.py           # Configuration
│       ├── models/             # Pydantic data models
│       ├── tools/              # MCP tools
│       ├── resources/          # MCP resources
│       └── observability/      # Logging & metrics
├── docs/
│   ├── ARCHITECTURE.md         # Architecture documentation
│   ├── API_REFERENCE.md        # API reference
│   ├── DATA_MODELS.md          # Data models
│   ├── DEPLOYMENT.md           # Deployment guide
│   ├── TROUBLESHOOTING.md       # Troubleshooting
│   ├── BEST_PRACTICES.md       # Best practices
│   ├── DEVELOPMENT.md          # Development guidelines
│   └── TOOLS.md                # Tools documentation
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Documentation

Comprehensive documentation is available in the `docs/` folder:

- **[Architecture](docs/ARCHITECTURE.md)**: System architecture and design decisions
- **[API Reference](docs/API_REFERENCE.md)**: Complete API documentation
- **[Data Models](docs/DATA_MODELS.md)**: Pydantic models and data structures
- **[Deployment](docs/DEPLOYMENT.md)**: Installation and deployment guide
- **[Troubleshooting](docs/TROUBLESHOOTING.md)**: Common issues and solutions
- **[Best Practices](docs/BEST_PRACTICES.md)**: Guidelines and common pitfalls
- **[Development](docs/DEVELOPMENT.md)**: Contribution guidelines
- **[Tools](docs/TOOLS.md)**: Detailed tool documentation with examples

## Key Concepts

### Sector Vocabulary Safety

⚠️ **IMPORTANT**: Sector codes have different meanings across vocabularies. Always:
1. Check the `sector_vocabulary` field
2. Use vocabulary 98 for UNHCR-specific analysis
3. Never aggregate across vocabularies without grouping first

The server provides built-in validation and warnings to prevent common errors.

### Result Framework

The server supports the complete IATI result framework:
- **Output (1)**: Short-term deliverables
- **Outcome (2)**: Medium-term results (16 UNHCR Operational Areas)
- **Impact (3)**: Long-term outcomes
- **Other (9)**: Other result types

### Code Tables

All 41 IATI code lookup tables are available through **code resolution tools** (not as direct MCP resources):
- Activity codes, Organisation codes, Geographic codes
- Financial codes, Sector codes, Policy codes
- Result codes, SDG codes

Use the following tools to access code tables:
- `resolve_code(code_type, code)` - Resolve a code to human-readable name
- `validate_code(code_type, code)` - Check if a code exists
- `list_code_table(code_type)` - List all entries in a code table
- `search_code_table(code_type, query)` - Search code table by name/description
- `batch_resolve_codes(code_type, codes)` - Resolve multiple codes at once

Note: Code tables are loaded on-demand (lazy loading) and cached for performance.

## Performance & Optimization

### Context Window Management

The MCP server has been optimized to minimize context window usage:

- **~55K tokens** total for all tool and resource definitions (down from ~91K)
- **33 tools** with concise docstrings
- **17 resources** (reduced from 63 by removing redundant code table resources)
- **Lazy loading** of code tables (loaded on-demand, not at startup)

This ensures compatibility with models having 32K-128K token context windows.

For models with smaller context windows:
- Use specific tools rather than listing all tools
- Access code tables via `resolve_code`, `list_code_table` tools rather than direct resources
- Request smaller result sets with `max_records` parameters

## Resources

- **IATI Documentation**: https://iatistandard.org/en/guidance/
- **FastMCP Documentation**: https://github.com/modelcontextprotocol/fastmcp
- **IATI Datastore API**: https://developer.iatistandard.org/
- **Model Context Protocol**: https://modelcontextprotocol.io/

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.
