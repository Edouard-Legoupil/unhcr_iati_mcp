the resources/ folder should contain read-only, agent-friendly data sources that LLMs can access without calling operational tools.
Think of:

Tools = perform actions, queries, calculations.
Resources = provide context, reference data, metadata, schemas, documentation, dimensions.

## Available MCP Resources

### Sector Resources (sectors.py)
- `unhcr://sectors` - UNHCR-specific sector code to name mapping (Vocabulary 98)
- `unhcr://sector_vocabularies` - Metadata about all IATI sector vocabularies with warnings
- `unhcr://sector_analysis_guidelines` - Comprehensive guidelines for correct sector data analysis
- `unhcr://sector_vocabulary_warnings` - Quick-reference warnings for each vocabulary

### Result Framework Resources (results.py)
- `unhcr://result_types` - Metadata about IATI result type codes (Output, Outcome, Impact, Other)
- `unhcr://indicator_measures` - Metadata about IATI indicator measure codes (Unit, Percentage, Nominal, Ordinal, Qualitative)
- `unhcr://result_areas` - UNHCR's 16 Operational Areas (OA) at the outcome level
- `unhcr://result_analysis_guidelines` - Comprehensive guidelines for correct result data analysis
- `unhcr://disaggregation_dimensions` - Metadata about common disaggregation dimensions (sex, age, disability, etc.)

### Code Tables
**NOTE: Code tables are NOT registered as MCP resources to reduce context window usage.**

Access code tables via the **code_resolution.py tools**:
- `resolve_code(code_type, code)` - Resolve codes to human-readable values
- `validate_code(code_type, code)` - Validate code existence
- `list_code_table(code_type)` - List all entries in a code table
- `search_code_table(code_type, query)` - Search code tables
- `batch_resolve_codes(code_type, codes)` - Batch resolve multiple codes

All 41 IATI code lookup tables are available and loaded on-demand (lazy loading).
Includes: sector, sector_category, sector_vocabulary, country, region, aid_type, etc.

### Other Resources
- `unhcr://countries` - Country metadata
- `unhcr://donors` - Donor information
- `unhcr://glossary` - Glossary of terms
- `unhcr://portfolio` - Portfolio data
- `unhcr://schemas` - Data schemas
- `unhcr://sdgs` - Sustainable Development Goals mapping
- `unhcr://prompts` - Agent prompts

## Critical Notes on Sector Data

**IMPORTANT**: Sector codes have different meanings across vocabularies.

The same code (e.g., "10") in vocabulary 10 (IASC) means something different from
code "10" in vocabulary 98 (UNHCR-specific). NEVER sum percentages or aggregate
across vocabularies without filtering by vocabulary first.

Key vocabularies:
- **98**: UNHCR-specific sectors (PRIMARY for UNHCR analysis)
- **10**: IASC Humanitarian Clusters (used alongside 98)
- **1**: OECD DAC CRS Purpose Codes (5-digit)
- **2**: OECD DAC CRS Purpose Codes (3-digit)
- **99**: Reporting Organisation (organisation-specific)

Always use the sector_vocabulary field to filter data before aggregation.