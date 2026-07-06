"""
IATI Code Lookup Tables for UNHCR IATI MCP Server.

This directory contains all 41 IATI code lookup tables in RData format.
These tables are critical for data interpretation, validation, and human-readable output.

Tables are loaded on-demand by code_tables.py and cached in memory for performance.

Categories:
- activity: date type, scope, status
- organisation: identifier, registration agency, role, type
- geographic: country, region, location class
- financial: aid type, budget, flow type, earmarking, currency
- sector: sector, category, vocabulary
- policy: policy marker, humanitarian scope, clusters
- result: indicator, result types, indicator vocabulary
- other: description type, collaboration type, etc.

File naming convention: code<Name>.RData (e.g., codeCountry.RData, codeSector.RData)

To add a new code table:
1. Add the .RData file to this directory
2. Add the table name to ESSENTIAL_TABLES in code_tables.py if it should be pre-loaded
3. Optionally add a corresponding @mcp.resource function

Note: The .RData files were originally sourced from the iati package:
https://github.com/IATI/IATI-R-data-package
"""
