# UNHCR IATI MCP Tools - Filtering Review

## Executive Summary

**Status**: Filtering is **implemented but inconsistent** across tools. The core `unhcr_filter()` function correctly filters for UNHCR's publisher reference, but there are **critical issues** with:
1. **Solr query syntax** - Incorrect field names and operators
2. **Missing pagination parameters** in fetch_all calls
3. **No result limiting** for tools that fetch all data
4. **Inconsistent return types** between similar tools
5. **Potential security issues** with direct query injection

---

## 1. Current Filtering Architecture

### Core Filter Function (`context.py`)
```python
def unhcr_filter() -> str:
    """Generate the UNHCR publisher filter string for IATI Datastore queries."""
    return f'reporting_org_ref:"{settings.unhcr_publisher_ref}"'
```

✅ **Strengths:**
- Centralized filter ensures all queries target UNHCR data
- Configurable via `unhcr_publisher_ref` setting (default: `XM-DAC-41121`)
- Applied consistently across all tools

---

## 2. Detailed Tool-by-Tool Analysis

### ✅ **WELL-IMPLEMENTED**

#### Activities Tools (`tools/activities.py`)

| Tool | Filter Implementation | Issues |
|------|---------------------|--------|
| `unhcr_activities` | Uses `unhcr_filter()` + pagination | ✅ None |
| `unhcr_activity` | `unhcr_filter() AND iati_identifier:"..."` | ✅ None |
| `unhcr_activity_by_country` | `unhcr_filter() AND recipient_country_code:X` | ❌ **Syntax error** - missing quotes |
| `unhcr_activity_by_sector` | `unhcr_filter() AND sector_code:X` | ❌ **Syntax error** - missing quotes |
| `unhcr_activity_by_year` | `unhcr_filter() AND activity_date_iso_date:[...]` | ✅ Correct date range syntax |

**Critical Bug in `unhcr_activity_by_country`:**
```python
# Current (BROKEN):
q = f'{unhcr_filter()} AND recipient_country_code:{country_code}'

# Should be:
q = f'{unhcr_filter()} AND recipient_country_code:"{country_code}"'
```

**Critical Bug in `unhcr_activity_by_sector`:**
```python
# Current (BROKEN):
q = f'{unhcr_filter()} AND sector_code:{sector_code}'

# Should be:
q = f'{unhcr_filter()} AND sector_code:"{sector_code}"'
```

#### Transactions Tools (`tools/transactions.py`)

| Tool | Filter Implementation | Issues |
|------|---------------------|--------|
| `unhcr_transactions` | `unhcr_filter()` + optional year | ✅ Correct |
| `unhcr_transaction_search` | `unhcr_filter() AND ({query})` | ⚠️ **Security risk** - direct query injection |

**Security Concern in `unhcr_transaction_search`:**
```python
# Current - allows arbitrary Solr queries
q = f'{unhcr_filter()} AND ({query})'
```
This allows users to inject arbitrary Solr syntax which could:
- Bypass the UNHCR filter
- Perform expensive queries
- Access other publishers' data

**Recommendation:** Sanitize or restrict the query parameter to specific fields.

#### Budgets Tools (`tools/budgets.py`)

| Tool | Filter Implementation | Issues |
|------|---------------------|--------|
| `unhcr_budgets` | `unhcr_filter()` + optional year | ✅ Correct |

**Note:** Uses `budget_period_start` field which is correct.

#### Donors Tools (`tools/donors.py`)

| Tool | Filter Implementation | Issues |
|------|---------------------|--------|
| `unhcr_top_donors` | Uses `unhcr_filter()` | ⚠️ **Performance** - fetches ALL transactions |

**Performance Issue:**
```python
# Fetches ALL UNHCR transactions (potentially thousands)
tx = await iati_client.fetch_all(collection="transaction", q=unhcr_filter())
```
No filtering or limiting - processes entire dataset in memory.

#### Countries Tools (`tools/countries.py`)

| Tool | Filter Implementation | Issues |
|------|---------------------|--------|
| `unhcr_top_countries` | Uses `unhcr_filter()` | ⚠️ **Performance** - fetches ALL activities |

