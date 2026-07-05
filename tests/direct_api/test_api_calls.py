"""
Direct API Call Tests for UNHCR IATI MCP Server.

This script tests that all MCP tools can successfully query the UNHCR IATI Datastore
and return valid data. Results are saved to JSON files in the tests/direct_api/ directory.

Usage:
    python -m tests.direct_api.test_api_calls

Or run specific tests:
    python -m tests.direct_api.test_api_calls TestCodeTables
    python -m tests.direct_api.test_api_calls TestAnalyticalTools
    python -m tests.direct_api.test_api_calls TestExistingTools
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


# =============================================================================
# TEST UTILITIES
# =============================================================================

TEST_DIR = Path(__file__).parent
RESULTS_DIR = TEST_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def save_result(filename: str, data: dict) -> Path:
    """Save test result to JSON file with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = RESULTS_DIR / f"{timestamp}_{filename}"
    
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"  ✅ Result saved to: {filepath}")
    return filepath


def format_size(data: dict) -> str:
    """Format the size of data for display."""
    if isinstance(data, list):
        return f"{len(data)} items"
    elif isinstance(data, dict):
        return f"{len(data)} keys"
    else:
        return str(type(data).__name__)


# =============================================================================
# TEST 1: Code Tables (Resources)
# =============================================================================

