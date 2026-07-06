# Best Practices & Common Pitfalls

This document provides best practices and guidance for working with the UNHCR IATI MCP Server.

## Sector Data Analysis

### ❌ DON'T: Aggregate across different vocabularies

```python
# WRONG: Aggregating across different vocabularies
from collections import Counter
sector_counter = Counter()
for activity in activities:
    for code in activity["sector_code"]:
        sector_counter[code] += 1  # This is WRONG!
```

### ✅ DO: Group by vocabulary first

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

**Why**: Sector codes have different meanings across vocabularies. The same code (e.g., "10") in vocabulary 10 (IASC) means something different from code "10" in vocabulary 98 (UNHCR-specific).

## Result Framework Analysis

### ✅ DO: Use Activity model's built-in methods

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

### ❌ DON'T: Mix result types without context

```python
# WRONG: Mixing result types without context
all_indicators = []
for activity in activities:
    all_indicators.extend(activity["result_indicator_measure"])
    all_indicators.extend(activity["result_indicator_baseline_value"])
    # This loses the relationship between indicators and results!
```

## Working with Code Tables

### ✅ DO: Access code tables via MCP resources

```python
# Essential tables are pre-loaded
countries = await client.read_resource("unhcr://codes/country")

# Or use the client directly
from unhcr_iati_mcp.resources.code_tables import _load_code_table
countries = _load_code_table("codeCountry")

# Check what tables are available
available = await client.read_resource("unhcr://codes/available")
metadata = await client.read_resource("unhcr://codes/metadata")
```

### ✅ DO: Use lazy loading for non-essential tables

```python
# Non-essential tables are loaded on-demand
# They are cached after first load
special_table = _load_code_table("codeSomeSpecialTable")
```

### ✅ DO: Code tables are cached automatically

```python
# First call loads from disk, subsequent calls use cache
countries1 = _load_code_table("codeCountry")  # Loads from disk
countries2 = _load_code_table("codeCountry")  # Returns cached

# Check cache status
cache_status = await client.read_resource("unhcr://codes/cache_status")
print(f"Cache size: {cache_status['cache_size']} entries")
```

## Caching and Performance

### ✅ DO: Implement your own caching for frequent queries

```python
from functools import lru_cache

@lru_cache(maxsize=100)
async def get_activity(iati_identifier):
    return await client.call_tool("unhcr_activity", {"iati_identifier": iati_identifier})
```

### ✅ DO: Use fetch_all with appropriate limits

```python
# Good: Use reasonable limits
data = await client.fetch_all(collection="activity", max_records=10000)

# Bad: Don't fetch unlimited data
data = await client.fetch_all(collection="activity")  # No limit!
```

### ✅ DO: Select specific fields to reduce data transfer

```python
# Only request fields you need
data = await client.query(
    collection="activity",
    q='reporting_org_ref:"XM-DAC-41121"',
    fl="iati_identifier,title_narrative,recipient_country_code"
)
```

## Query Optimization

### ✅ DO: Use appropriate filters

```python
# Filter by country and sector
data = await client.query(
    collection="activity",
    q='reporting_org_ref:"XM-DAC-41121" AND recipient_country_code:SYR AND sector_code:122*'
)
```

### ✅ DO: Use date ranges for time-based queries

```python
# Query activities from a specific time period
data = await client.query(
    collection="activity",
    q='last_updated_datetime:[2024-01-01 TO 2024-12-31]'
)
```

### ❌ DON'T: Query without filters

```python
# BAD: This will return all UNHCR activities (potentially thousands)
data = await client.query(collection="activity", q='reporting_org_ref:"XM-DAC-41121"')

# GOOD: Add filters to reduce result set
data = await client.query(
    collection="activity",
    q='reporting_org_ref:"XM-DAC-41121"',
    rows=100,  # Limit results
    start=0
)
```

## Error Handling

### ✅ DO: Handle different error types appropriately

```python
from unhcr_iati_mcp.client import (
    IATIError, IATIAuthenticationError, 
    IATIRateLimitError, IATIServerError
)

try:
    data = await client.query(collection="activity", q="...")
except IATIAuthenticationError as e:
    logger.error("Authentication failed", error=str(e))
    # Re-authenticate or check API key
except IATIRateLimitError as e:
    logger.warning("Rate limit exceeded", error=str(e))
    # Wait and retry with backoff
except IATIServerError as e:
    logger.error("Server error", error=str(e))
    # Retry or failover
except IATIError as e:
    logger.error("General IATI error", error=str(e))
```