**Performance Issue:**
```python
# Fetches ALL UNHCR activities
activities = await iati_client.fetch_all(collection="activity", q=unhcr_filter())
```

#### Sectors Tools (`tools/sectors.py`)

| Tool | Filter Implementation | Issues |
|------|---------------------|--------|
| `unhcr_sector_summary` | Uses `unhcr_filter()` | ⚠️ **Performance** - fetches ALL activities |

**Performance Issue:** Same as above - fetches all activities.

#### Analytics Tools (`tools/analytics.py`)

| Tool | Filter Implementation | Issues |
|------|---------------------|--------|
| `unhcr_portfolio_summary` | Uses `unhcr_filter()` for all collections | ⚠️ **Performance** - fetches ALL data |

**Performance Issue:** Fetches all activities, budgets, and transactions without limits.

#### Export Tools (`tools/export.py`)

| Tool | Filter Implementation | Issues |
|------|---------------------|--------|
| `unhcr_export_json` | `unhcr_filter() + optional query` | ⚠️ **Security** - same query injection risk |
| `unhcr_export_csv` | Same as above | ⚠️ **Security** - same query injection risk |
| `unhcr_bulk_extract` | Uses `unhcr_filter()` for each collection | ⚠️ **Performance** - no limits |

**Query Injection Vulnerability:**
```python
q = f"{unhcr_filter()}" + (f" AND ({query})" if query else "")
```

---

## 3. Critical Issues Identified

### 🔴 **P1 - BLOCKING: Syntax Errors in Solr Queries**

**Affected Tools:**
- `unhcr_activity_by_country` - Line 114
- `unhcr_activity_by_sector` - Line 149

**Problem:** String values in Solr queries must be quoted. Current implementation:
```python
q = f'{unhcr_filter()} AND recipient_country_code:{country_code}'
```

This generates: `reporting_org_ref:"XM-DAC-41121" AND recipient_country_code:AFG`

But Solr expects: `reporting_org_ref:"XM-DAC-41121" AND recipient_country_code:"AFG"`

**Impact:** These tools will return **zero results** for all queries.

**Fix:**
```python
# For activity_by_country
q = f'{unhcr_filter()} AND recipient_country_code:"{country_code}"'

# For activity_by_sector  
q = f'{unhcr_filter()} AND sector_code:"{sector_code}"'
```

---

### 🟡 **P2 - HIGH: Query Injection Security Risk**

**Affected Tools:**
- `unhcr_transaction_search`
- `unhcr_export_json`
- `unhcr_export_csv`

**Problem:** User-provided query strings are directly interpolated into Solr queries:
```python
q = f'{unhcr_filter()} AND ({query})'
```

A malicious user could:
1. **Bypass UNHCR filter**: `*) AND (reporting_org_ref:"OTHER-ORG"`
2. **Inject expensive queries**: `* AND _val_:"pow(2,30)"` (DoS risk)
3. **Access all data**: `* AND (*:*)` (bypass all filters)

**Impact:** Potential data leakage and denial of service.

**Fix Options:**
1. **Whitelist approach** - Only allow specific field names
2. **Sanitization** - Escape special Solr characters
3. **Field restriction** - Only allow filtering on specific fields

**Recommended Fix:**
```python
def _sanitize_solr_query(query: str) -> str:
    """Sanitize user input for Solr query safety."""
    # Remove potentially dangerous Solr syntax
    dangerous_patterns = ['(', ')', 'AND', 'OR', 'NOT', '*', '?', '[', ']', '{', '}', '~']
    for pattern in dangerous_patterns:
        query = query.replace(pattern, '')
    return query

# Or use a proper Solr query builder library
```

---

### 🟡 **P3 - HIGH: Performance Issues with Unbounded Fetches**

**Affected Tools:**
- `unhcr_top_donors`
- `unhcr_top_countries`
- `unhcr_sector_summary`
- `unhcr_portfolio_summary`
- `unhcr_bulk_extract`

