"""
Analytics tools for UNHCR IATI data.

This module implements the 7 core analytical questions from the R-analysis framework,
providing standardized, production-ready analytics for UNHCR operations.

The 7 Core Questions:
1. Most funded sectors per country
2. Main donors by country
3. Main implementing partners by country
4. Earmarking type breakdown
5. Partnership level analysis
6. Expenditure vs budget comparison
7. Indicator evolution over time
"""

from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple

from unhcr_iati_mcp.context import (
    mcp,
    iati_client,
    unhcr_filter,
    parse_unhcr_identifier,
    PROGRAMME_LABELS,
    DEFAULT_MAX_RECORDS,
)
from unhcr_iati_mcp.client import IATIError
from unhcr_iati_mcp.observability.logging import get_logger

logger = get_logger(__name__)


def _safe_get_list(data: Dict, key: str) -> List:
    """Safely get a list value from a dictionary, handling None and missing keys."""
    value = data.get(key, [])
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _safe_get_float(data: Dict, key: str) -> float:
    """Safely get a float value from a dictionary, handling None, missing keys, and lists."""
    value = data.get(key, 0)
    if value is None:
        return 0.0
    # Handle case where value is a list (e.g., [9992.0] from IATI Datastore)
    if isinstance(value, list) and len(value) > 0:
        value = value[0]
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def _safe_get_str(data: Dict, key: str) -> str:
    """Safely get a string value from a dictionary, handling None, missing keys, and lists."""
    value = data.get(key, "")
    if value is None:
        return ""
    # Handle case where value is a list (e.g., ["SY"] from IATI Datastore)
    if isinstance(value, list) and len(value) > 0:
        value = value[0]
    return str(value)


# =============================================================================
# UNHCR IATI IDENTIFIER PARSING
# =============================================================================
#
# The iati_identifier for UNHCR follows this pattern:
# XM-DAC-41121-{YEAR}-{REGION/OPS}[-{COUNTRY}]
#
# Examples:
#   XM-DAC-41121-2024-HQ              -> HQ operation, year 2024
#   XM-DAC-41121-2024-MENA            -> MENA regional, year 2024
#   XM-DAC-41121-2024-MENA-SYR        -> Syria country operation under MENA, year 2024
#   XM-DAC-41121-2024-GLOBALPROG      -> Global Program, year 2024

# Note: parse_unhcr_identifier and PROGRAMME_LABELS are imported from context module


# =============================================================================
# QUESTION 1: Most Funded Sectors per Country
# =============================================================================

@mcp.tool(
    name="unhcr_most_funded_sectors",
    description="Get most funded sectors per country with funding amounts"
)
async def unhcr_most_funded_sectors(
    country_code: Optional[str] = None,
    top_n: int = 10,
    year: Optional[int] = None,
    max_records: int = DEFAULT_MAX_RECORDS
) -> List[Dict[str, Any]]:
    """Get most funded sectors per country with funding amounts."""
    try:
        # Build query
        q = unhcr_filter()
        if country_code:
            q += f' AND recipient_country_code:"{country_code}"'
        if year:
            q += f' AND transaction_value_value_date:[{year}-01-01T00:00:00Z TO {year}-12-31T23:59:59Z]'
        
        # Fetch transactions
        transactions = await iati_client.fetch_all(
            collection="transaction",
            q=q,
            max_records=max_records
        )
        
        # Aggregate by sector
        sector_funding = Counter()
        sector_transaction_count = Counter()
        
        for tx in transactions:
            sectors = _safe_get_list(tx, "sector_code")
            value = _safe_get_float(tx, "transaction_value")
            
            if value == 0:
                continue
                
            for sector in sectors:
                if sector:
                    sector_funding[sector] += value
                    sector_transaction_count[sector] += 1
        
        if not sector_funding:
            return []
        
        # Calculate percentages
        total_funding = sum(sector_funding.values())
        
        # Sort and limit
        results = []
        for sector, amount in sector_funding.most_common(top_n):
            results.append({
                "sector_code": sector,
                "sector_name": f"Sector {sector}",  # Would be resolved via code tables
                "total_value": amount,
                "transaction_count": sector_transaction_count[sector],
                "percentage": round((amount / total_funding) * 100, 2) if total_funding > 0 else 0
            })
        
        return results
        
    except IATIError as e:
        logger.error(f"Error in unhcr_most_funded_sectors: {e}")
        return []
    except Exception as e:
        logger.exception("Unexpected error in unhcr_most_funded_sectors")
        return []