### ✅ DO: Implement retry logic with backoff

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_with_retry():
    return await client.query(collection="activity", q="...")
```

## Data Validation

### ✅ DO: Validate data before processing

```python
from unhcr_iati_mcp.models.activity import Activity

# Parse and validate activity data
activity = Activity(**activity_data)

# Validate sector aggregation
is_valid = activity.validate_sector_aggregation()
if not is_valid:
    # Handle invalid sector data
    sectors_by_vocab = activity.get_sectors_by_vocabulary()
    # Process each vocabulary separately
```

### ✅ DO: Check for mixed vocabularies

```python
# Check for mixed vocabularies before aggregation
if activity.has_mixed_vocabularies():
    # Process vocabularies separately
    sectors_by_vocab = activity.get_sectors_by_vocabulary()
else:
    # Safe to aggregate all sectors together
    all_sectors = activity.get_sector_info()
```

## Natural Language Query Examples

The MCP server is designed to work seamlessly with AI assistants. Here are examples of well-formed questions:

### Activity Queries

- "Show me UNHCR projects in Afghanistan"
- "What are the most recent UNHCR activities?"
- "Find UNHCR health projects in Kenya"
- "Get details for activity XM-DAC-41121-ACT-001"
- "What activities does UNHCR have in Uganda?"

### Financial Queries

- "What is the total budget for UNHCR projects in 2024?"
- "Show me transactions from Germany to UNHCR"
- "What are the top donors to UNHCR?"
- "Get budget breakdown by sector"

### Sector and Geographic Analysis

- "What sectors does UNHCR work in?"
- "Show me UNHCR education projects"
- "Which countries receive the most UNHCR funding?"
- "Get sector distribution for UNHCR activities"
- "What is UNHCR's sector vocabulary 98?"
- "What are the warnings about sector vocabulary aggregation?"

### Result Framework Queries

- "What are UNHCR's output-level results?"
- "Show me outcome indicators for UNHCR projects"
- "What are the 16 UNHCR Operational Areas?"
- "Get progress tracking for UNHCR indicators"
- "Show me indicators with disaggregation by sex and age"

### Advanced Queries

- "Find UNHCR projects about climate change and refugees"
- "Show me high-budget health projects in Syria"
- "Get activities updated in the last 30 days"
- "What are UNHCR's active projects?"

## Solr Query Syntax Reference

For advanced queries, use Solr syntax:

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
| **Sectors** | `sector_code`, `sector_narrative`, `sector_vocabulary` |
| **Financial** | `transaction_value`, `transaction_value_currency`, `budget_value` |
| **Dates** | `activity_date`, `last_updated_datetime`, `transaction_date` |
| **Organizations** | `participating_org_ref`, `provider_org_ref`, `receiver_org_ref` |
| **Status** | `activity_status_code` (1-6) |
| **Results** | `result_type`, `result_title_narrative`, `result_indicator_*` |

## Performance Best Practices

1. **Always use pagination**: Never fetch unlimited data
2. **Select specific fields**: Only request data you need
3. **Use filters**: Reduce result sets with appropriate filters
4. **Cache frequent queries**: Implement caching for repeated queries
5. **Handle errors gracefully**: Always have error handling in place
6. **Validate data**: Check data quality before processing
7. **Monitor performance**: Track query times and optimize slow queries
8. **Use async/await**: Take advantage of async operations

## Memory Management

1. **Limit cache size**: Don't cache unnecessary data
2. **Use generators**: Process large datasets with generators
3. **Clear unused data**: Regularly clear temporary data
4. **Monitor memory usage**: Track memory consumption
5. **Use lazy loading**: Load data on-demand when possible

## Security Best Practices

1. **Never hardcode API keys**: Always use environment variables
2. **Use HTTPS**: Always use encrypted connections
3. **Validate inputs**: Sanitize all user inputs
4. **Limit exposure**: Only expose necessary endpoints
5. **Use authentication**: Protect sensitive operations
6. **Log securely**: Don't log sensitive information
7. **Keep dependencies updated**: Regularly update dependencies
8. **Use secrets management**: Store secrets in a secure vault

## Testing Best Practices

1. **Test with real data**: Use actual IATI data in tests
2. **Test edge cases**: Handle missing data, empty results, errors
3. **Test performance**: Measure query times and optimize
4. **Test error handling**: Verify error paths work correctly
5. **Test with different vocabularies**: Ensure vocabulary handling is correct
6. **Test result framework**: Verify result data parsing works
7. **Test code tables**: Ensure all code tables load correctly
8. **Test caching**: Verify caching works as expected