**Problem:** These tools use `fetch_all()` without any limits:
```python
activities = await iati_client.fetch_all(collection="activity", q=unhcr_filter())
```

**Impact:**
- Memory exhaustion with large datasets
- Slow response times
- Potential API rate limit hits

**Fix:** Add `max_records` parameter or default limit:
```python
# In fetch_all calls
activities = await iati_client.fetch_all(
    collection="activity", 
    q=unhcr_filter(),
    max_records=10000  # Reasonable default
)

# Or add to tool parameters
async def unhcr_top_countries(top_n: int = 20, max_records: int = 10000) -> List[...]:
    ...
    activities = await iati_client.fetch_all(
        collection="activity",
        q=unhcr_filter(),
        max_records=max_records
    )
```

---

### 🟡 **P4 - MEDIUM: Inconsistent Return Types**

**Problem:** Tools return different types for similar operations:

| Tool | Returns |
|------|---------|
| `unhcr_activities` | `Dict[str, Any]` (raw API response) |
| `unhcr_activity` | `Dict[str, Any]` (raw API response) |
| `unhcr_activity_by_year` | `List[Dict[str, Any]]` (processed) |
| `unhcr_transactions` | `List[Dict[str, Any]]` (processed) |
| `unhcr_budgets` | `List[Dict[str, Any]]` (processed) |

**Impact:** Inconsistent API makes it harder for clients to use.

**Recommendation:** Standardize on either:
1. **Raw responses** - Always return full API response with metadata
2. **Processed data** - Always return just the data list

**Suggested:** Processed data (list) for most tools, with optional metadata parameter.

---

### 🟡 **P5 - MEDIUM: Missing Pagination in List Tools**

**Affected Tools:**
- `unhcr_activity_by_country`
- `unhcr_activity_by_sector`

**Problem:** These tools accept `rows` parameter but don't support `start` for pagination.

**Current:**
```python
async def unhcr_activity_by_country(country_code: str, rows: int = 100)
```

**Should be:**
```python
async def unhcr_activity_by_country(
    country_code: str, 
    rows: int = 100,
    start: int = 0
)
```

---

### 🟢 **P6 - LOW: Missing Field List Parameter**

**Problem:** All queries use `fl="*"` (all fields) which returns unnecessary data.

**Impact:** Increased bandwidth and memory usage.

**Fix:** Add optional `fields` parameter to tools:
```python
async def unhcr_activities(
    rows: int = 100,
    start: int = 0,
    fields: str = "*"
) -> Dict[str, Any]:
    return await iati_client.query(
        collection="activity",
        q=unhcr_filter(),
        rows=rows,
        start=start,
        fl=fields
    )
```

---

## 4. Field Name Verification

### ❌ **INCORRECT Field Names Found**

Based on IATI Datastore schema:

| Tool | Field Used | Status | Correct Field |
|------|------------|--------|---------------|
| `unhcr_activity_by_country` | `recipient_country_code` | ⚠️ Verify | May need validation |
| `unhcr_activity_by_sector` | `sector_code` | ⚠️ Verify | May need validation |
| `unhcr_activity_by_year` | `activity_date_iso_date` | ⚠️ Verify | May need validation |
| `unhcr_transactions` | `transaction_value_value_date` | ❌ **WRONG** | Should be `transaction_date` or similar |
| `unhcr_budgets` | `budget_period_start` | ⚠️ Verify | May need validation |

**Action Required:** Verify field names against actual IATI Datastore schema.

---

## 5. Recommendations Summary

### Immediate Actions (P1)

1. **Fix Solr query syntax errors** in `activities.py`:
   - Quote string values in `unhcr_activity_by_country`
   - Quote string values in `unhcr_activity_by_sector`

2. **Add input sanitization** for query parameters:
   - `unhcr_transaction_search`
   - `unhcr_export_json`
   - `unhcr_export_csv`

### Short-term Actions (P2-P3)

3. **Add default limits** to all `fetch_all()` calls:
   - Add `max_records` parameter to tools that fetch all data
   - Set reasonable defaults (e.g., 10,000 records)