# =============================================================================
# QUESTION 2: Main Donors by Country
# =============================================================================

@mcp.tool(
    name="unhcr_top_donors_by_country",
    description="Get main donors by country with contribution amounts"
)
async def unhcr_top_donors_by_country(
    country_code: Optional[str] = None,
    top_n: int = 10,
    year: Optional[int] = None,
    max_records: int = DEFAULT_MAX_RECORDS
) -> List[Dict[str, Any]]:
    """Get main donors by country with contribution amounts."""
    try:
        # Build query
        q = unhcr_filter()
        if country_code:
            q += f' AND recipient_country_code:"{country_code}"'
        if year:
            q += f' AND transaction_value_value_date:[{year}-01-01T00:00:00Z TO {year}-12-31T23:59:59Z]'
        
        # Fetch transactions
        transactions = await iati_client.fetch_all(
            collection="transaction",
            q=q,
            max_records=max_records
        )
        
        # Aggregate by donor
        donor_funding = Counter()
        donor_transaction_count = Counter()
        donor_names = {}
        
        for tx in transactions:
            # In IATI Datastore, these are separate fields, not nested
            # transaction_provider_org_ref is often None, so use narrative as key
            donor_ref = _safe_get_str(tx, "transaction_provider_org_ref")
            donor_narrative = _safe_get_str(tx, "transaction_provider_org_narrative")
            value = _safe_get_float(tx, "transaction_value")
            
            # Use narrative as the donor identifier when ref is not available
            donor_key = donor_ref if donor_ref else donor_narrative
            
            if donor_key and value > 0:
                donor_funding[donor_key] += value
                donor_transaction_count[donor_key] += 1
                if donor_key not in donor_names:
                    donor_names[donor_key] = donor_narrative if donor_narrative else f"Donor {donor_key}"
        
        if not donor_funding:
            return []
        
        # Calculate percentages
        total_funding = sum(donor_funding.values())
        
        # Sort and limit
        results = []
        for donor_ref, amount in donor_funding.most_common(top_n):
            results.append({
                "donor_ref": donor_ref,
                "donor_name": donor_names.get(donor_ref, f"Donor {donor_ref}"),
                "total_value": amount,
                "transaction_count": donor_transaction_count[donor_ref],
                "percentage": round((amount / total_funding) * 100, 2) if total_funding > 0 else 0
            })
        
        return results
        
    except IATIError as e:
        logger.error(f"Error in unhcr_top_donors_by_country: {e}")
        return []
    except Exception as e:
        logger.exception("Unexpected error in unhcr_top_donors_by_country")
        return []


# =============================================================================
# QUESTION 3: Main Implementing Partners by Country
# =============================================================================

