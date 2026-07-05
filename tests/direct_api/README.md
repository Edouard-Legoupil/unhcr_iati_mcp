# Direct API Tests

This directory contains tests that directly call the MCP tools to verify they work with real UNHCR IATI Datastore data.

## Structure

```
tests/direct_api/
├── __init__.py           # Package initialization
├── README.md             # This file
├── test_api_calls.py     # Main test script
└── results/              # Directory for test results (created on first run)
    ├── 20260705_123456_code_country.json
    ├── 20260705_123456_code_sector.json
    ├── 20260705_123456_Q1_most_funded_sectors.json
    ├── 20260705_123456_analytical_tools_summary.json
    └── ...
```

## Running Tests

### Run All Tests

```bash
cd /home/edouard/python/unhcr_iati_mcp
python -m tests.direct_api.test_api_calls
```

### Expected Output

```
UNHCR IATI MCP - DIRECT API TESTS
======================================================================
Results will be saved to: /home/edouard/python/unhcr_iati_mcp/tests/direct_api/results
Timestamp: 2026-07-05T12:34:56.789012

TEST 1: Code Table Resources
======================================================================
  Testing code_country resource...
  ✅ Result saved to: /home/edouard/python/unhcr_iati_mcp/tests/direct_api/results/20260705_123456_code_country.json
  Testing code_sector resource...
  ✅ Result saved to: /home/edouard/python/unhcr_iati_mcp/tests/direct_api/results/20260705_123457_code_sector.json
  ...

TEST 2: Code Resolution Tools
======================================================================
  Testing resolve_code tool...
  ✅ Result saved to: /home/edouard/python/unhcr_iati_mcp/tests/direct_api/results/20260705_123458_resolve_code_SY.json
  ...

ALL TESTS COMPLETED
======================================================================

Results directory: /home/edouard/python/unhcr_iati_mcp/tests/direct_api/results
Files saved: 25 JSON files
```

## Test Suites

### Test Suite 1: Code Table Resources
Tests the 41 IATI code table resources:
- `code_country` - Country codes
- `code_sector` - Sector codes
- `code_organisation_role` - Organisation roles
- `code_activity_status` - Activity statuses
- `mapping_sdg` - SDG mappings
- `all_code_tables` - List of all tables

**Output Files:**
- `code_country.json`
- `code_sector.json`
- `code_organisation_role.json`
- `code_activity_status.json`
- `mapping_sdg.json`
- `all_code_tables.json`
- `code_tables_summary.json`

### Test Suite 2: Code Resolution Tools
Tests the 5 code resolution tools:
- `resolve_code` - Resolve a code to name
- `validate_code` - Validate if code exists
- `search_code_table` - Search code table
- `list_code_table` - List all entries
- `batch_resolve_codes` - Batch resolve multiple codes

**Output Files:**
- `resolve_code_SY.json`
- `validate_code_SY.json`
- `search_code_table_health.json`
- `list_code_table_org_role.json`
- `batch_resolve_codes.json`
- `code_resolution_summary.json`

### Test Suite 3: Existing Tools
Tests the existing MCP tools:
- `unhcr_activities` - List activities
- `unhcr_top_donors` - Top donors
- `unhcr_sector_summary` - Sector summary
- `unhcr_activity_by_country` - Activities by country
- `unhcr_activity_by_year` - Activities by year

**Output Files:**
- `unhcr_activities.json`
- `unhcr_top_donors.json`
- `unhcr_sector_summary.json`
- `unhcr_activity_by_country_SY.json`
- `unhcr_activity_by_year_2025.json`
- `existing_tools_summary.json`

### Test Suite 4: Analytical Tools (7 Core Questions)
Tests the 7 core analytical question tools + summary:
- `Q1_most_funded_sectors` - Question 1
- `Q2_top_donors_by_country` - Question 2
- `Q3_implementing_partners` - Question 3
- `Q4_earmarking_breakdown` - Question 4
- `Q5_partnership_analysis` - Question 5
- `Q6_budget_vs_expenditure` - Question 6
- `Q7_indicator_trends` - Question 7
- `summary_all_7_questions` - All questions combined

**Output Files:**
- `Q1_most_funded_sectors.json`
- `Q2_top_donors_by_country.json`
- `Q3_implementing_partners.json`
- `Q4_earmarking_breakdown.json`
- `Q5_partnership_analysis.json`
- `Q6_budget_vs_expenditure.json`
- `Q7_indicator_trends.json`
- `summary_all_7_questions.json`
- `analytical_tools_summary.json`

## Test Results

All test results are saved as JSON files in the `results/` directory with:
- Timestamp prefix (YYYYMMDD_HHMMSS)
- Descriptive filename indicating which tool was tested
- Full API response data
- Metadata including status, count, and timestamp

### Understanding Results

Each JSON file contains:
- **For resources**: List of code entries (e.g., countries, sectors)
- **For tools**: Dictionary with results and metadata
- **For summaries**: Aggregated test results with success/error counts

Example result file (`20260705_123456_code_country.json`):
```json
[
  {"code": "AF", "name": "Afghanistan", "description": null, "category": null, "url": null, "status": "active"},
  {"code": "AX", "name": "Åland Islands", "description": null, "category": null, "url": null, "status": "active"},
  ...
]
```

## Notes

- Tests use `max_records` limits to avoid excessive data retrieval
- Tests fetch data from the live IATI Datastore (internet connection required)
- Results may vary slightly between runs due to data updates
- Error responses are also saved for debugging
- All tests run asynchronously for better performance

## Cleanup

To remove all test result files:

```bash
rm -rf /home/edouard/python/unhcr_iati_mcp/tests/direct_api/results/*
```

## Next Steps

After running tests:
1. Check the `results/` directory for JSON output files
2. Review success/error counts in summary files
3. Inspect individual result files for data validation
4. Use results to verify data structure and content