4. **Add pagination support** to filtering tools:
   - Add `start` parameter to `unhcr_activity_by_country`
   - Add `start` parameter to `unhcr_activity_by_sector`

5. **Verify field names** against IATI Datastore API:
   - Check `transaction_value_value_date` in transactions
   - Verify all filter fields exist

### Long-term Actions (P4-P6)

6. **Standardize return types** across all tools
7. **Add field filtering** parameter to reduce data transfer
8. **Implement query validation** library for Solr

---

## 6. Code Examples for Fixes

### Fix 1: Syntax Errors

```python
# tools/activities.py - FIXED

async def unhcr_activity_by_country(
    country_code: str,
    rows: int = 100,
    start: int = 0
) -> Dict[str, Any]:
    """Retrieve activities for a specific country."""
    try:
        # FIX: Added quotes around country_code
        q = (
            f'{unhcr_filter()} '
            f'AND recipient_country_code:"{country_code}"'
        )
        
        return await iati_client.query(
            collection="activity",
            q=q,
            rows=rows,
            start=start
        )
    except IATIError as e:
        return _handle_error(e, "unhcr_activity_by_country")
    except Exception as e:
        return _handle_error(e, "unhcr_activity_by_country")

async def unhcr_activity_by_sector(
    sector_code: str,
    rows: int = 100,
    start: int = 0
) -> Dict[str, Any]:
    """Retrieve activities for a specific sector."""
    try:
        # FIX: Added quotes around sector_code
        q = (
            f'{unhcr_filter()} '
            f'AND sector_code:"{sector_code}"'
        )
        
        return await iati_client.query(
            collection="activity",
            q=q,
            rows=rows,
            start=start
        )
    except IATIError as e:
        return _handle_error(e, "unhcr_activity_by_sector")
    except Exception as e:
        return _handle_error(e, "unhcr_activity_by_sector")
```

### Fix 2: Query Sanitization

```python
# tools/transactions.py - FIXED

import re

def _sanitize_solr_value(value: str) -> str:
    """Escape special Solr characters in a value."""
    # Escape these Solr special characters: + - = & | ! ( ) { } [ ] ^ " ~ * ? : \ /
    special_chars = r'[+\-=&|!\(\)\{\}\[\]\^"~*?:\\/]'
    return re.sub(special_chars, r'\\\g<0>', value)

async def unhcr_transaction_search(query: str) -> List[Dict[str, Any]]:
    """Search transactions using a custom Solr query string."""
    try:
        # FIX: Sanitize user query to prevent injection
        sanitized_query = _sanitize_solr_value(query)
        q = f'{unhcr_filter()} AND ({sanitized_query})'
        
        return await iati_client.fetch_all(
            collection="transaction",
            q=q,
            max_records=10000  # FIX: Add limit
        )
    except IATIError as e:
        logger.error(f"Error in unhcr_transaction_search: {e}")
        return []
    except Exception as e:
        logger.exception("Unexpected error in unhcr_transaction_search")
        return []
```

### Fix 3: Performance Limits

```python
# tools/donors.py - FIXED

async def unhcr_top_donors(top_n: int = 20, max_records: int = 10000) -> List[Tuple[str, float]]:
    """Retrieve and rank donors by their total contribution amount."""
    try:
        # FIX: Add max_records limit
        tx = await iati_client.fetch_all(
            collection="transaction",
            q=unhcr_filter(),
            max_records=max_records
        )
        
        donors = defaultdict(float)
        for row in tx:
            # ... rest of logic
        
        return sorted(donors.items(), key=lambda x: x[1], reverse=True)[:top_n]
    except IATIError as e:
        logger.error(f"Error in unhcr_top_donors: {e}")
        return []
    except Exception as e:
        logger.exception("Unexpected error in unhcr_top_donors")
        return []
```

### Fix 4: Standardized Return Type