@mcp.tool(
    name="unhcr_implementing_partners",
    description="Get main implementing partners by country"
)
async def unhcr_implementing_partners(
    country_code: Optional[str] = None,
    top_n: int = 10,
    max_records: int = DEFAULT_MAX_RECORDS
) -> List[Dict[str, Any]]:
    """Get main implementing partners by country."""
    try:
        # Build query
        q = unhcr_filter()
        if country_code:
            q += f' AND recipient_country_code:"{country_code}"'
        
        # Fetch activities
        activities = await iati_client.fetch_all(
            collection="activity",
            q=q,
            max_records=max_records
        )
        
        # Track implementing partners
        partner_activity_count = Counter()
        partner_info = {}
        
        for activity in activities:
            # In IATI Datastore, participating_org is stored as separate list fields
            org_refs = _safe_get_list(activity, "participating_org_ref")
            org_narratives = _safe_get_list(activity, "participating_org_narrative")
            org_roles = _safe_get_list(activity, "participating_org_role")
            
            # Process each participating organization
            for i, org_ref in enumerate(org_refs):
                org_name = org_narratives[i] if i < len(org_narratives) else ""
                role = org_roles[i] if i < len(org_roles) else ""
                
                # We want Implementing partners (role code 4)
                if role == "4" or role.lower() == "implementing":
                    # Use ref if available, otherwise use narrative
                    partner_key = org_ref if org_ref else org_name
                    if partner_key:
                        partner_activity_count[partner_key] += 1
                        if partner_key not in partner_info:
                            partner_info[partner_key] = {
                                "name": org_name if org_name else f"Partner {partner_key}",
                                "role": role
                            }
        
        if not partner_activity_count:
            return []
        
        # Sort and limit
        results = []
        for org_ref, count in partner_activity_count.most_common(top_n):
            info = partner_info[org_ref]
            results.append({
                "org_ref": org_ref,
                "org_name": info["name"],
                "activity_count": count,
                "role": info["role"]
            })
        
        return results
        
    except IATIError as e:
        logger.error(f"Error in unhcr_implementing_partners: {e}")
        return []
    except Exception as e:
        logger.exception("Unexpected error in unhcr_implementing_partners")
        return []


# =============================================================================
# QUESTION 4: Earmarking Type Breakdown
# =============================================================================

@mcp.tool(
    name="unhcr_earmarking_breakdown",
    description="Get earmarking type breakdown for transactions"
)
async def unhcr_earmarking_breakdown(
    year: Optional[int] = None,
    country_code: Optional[str] = None,
    max_records: int = DEFAULT_MAX_RECORDS
) -> Dict[str, Any]:
    """Get earmarking type breakdown for transactions."""
    try:
        # Earmarking category mapping
        EARMARKING_CATEGORIES = {
            "0": "Un-earmarked",
            "1": "Tightly earmarked",
            "2": "Loosely earmarked",
            "3": "Core/Un-earmarked contributions"
        }
        
        # Build query
        q = unhcr_filter()
        if country_code:
            q += f' AND recipient_country_code:"{country_code}"'
        if year:
            q += f' AND transaction_value_value_date:[{year}-01-01T00:00:00Z TO {year}-12-31T23:59:59Z]'
        
        # Fetch transactions
        transactions = await iati_client.fetch_all(
            collection="transaction",
            q=q,
            max_records=max_records
        )
        
        # Aggregate by earmarking category
        category_totals = Counter()
        category_counts = Counter()
        total_value = 0.0
        
        for tx in transactions:
            earmarking = _safe_get_str(tx, "transaction_aid_type_earmarking_category_code")
            value = _safe_get_float(tx, "transaction_value")
            
            if value > 0:
                total_value += value
                if earmarking:
                    category_totals[earmarking] += value
                    category_counts[earmarking] += 1
                else:
                    category_totals["unknown"] += value
                    category_counts["unknown"] += 1
        
        # Build results
        breakdown = []
        for category, amount in category_totals.most_common():
            breakdown.append({
                "category_code": category,
                "category_name": EARMARKING_CATEGORIES.get(category, f"Category {category}"),
                "total_value": amount,
                "transaction_count": category_counts[category],
                "percentage": round((amount / total_value) * 100, 2) if total_value > 0 else 0
            })
        
        return {
            "total_transactions": len(transactions),
            "total_value": total_value,
            "breakdown": breakdown,
            "categories": EARMARKING_CATEGORIES
        }
        
    except IATIError as e:
        logger.error(f"Error in unhcr_earmarking_breakdown: {e}")
        return {"error": str(e), "breakdown": []}
    except Exception as e:
        logger.exception("Unexpected error in unhcr_earmarking_breakdown")
        return {"error": str(e), "breakdown": []}


# =============================================================================
# QUESTION 5: Partnership Level Analysis
# =============================================================================