async def test_code_tables():
    """Test that code table resources can be accessed."""
    print("\n" + "="*70)
    print("TEST 1: Code Table Resources")
    print("="*70)
    
    from unhcr_iati_mcp.resources.code_tables import (
        code_country,
        code_sector,
        code_organisation_role,
        code_activity_status,
        mapping_sdg,
        all_code_tables
    )
    
    results = {}
    
    # Test country codes
    print("\n  Testing code_country resource...")
    try:
        data = await code_country()
        results["code_country"] = {
            "status": "success",
            "count": len(data),
            "sample": data[0] if data else None,
            "timestamp": datetime.now().isoformat()
        }
        save_result("code_country.json", data)
    except Exception as e:
        results["code_country"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  ❌ Error: {e}")
    
    # Test sector codes
    print("  Testing code_sector resource...")
    try:
        data = await code_sector()
        results["code_sector"] = {
            "status": "success",
            "count": len(data),
            "sample": data[0] if data else None,
            "timestamp": datetime.now().isoformat()
        }
        save_result("code_sector.json", data)
    except Exception as e:
        results["code_sector"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  ❌ Error: {e}")
    
    # Test organisation roles
    print("  Testing code_organisation_role resource...")
    try:
        data = await code_organisation_role()
        results["code_organisation_role"] = {
            "status": "success",
            "count": len(data),
            "sample": data[0] if data else None,
            "timestamp": datetime.now().isoformat()
        }
        save_result("code_organisation_role.json", data)
    except Exception as e:
        results["code_organisation_role"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  ❌ Error: {e}")
    
    # Test activity status
    print("  Testing code_activity_status resource...")
    try:
        data = await code_activity_status()
        results["code_activity_status"] = {
            "status": "success",
            "count": len(data),
            "sample": data[0] if data else None,
            "timestamp": datetime.now().isoformat()
        }
        save_result("code_activity_status.json", data)
    except Exception as e:
        results["code_activity_status"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  ❌ Error: {e}")
    
    # Test SDG mapping
    print("  Testing mapping_sdg resource...")
    try:
        data = await mapping_sdg()
        results["mapping_sdg"] = {
            "status": "success",
            "count": len(data),
            "sample": data[0] if data else None,
            "timestamp": datetime.now().isoformat()
        }
        save_result("mapping_sdg.json", data)
    except Exception as e:
        results["mapping_sdg"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  ❌ Error: {e}")
    
    # Test all tables list
    print("  Testing all_code_tables resource...")
    try:
        data = await all_code_tables()
        results["all_code_tables"] = {
            "status": "success",
            "count": len(data),
            "total_entries": sum(t.get("entry_count", 0) for t in data),
            "sample": data[0] if data else None,
            "timestamp": datetime.now().isoformat()
        }
        save_result("all_code_tables.json", data)
    except Exception as e:
        results["all_code_tables"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  ❌ Error: {e}")
    
    # Save summary
    save_result("code_tables_summary.json", results)
    print(f"\n  Summary: {sum(1 for r in results.values() if r['status'] == 'success')}/{len(results)} tests passed")


# =============================================================================
# TEST 2: Code Resolution Tools
# =============================================================================

async def test_code_resolution_tools():
    """Test that code resolution tools work correctly."""
    print("\n" + "="*70)
    print("TEST 2: Code Resolution Tools")
    print("="*70)
    
    from unhcr_iati_mcp.tools.code_resolution import (
        resolve_code,
        validate_code,
        search_code_table,
        list_code_table,
        batch_resolve_codes
    )
    
    results = {}
    
    # Test resolve_code
    print("\n  Testing resolve_code tool...")
    try:
        data = await resolve_code("country", "SY")
        results["resolve_code"] = {
            "status": "success",
            "found": data.get("found"),
            "name": data.get("name"),
            "timestamp": datetime.now().isoformat()
        }
        save_result("resolve_code_SY.json", data)
    except Exception as e:
        results["resolve_code"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  ❌ Error: {e}")
    
    # Test validate_code
    print("  Testing validate_code tool...")
    try:
        data = await validate_code("country", "SY")
        results["validate_code"] = {
            "status": "success",
            "valid": data.get("valid"),
            "timestamp": datetime.now().isoformat()
        }
        save_result("validate_code_SY.json", data)
    except Exception as e:
        results["validate_code"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  ❌ Error: {e}")
    
    # Test search_code_table
    print("  Testing search_code_table tool...")
    try:
        data = await search_code_table("sector", "health", limit=5)
        results["search_code_table"] = {
            "status": "success",
            "count": data.get("count", 0),
            "results_count": len(data.get("results", [])),
            "timestamp": datetime.now().isoformat()
        }
        save_result("search_code_table_health.json", data)
    except Exception as e:
        results["search_code_table"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  ❌ Error: {e}")
    
    # Test list_code_table
    print("  Testing list_code_table tool...")
    try:
        data = await list_code_table("organisation_role", limit=10)
        results["list_code_table"] = {
            "status": "success",
            "total": data.get("total", 0),
            "returned": len(data.get("entries", [])),
            "timestamp": datetime.now().isoformat()
        }
        save_result("list_code_table_org_role.json", data)
    except Exception as e:
        results["list_code_table"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  ❌ Error: {e}")
    
    # Test batch_resolve_codes
    print("  Testing batch_resolve_codes tool...")
    try:
        data = await batch_resolve_codes("country", ["SY", "US", "KEN"])
        results["batch_resolve_codes"] = {
            "status": "success",
            "resolved": data.get("resolved", 0),
            "unresolved": data.get("unresolved", 0),
            "timestamp": datetime.now().isoformat()
        }
        save_result("batch_resolve_codes.json", data)
    except Exception as e:
        results["batch_resolve_codes"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  ❌ Error: {e}")
    
    # Save summary
    save_result("code_resolution_summary.json", results)
    print(f"\n  Summary: {sum(1 for r in results.values() if r['status'] == 'success')}/{len(results)} tests passed")


# =============================================================================
# TEST 3: Existing Tools (Activities, Donors, Sectors, etc.)
# =============================================================================

async def test_existing_tools():
    """Test existing tools that were already in the MCP server."""
    print("\n" + "="*70)
    print("TEST 3: Existing Tools")
    print("="*70)
    
    from unhcr_iati_mcp.tools.activities import (
        unhcr_activities,
        unhcr_activity_by_country,
        unhcr_activity_by_year
    )
    from unhcr_iati_mcp.tools.donors import (
        unhcr_top_donors
    )
    from unhcr_iati_mcp.tools.sectors import (
        unhcr_sector_summary
    )
    from unhcr_iati_mcp.tools.transactions import (
        unhcr_transactions
    )
    from unhcr_iati_mcp.tools.budgets import (
        unhcr_budgets
    )
    
    results = {}
    
    # Test unhcr_activities
    print("\n  Testing unhcr_activities tool...")
    try:
        data = await unhcr_activities(rows=10, start=0)
        results["unhcr_activities"] = {
            "status": "success",
            "response_keys": list(data.keys()) if isinstance(data, dict) else "list",
            "timestamp": datetime.now().isoformat()
        }
        save_result("unhcr_activities.json", data)
    except Exception as e:
        results["unhcr_activities"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  ❌ Error: {e}")
    
    # Test unhcr_top_donors
    print("  Testing unhcr_top_donors tool...")
    try:
        data = await unhcr_top_donors(top_n=5, max_records=1000)
        results["unhcr_top_donors"] = {
            "status": "success",
            "count": len(data),
            "sample": data[0] if data else None,
            "timestamp": datetime.now().isoformat()
        }
        save_result("unhcr_top_donors.json", data)
    except Exception as e:
        results["unhcr_top_donors"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  ❌ Error: {e}")
    
    # Test unhcr_sector_summary
    print("  Testing unhcr_sector_summary tool...")
    try:
        data = await unhcr_sector_summary(max_records=1000)
        results["unhcr_sector_summary"] = {
            "status": "success",
            "count": len(data),
            "sample": list(data.items())[0] if data else None,
            "timestamp": datetime.now().isoformat()
        }
        save_result("unhcr_sector_summary.json", data)
    except Exception as e:
        results["unhcr_sector_summary"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  ❌ Error: {e}")
    
    # Test unhcr_activity_by_country
    print("  Testing unhcr_activity_by_country tool...")
    try:
        data = await unhcr_activity_by_country(country_code="SY", rows=10)
        results["unhcr_activity_by_country"] = {
            "status": "success",
            "response_keys": list(data.keys()) if isinstance(data, dict) else "list",
            "timestamp": datetime.now().isoformat()
        }
        save_result("unhcr_activity_by_country_SY.json", data)
    except Exception as e:
        results["unhcr_activity_by_country"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  ❌ Error: {e}")
    
    # Test unhcr_activity_by_year
    print("  Testing unhcr_activity_by_year tool...")
    try:
        data = await unhcr_activity_by_year(year=2025, max_records=100)
        results["unhcr_activity_by_year"] = {
            "status": "success",
            "count": len(data),
            "timestamp": datetime.now().isoformat()
        }
        save_result("unhcr_activity_by_year_2025.json", data)
    except Exception as e:
        results["unhcr_activity_by_year"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  ❌ Error: {e}")
    
    # Save summary
    save_result("existing_tools_summary.json", results)
    print(f"\n  Summary: {sum(1 for r in results.values() if r['status'] == 'success')}/{len(results)} tests passed")


# =============================================================================
# TEST 4: New Analytical Tools (7 Core Questions)
# =============================================================================

async def test_analytical_tools():
    """Test the 7 core analytical question tools."""
    print("\n" + "="*70)
    print("TEST 4: Analytical Tools (7 Core Questions)")
    print("="*70)
    
    from unhcr_iati_mcp.tools.analytics import (
        unhcr_most_funded_sectors,
        unhcr_top_donors_by_country,
        unhcr_implementing_partners,
        unhcr_earmarking_breakdown,
        unhcr_partnership_analysis,
        unhcr_budget_vs_expenditure,
        unhcr_indicator_trends,
        unhcr_analytical_questions_summary
    )
    
    results = {}
    
    # Test 1: Most funded sectors
    print("\n  Testing unhcr_most_funded_sectors (Q1)...")
    try:
        data = await unhcr_most_funded_sectors(top_n=5, max_records=500)
        results["Q1_most_funded_sectors"] = {
            "status": "success",
            "count": len(data),
            "sample": data[0] if data else None,
            "timestamp": datetime.now().isoformat()
        }
        save_result("Q1_most_funded_sectors.json", data)
    except Exception as e:
        results["Q1_most_funded_sectors"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  ❌ Error: {e}")
    
    # Test 2: Top donors by country
    print("  Testing unhcr_top_donors_by_country (Q2)...")
    try:
        data = await unhcr_top_donors_by_country(top_n=5, max_records=500)
        results["Q2_top_donors_by_country"] = {
            "status": "success",
            "count": len(data),
            "sample": data[0] if data else None,
            "timestamp": datetime.now().isoformat()
        }
        save_result("Q2_top_donors_by_country.json", data)
    except Exception as e:
        results["Q2_top_donors_by_country"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  ❌ Error: {e}")
    
    # Test 3: Implementing partners
    print("  Testing unhcr_implementing_partners (Q3)...")
    try:
        data = await unhcr_implementing_partners(top_n=5, max_records=500)
        results["Q3_implementing_partners"] = {
            "status": "success",
            "count": len(data),
            "sample": data[0] if data else None,
            "timestamp": datetime.now().isoformat()
        }
        save_result("Q3_implementing_partners.json", data)
    except Exception as e:
        results["Q3_implementing_partners"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  ❌ Error: {e}")
    
    # Test 4: Earmarking breakdown
    print("  Testing unhcr_earmarking_breakdown (Q4)...")
    try:
        data = await unhcr_earmarking_breakdown(max_records=500)
        results["Q4_earmarking_breakdown"] = {
            "status": "success",
            "total_transactions": data.get("total_transactions", 0),
            "total_value": data.get("total_value", 0),
            "breakdown_count": len(data.get("breakdown", [])),
            "timestamp": datetime.now().isoformat()
        }
        save_result("Q4_earmarking_breakdown.json", data)
    except Exception as e:
        results["Q4_earmarking_breakdown"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  ❌ Error: {e}")
    
    # Test 5: Partnership analysis
    print("  Testing unhcr_partnership_analysis (Q5)...")
    try:
        data = await unhcr_partnership_analysis(max_records=500)
        results["Q5_partnership_analysis"] = {
            "status": "success",
            "total_activities": data.get("total_activities", 0),
            "total_partners": data.get("total_partners", 0),
            "roles_count": len(data.get("partnership_roles", {})),
            "timestamp": datetime.now().isoformat()
        }
        save_result("Q5_partnership_analysis.json", data)
    except Exception as e:
        results["Q5_partnership_analysis"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  ❌ Error: {e}")
    
    # Test 6: Budget vs expenditure
    print("  Testing unhcr_budget_vs_expenditure (Q6)...")
    try:
        data = await unhcr_budget_vs_expenditure(max_records=500)
        results["Q6_budget_vs_expenditure"] = {
            "status": "success",
            "count": len(data),
            "sample": data[0] if data else None,
            "timestamp": datetime.now().isoformat()
        }
        save_result("Q6_budget_vs_expenditure.json", data)
    except Exception as e:
        results["Q6_budget_vs_expenditure"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  ❌ Error: {e}")
    
    # Test 7: Indicator trends
    print("  Testing unhcr_indicator_trends (Q7)...")
    try:
        data = await unhcr_indicator_trends(start_year=2020, end_year=2025, max_records=500)
        results["Q7_indicator_trends"] = {
            "status": "success",
            "count": len(data),
            "sample": data[0] if data else None,
            "timestamp": datetime.now().isoformat()
        }
        save_result("Q7_indicator_trends.json", data)
    except Exception as e:
        results["Q7_indicator_trends"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  ❌ Error: {e}")
    
    # Test summary tool
    print("  Testing unhcr_analytical_questions_summary (All 7)...")
    try:
        data = await unhcr_analytical_questions_summary()
        results["summary_all_7"] = {
            "status": "success",
            "questions_answered": data.get("metadata", {}).get("questions_answered", 0),
            "results_keys": list(data.get("results", {}).keys()),
            "timestamp": datetime.now().isoformat()
        }
        save_result("summary_all_7_questions.json", data)
    except Exception as e:
        results["summary_all_7"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(f"  ❌ Error: {e}")
    
    # Save summary
    save_result("analytical_tools_summary.json", results)
    print(f"\n  Summary: {sum(1 for r in results.values() if r['status'] == 'success')}/{len(results)} tests passed")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

async def run_all_tests():
    """Run all test suites."""
    print("\n" + "="*70)
    print("UNHCR IATI MCP - DIRECT API TESTS")
    print("="*70)
    print(f"Results will be saved to: {RESULTS_DIR.absolute()}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    await test_code_tables()
    await test_code_resolution_tools()
    await test_existing_tools()
    await test_analytical_tools()
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETED")
    print("="*70)
    print(f"\nResults directory: {RESULTS_DIR.absolute()}")
    print(f"Files saved: {len(list(RESULTS_DIR.glob('*.json')))} JSON files")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