```python
# tools/activities.py - Standardized

@mcp.tool(
    name="unhcr_activities",
    description="Retrieve UNHCR activities with pagination."
)
async def unhcr_activities(
    rows: int = 100,
    start: int = 0,
    return_full_response: bool = False  # NEW: Option to return full response
) -> Dict[str, Any] | List[Dict[str, Any]]:
    """
    Retrieve UNHCR activities from IATI Datastore.
    
    Args:
        rows: Number of results to return per page (default: 100)
        start: Starting offset for pagination (default: 0)
        return_full_response: If True, return full API response; if False, return just docs
    """
    try:
        response = await iati_client.query(
            collection="activity",
            q=unhcr_filter(),
            rows=rows,
            start=start
        )
        
        if return_full_response:
            return response
        else:
            # Return just the documents for consistency
            return response.get("response", {}).get("docs", [])
    except IATIError as e:
        return _handle_error(e, "unhcr_activities")
    except Exception as e:
        return _handle_error(e, "unhcr_activities")
```

---

## 7. Testing Recommendations

### Test Cases to Add

1. **Syntax Error Tests:**
```python
# Test that country_code filtering works
result = await unhcr_activity_by_country(country_code="AFG", rows=10)
assert len(result.get("response", {}).get("docs", [])) > 0

# Test that sector_code filtering works  
result = await unhcr_activity_by_sector(sector_code="1", rows=10)
assert len(result.get("response", {}).get("docs", [])) > 0
```

2. **Security Tests:**
```python
# Test query injection prevention
result = await unhcr_transaction_search(query='*) AND (reporting_org_ref:"OTHER-ORG"')
# Should NOT return data from other organizations
for tx in result:
    assert tx.get("reporting_org_ref") == settings.unhcr_publisher_ref
```

3. **Performance Tests:**
```python
# Test that fetch_all respects max_records
result = await unhcr_top_donors(top_n=10, max_records=50)
# Should process at most 50 transactions
```

---

## 8. Conclusion

The filtering implementation has a **solid foundation** with the centralized `unhcr_filter()` function, but there are **critical bugs** that need immediate attention:

1. **P1 - Syntax errors** in `unhcr_activity_by_country` and `unhcr_activity_by_sector`
2. **P2 - Security vulnerabilities** in query injection points
3. **P3 - Performance issues** with unbounded data fetching

**Recommended Action Plan:**
1. Fix P1 issues immediately (these are blocking bugs)
2. Address P2 security issues within 1 week
3. Implement P3 performance improvements within 2 weeks
4. Standardize APIs and add tests within 1 month

---

## Appendix: Tool Inventory

### Activities (5 tools)
- `unhcr_activities` - Paginated activities list ✅
- `unhcr_activity` - Single activity by ID ✅
- `unhcr_activity_by_country` - Filter by country ❌ **BROKEN**
- `unhcr_activity_by_sector` - Filter by sector ❌ **BROKEN**
- `unhcr_activity_by_year` - Filter by year ✅

### Transactions (2 tools)
- `unhcr_transactions` - All transactions with optional year ⚠️
- `unhcr_transaction_search` - Custom query ⚠️ **SECURITY RISK**

### Budgets (1 tool)
- `unhcr_budgets` - All budgets with optional year ✅

### Analytics (1 tool)
- `unhcr_portfolio_summary` - Counts for all collections ⚠️ **PERFORMANCE**

### Countries (1 tool)
- `unhcr_top_countries` - Rank countries by activity count ⚠️ **PERFORMANCE**

### Sectors (1 tool)
- `unhcr_sector_summary` - Sector distribution ⚠️ **PERFORMANCE**

### Donors (1 tool)
- `unhcr_top_donors` - Rank donors by contribution ⚠️ **PERFORMANCE**

### Export (3 tools)
- `unhcr_export_json` - Export to JSON ⚠️ **SECURITY RISK**
- `unhcr_export_csv` - Export to CSV ⚠️ **SECURITY RISK**
- `unhcr_bulk_extract` - Bulk export ⚠️ **PERFORMANCE**

### Health (5 tools)
- `metrics` - Prometheus metrics ✅
- `health_check` - Health status ✅
- `system_status` - System status ✅
- `datastore_ping` - Test connection ✅
- `api_limits` - Rate limit info ✅