@mcp.tool(
    name="unhcr_partnership_analysis",
    description="Analyze partnership levels across activities"
)
async def unhcr_partnership_analysis(
    country_code: Optional[str] = None,
    max_records: int = DEFAULT_MAX_RECORDS
) -> Dict[str, Any]:
    """Analyze partnership levels across activities."""
    try:
        # Partnership role mapping
        PARTNERSHIP_ROLES = {
            "1": {"name": "Funding", "description": "The government or organisation which provides funds to the activity"},
            "2": {"name": "Accountable", "description": "Organisation responsible for oversight of the activity and its outcomes"},
            "3": {"name": "Implementing", "description": "The organisation that physically carries out the activity or intervention"},
            "4": {"name": "Extending", "description": "An organisation that manages the budget and direction of an activity on behalf of the funding organisation"}
        }
        
        # Build query
        q = unhcr_filter()
        if country_code:
            q += f' AND recipient_country_code:"{country_code}"'
        
        # Fetch activities
        activities = await iati_client.fetch_all(
            collection="activity",
            q=q,
            max_records=max_records
        )
        
        # Analyze partnerships
        role_counts = Counter()
        total_partners = 0
        
        for activity in activities:
            # In IATI Datastore, participating_org is stored as separate list fields
            org_roles = _safe_get_list(activity, "participating_org_role")
            # Note: value is not available in participating_org in IATI Datastore
            activity_partner_count = len(org_roles) if org_roles else 0
            
            for role in org_roles:
                if role:
                    role_counts[role] += 1
                    # role_values[role] += value  # No value field available
                    total_partners += 1
        
        # Build results
        partnership_roles = {}
        for role_code, count in role_counts.most_common():
            role_info = PARTNERSHIP_ROLES.get(role_code, {"name": f"Role {role_code}", "description": ""})
            partnership_roles[role_code] = {
                "name": role_info["name"],
                "description": role_info["description"],
                "count": count,
                "total_value": 0  # Value not available in IATI Datastore for participating_org
            }
        
        return {
            "total_activities": len(activities),
            "total_partners": total_partners,
            "average_partners_per_activity": round(total_partners / len(activities), 2) if activities else 0,
            "partnership_roles": partnership_roles,
            "role_definitions": PARTNERSHIP_ROLES
        }
        
    except IATIError as e:
        logger.error(f"Error in unhcr_partnership_analysis: {e}")
        return {"error": str(e), "partnership_roles": {}}
    except Exception as e:
        logger.exception("Unexpected error in unhcr_partnership_analysis")
        return {"error": str(e), "partnership_roles": {}}


# =============================================================================
# QUESTION 6: Expenditure vs Budget Comparison
# =============================================================================

@mcp.tool(
    name="unhcr_budget_vs_expenditure",
    description="Compare budget vs expenditure for financial tracking"
)
async def unhcr_budget_vs_expenditure(
    year: Optional[int] = None,
    country_code: Optional[str] = None,
    max_records: int = DEFAULT_MAX_RECORDS
) -> List[Dict[str, Any]]:
    """Compare budget vs expenditure for financial tracking."""
    try:
        # Fetch budgets and transactions
        q = unhcr_filter()
        if country_code:
            q += f' AND recipient_country_code:"{country_code}"'
        if year:
            q += f' AND (budget_period_start:[{year}-01-01T00:00:00Z TO {year}-12-31T23:59:59Z] '
            q += f'OR transaction_value_value_date:[{year}-01-01T00:00:00Z TO {year}-12-31T23:59:59Z])'
        
        # Get budgets
        budgets = await iati_client.fetch_all(
            collection="budget",
            q=q,
            max_records=max_records
        )
        
        # Get transactions (expenditure only)
        transactions = await iati_client.fetch_all(
            collection="transaction",
            q=q,
            max_records=max_records
        )
        
        # Group budgets by activity
        activity_budgets = defaultdict(float)
        for budget in budgets:
            activity_id = _safe_get_str(budget, "iati_identifier")
            value = _safe_get_float(budget, "budget_value")
            activity_budgets[activity_id] += value
        
        # Group transactions by activity (expenditure only)
        activity_expenditures = defaultdict(float)
        for tx in transactions:
            activity_id = _safe_get_str(tx, "iati_identifier")
            # Check if this is an expenditure transaction
            # Expenditure transactions typically have transaction_type_code indicating disbursement
            tx_type = _safe_get_str(tx, "transaction_type_code")
            value = _safe_get_float(tx, "transaction_value")
            
            # Include all transactions for now (can be refined)
            if value > 0:
                activity_expenditures[activity_id] += value
        
        # Compare budget vs expenditure
        results = []
        for activity_id, budget_value in activity_budgets.items():
            expenditure_value = activity_expenditures.get(activity_id, 0)
            deviation_amount = expenditure_value - budget_value
            deviation_percentage = round((deviation_amount / budget_value) * 100, 2) if budget_value > 0 else 0
            
            if deviation_amount > 0:
                status = "Over budget"
            elif deviation_amount < -0.05 * budget_value:  # More than 5% under
                status = "Under budget"
            else:
                status = "On track"
            
            results.append({
                "activity_id": activity_id,
                "activity_title": f"Activity {activity_id}",
                "budget_value": budget_value,
                "expenditure_value": expenditure_value,
                "deviation_amount": deviation_amount,
                "deviation_percentage": deviation_percentage,
                "status": status
            })
        
        # Sort by absolute deviation
        results.sort(key=lambda x: abs(x["deviation_amount"]), reverse=True)
        
        return results
        
    except IATIError as e:
        logger.error(f"Error in unhcr_budget_vs_expenditure: {e}")
        return []
    except Exception as e:
        logger.exception("Unexpected error in unhcr_budget_vs_expenditure")
        return []


