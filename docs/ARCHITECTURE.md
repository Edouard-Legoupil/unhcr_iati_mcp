# UNHCR IATI MCP Server - Architecture

This document describes the architecture of the UNHCR IATI MCP Server.

## Overview

The UNHCR IATI MCP Server provides AI agents and applications with structured access to UNHCR's IATI (International Aid Transparency Initiative) data from the official IATI Datastore API.

## Architecture Diagram

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

## Component Layers

### 1. MCP Interface Layer

The top layer exposes functionality through the Model Context Protocol:

- **Tools**: Executable actions that query and transform data
- **Resources**: Read-only reference data accessible via URIs

All tools are prefixed with `unhcr_` and automatically filter results to UNHCR's data (publisher_ref: `XM-DAC-41121`).

### 2. Client Layer

The `IATIClient` class in `client.py` provides the core API interaction layer with:

- **Connection Management**: HTTPX async client with connection pooling
- **Retry Logic**: Automatic exponential backoff for transient failures
- **Pagination Support**: Automatic handling of large result sets
- **Error Handling**: Custom exception hierarchy for different error types

### 3. Data Layer

The IATI Datastore API provides access to:

- **Activity Collection**: Projects and programs with full result framework
- **Transaction Collection**: Financial movements and disbursements
- **Budget Collection**: Planned funding allocations
- **Organisation Collection**: Publishing organizations

### 4. Resource Layer

Static reference data includes:

- **Code Tables**: All 41 IATI code lookup tables
- **Sector Data**: UNHCR-specific sector mappings and vocabulary management
- **Result Framework**: Complete IATI result framework with indicators
- **Geographic Data**: Country and region reference data
- **Financial Data**: Donor information and currency codes

## Key Design Decisions

### Sector Vocabulary Management

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

### Result Framework Support

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

### Code Tables

All **41 IATI code lookup tables** are embedded in the package:
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

## Data Flow

1. **Request**: MCP client calls a tool (e.g., `unhcr_activities`)
2. **Validation**: Tool validates parameters and context
3. **Query Construction**: Tool constructs Solr query with UNHCR filter
4. **API Call**: IATIClient sends request to IATI Datastore
5. **Retry Handling**: Automatic retry on failures
6. **Data Transformation**: Results parsed into Pydantic models
7. **Vocabulary Check**: Sector vocabulary warnings generated
8. **Response**: Structured data returned to client

## Performance Considerations

- **Connection Pooling**: Max 50 concurrent connections
- **Timeout**: Configurable (default 120 seconds)
- **Pagination**: Automatic handling with configurable page size
- **Caching**: Code tables cached in memory after first load
- **Lazy Loading**: Non-essential code tables loaded on-demand