# =============================================================================
# QUESTION 7: Indicator Evolution Over Time
# =============================================================================

@mcp.tool(
    name="unhcr_indicator_trends",
    description="Track indicator evolution over time for performance monitoring"
)
async def unhcr_indicator_trends(
    indicator_ref: Optional[str] = None,
    country_code: Optional[str] = None,
    start_year: int = 2020,
    end_year: int = 2025,
    max_records: int = DEFAULT_MAX_RECORDS
) -> List[Dict[str, Any]]:
    """Track indicator evolution over time for performance monitoring."""
    try:
        # Build query for indicators
        q = unhcr_filter()
        if country_code:
            q += f' AND recipient_country_code:"{country_code}"'
        
        # Fetch indicators/results
        # Note: In IATI, indicators are typically in the result element of activities
        activities = await iati_client.fetch_all(
            collection="activity",
            q=q,
            max_records=max_records
        )
        
        # Extract and aggregate indicator data by year
        indicator_data = defaultdict(lambda: defaultdict(list))
        
        for activity in activities:
            # Get activity date to determine year
            activity_date = _safe_get_str(activity, "activity_date_iso_date")
            year = None
            if activity_date:
                try:
                    year = int(activity_date[:4])
                except (ValueError, IndexError):
                    pass
            
            if not year or year < start_year or year > end_year:
                continue
            
            # In IATI Datastore, result_indicator is stored as separate list fields
            # We need to reconstruct the indicator structure from these fields
            indicator_refs = _safe_get_list(activity, "result_indicator_ref")
            indicator_titles = _safe_get_list(activity, "result_indicator_title_narrative")
            indicator_types = _safe_get_list(activity, "result_indicator_measure")
            
            # Get baseline values
            baseline_values = _safe_get_list(activity, "result_indicator_baseline_value")
            
            # Get period actual and target values
            # These are repeated for each period, so we take the first set
            actual_values = _safe_get_list(activity, "result_indicator_period_actual_value")
            target_values = _safe_get_list(activity, "result_indicator_period_target_value")
            
            # Process each indicator
            num_indicators = max(len(indicator_refs), len(indicator_titles), len(indicator_types))
            for i in range(num_indicators):
                ref = indicator_refs[i] if i < len(indicator_refs) else f"indicator_{i}"
                title = indicator_titles[i] if i < len(indicator_titles) else ""
                ind_type = indicator_types[i] if i < len(indicator_types) else ""
                
                # Get values (use first available if lists are shorter)
                actual = float(actual_values[i]) if i < len(actual_values) and actual_values[i] else 0
                target = float(target_values[i]) if i < len(target_values) and target_values[i] else 0
                baseline = float(baseline_values[i]) if i < len(baseline_values) and baseline_values[i] else 0
                
                # Store indicator data
                if indicator_ref and ref != indicator_ref:
                    continue
                
                indicator_data[ref][year].append({
                    "actual": actual,
                    "target": target,
                    "baseline": baseline,
                    "title": title,
                    "type": ind_type
                })
        
        # Aggregate by year (take average if multiple values per year)
        results = []
        for ref, year_data in indicator_data.items():
            for year, values in year_data.items():
                # Average the values for this year
                avg_actual = sum(v["actual"] for v in values) / len(values) if values else 0
                avg_target = sum(v["target"] for v in values) / len(values) if values else 0
                avg_baseline = sum(v["baseline"] for v in values) / len(values) if values else 0
                
                title = values[0]["title"] if values else f"Indicator {ref}"
                ind_type = values[0]["type"] if values else "Unknown"
                
                # Map type codes to readable names
                type_map = {
                    "1": "Impact",
                    "2": "Outcome", 
                    "3": "Output"
                }
                type_name = type_map.get(ind_type, ind_type)
                
                progress = round((avg_actual / avg_target) * 100, 2) if avg_target > 0 else 0
                deviation = avg_actual - avg_target
                
                results.append({
                    "indicator_ref": ref,
                    "indicator_title": title,
                    "indicator_type": type_name,
                    "indicator_type_code": ind_type,
                    "year": year,
                    "actual_value": avg_actual,
                    "target_value": avg_target,
                    "baseline_value": avg_baseline,
                    "progress_percentage": progress,
                    "deviation_from_target": deviation
                })
        
        # Sort by year and then by progress
        results.sort(key=lambda x: (x["year"], -x["progress_percentage"]))
        
        return results
        
    except IATIError as e:
        logger.error(f"Error in unhcr_indicator_trends: {e}")
        return []
    except Exception as e:
        logger.exception("Unexpected error in unhcr_indicator_trends")
        return []


# =============================================================================
# UTILITY: Get All 7 Analytical Questions Summary
# =============================================================================

@mcp.tool(
    name="unhcr_analytical_questions_summary",
    description="Get summary of all 7 core analytical questions"
)
async def unhcr_analytical_questions_summary(
    country_code: Optional[str] = None,
    year: Optional[int] = None
) -> Dict[str, Any]:
    """Get summary of all 7 core analytical questions."""
    results = {}
    
    try:
        # Run all 7 analyses
        results["most_funded_sectors"] = await unhcr_most_funded_sectors(
            country_code=country_code, year=year, top_n=5
        )
    except Exception as e:
        results["most_funded_sectors"] = {"error": str(e)}
    
    try:
        results["top_donors"] = await unhcr_top_donors_by_country(
            country_code=country_code, year=year, top_n=5
        )
    except Exception as e:
        results["top_donors"] = {"error": str(e)}
    
    try:
        results["implementing_partners"] = await unhcr_implementing_partners(
            country_code=country_code, top_n=5
        )
    except Exception as e:
        results["implementing_partners"] = {"error": str(e)}
    
    try:
        results["earmarking_breakdown"] = await unhcr_earmarking_breakdown(
            country_code=country_code, year=year
        )
    except Exception as e:
        results["earmarking_breakdown"] = {"error": str(e)}
    
    try:
        results["partnership_analysis"] = await unhcr_partnership_analysis(
            country_code=country_code
        )
    except Exception as e:
        results["partnership_analysis"] = {"error": str(e)}
    
    try:
        results["budget_vs_expenditure"] = await unhcr_budget_vs_expenditure(
            country_code=country_code, year=year
        )
    except Exception as e:
        results["budget_vs_expenditure"] = {"error": str(e)}
    
    try:
        results["indicator_trends"] = await unhcr_indicator_trends(
            country_code=country_code, start_year=year or 2020, end_year=year or 2025
        )
    except Exception as e:
        results["indicator_trends"] = {"error": str(e)}
    
    return {
        "metadata": {
            "country_code": country_code,
            "year": year,
            "timestamp": "2026-07-05",
            "questions_answered": 7
        },
        "results": results
    }
