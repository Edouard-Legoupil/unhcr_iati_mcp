# Troubleshooting

This document provides comprehensive troubleshooting guidance for the UNHCR IATI MCP Server.

## Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Server fails to start | Missing `IATI_API_KEY` | Set `IATI_API_KEY` environment variable |
| Import errors | Missing dependencies | Run `pip install -e .` |
| Connection timeout | Network issues | Check connection, increase `TIMEOUT_SECONDS` |
| Rate limit errors | Too many requests | Implement caching, use `fetch_all` with smaller batches |
| Authentication errors | Invalid API key | Verify your IATI API key is correct |
| Empty results | Incorrect filter | Check `UNHCR_PUBLISHER_REF` is set to `XM-DAC-41121` |
| Sector aggregation errors | Mixing vocabularies | Use `get_sectors_by_vocabulary()` to group by vocabulary first |
| Result framework parsing | Missing result fields | Use Activity model's `get_results_with_indicators()` method |
| Code table not found | Table not in data/codelists/ | Use `list_code_table(code_type="country")` to check available code types |
| Cache issues | Stale code table data | Code tables load on-demand; restart server to clear cache |
| Invalid indicator data | Non-numeric values for quantitative | Use `validate_indicator_data()` to check data quality |
| Context window exceeded | Too many tools/resources loaded | Use specific tools instead of listing all; see Context Window section below |

## Context Window Issues

### Symptom
Error: "The conversation context exceeds the model's maximum limit" when loading tools from the MCP server.

### Cause
The MCP server's tool and resource definitions consume context window space. With the current optimization:
- **33 tools** + **17 resources** = ~55K tokens total
- This fits within 64K+ context windows but may exceed 32K windows

### Solutions

1. **Use specific tools** instead of listing all:
   ```python
   # Instead of:
   tools = await client.list_tools()
   
   # Use specific tool directly:
   result = await client.call_tool("unhcr_activities", {"rows": 10})
   ```

2. **Access code tables via tools** (not as resources):
   ```python
   # Instead of:
   resource = await client.read_resource("unhcr://codes/country")
   
   # Use:
   result = await client.call_tool("resolve_code", {
       "code_type": "country",
       "code": "SYR"
   })
   ```

3. **Request smaller result sets**:
   ```python
   # Use max_records parameter
   result = await client.call_tool("unhcr_activities", {
       "rows": 100,  # or max_records
       "start": 0
   })
   ```

4. **Use models with larger context windows** (64K+ recommended)

### Optimization Details

The server has been optimized to reduce context window usage:
- **Shortened docstrings**: From 500-1000+ chars to <100 chars
- **Removed 44 code table resources**: Access via code resolution tools instead
- **Lazy loading**: Code tables load on-demand, not at startup
- **Result**: ~55K tokens (down from ~91K)

## Debug Mode

Enable verbose logging to troubleshoot issues:

```bash
LOG_LEVEL=DEBUG python -m unhcr_iati_mcp.server
```

This will output detailed information about:
- HTTP requests and responses
- Query execution
- Retry attempts
- Error details
- Performance metrics

## Testing Connection

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

## Checking API Key

Verify your IATI API key is valid:

1. Go to https://developer.iatistandard.org/
2. Log in to your account
3. Check your subscription key
4. Test it with a simple curl request:

```bash
curl -H "Ocp-Apim-Subscription-Key: YOUR_API_KEY" \
  "https://api.iatistandard.org/datastore/activity/select?q=*:*&rows=1"
```

## Docker Issues

### Problem: Build fails

```bash
# Make sure you have the correct Python version
docker --version
python --version

# Clean build
docker-compose build --no-cache
```

### Problem: Container exits immediately

```bash
# Check logs
docker-compose logs mcp

# Run interactively to see errors
docker-compose run mcp bash
```

### Problem: Port already in use

```yaml
# Change port in docker-compose.yml
ports:
  - "8080:8000"  # Map to different host port
```

## Sector Data Issues

### Issue: Sector aggregation returns incorrect results

**Problem**: You're aggregating sector codes across different vocabularies.

**Solution**: Always group by vocabulary first:

```python
# ❌ WRONG
from collections import Counter
sector_counter = Counter()
for activity in activities:
    for code in activity["sector_code"]:
        sector_counter[code] += 1  # This is WRONG!

# ✅ CORRECT
from collections import defaultdict
sectors_by_vocab = defaultdict(lambda: defaultdict(int))
for activity in activities:
    for code, vocab in zip(activity["sector_code"], activity["sector_vocabulary"]):
        sectors_by_vocab[vocab][code] += 1

# Then analyze each vocabulary separately
for vocab, sectors in sectors_by_vocab.items():
    print(f"Vocabulary {vocab}: {dict(sectors)}")
```

### Issue: Using wrong vocabulary

**Problem**: You're using IASC vocabulary (10) when you should be using UNHCR vocabulary (98).

**Solution**: Always specify the vocabulary:

```python
# Use UNHCR vocabulary 98 for UNHCR-specific analysis
unhcr_sectors = activity.get_unhcr_sectors()

# Or filter by vocabulary
sectors_v98 = [s for s in activity.get_sector_info() if s.sector_vocabulary == "98"]
```

### Issue: Mixed vocabularies in results

**Problem**: Your query returns activities with mixed sector vocabularies.

**Solution**: Validate before aggregation:

```python
from unhcr_iati_mcp.models.activity import Activity

activity = Activity(**activity_data)

# Check for mixed vocabularies
if activity.has_mixed_vocabularies():
    # Handle mixed vocabularies
    sectors_by_vocab = activity.get_sectors_by_vocabulary()
    for vocab, sectors in sectors_by_vocab.items():
        print(f"Vocabulary {vocab}: {sectors}")
else:
    # Safe to aggregate
    all_sectors = activity.get_sector_info()
```

## Result Framework Issues

### Issue: Result data not parsed correctly

**Problem**: Result framework data is in raw format and needs parsing.

**Solution**: Use the Activity model's built-in methods:

```python
# ✅ CORRECT
activity = Activity(**activity_data)

# Get results with their indicators (SAFEST approach)
results_with_indicators = activity.get_results_with_indicators()

# Group indicators by result type
indicators_by_type = activity.get_indicators_by_type()

# Filter to quantitative indicators only
quantitative = activity.get_quantitative_indicators()
```

### Issue: Missing indicator values

**Problem**: Some indicators have missing baseline, target, or actual values.

**Solution**: Handle missing values gracefully:

```python
# Check if indicator has valid data
if indicator.baseline_value and indicator.period_target_value and indicator.period_actual_value:
    # Calculate progress
    try:
        progress = calculate_progress_percentage(
            baseline=float(indicator.baseline_value),
            target=float(indicator.period_target_value),
            actual=float(indicator.period_actual_value)
        )
    except (ValueError, TypeError):
        progress = None
```

## Code Table Issues

### Issue: Code table not found

**Problem**: Requested code table doesn't exist.

**Solution**: Check available tables:

```python
# Via MCP resource
available = await client.read_resource("unhcr://codes/available")
print(f"Available tables: {available}")

# Or check metadata
metadata = await client.read_resource("unhcr://codes/metadata")
for table in metadata:
    print(f"{table['table_name']}: {table['description']}")
```

### Issue: Code table load failure

**Problem**: Code table fails to load from disk.

**Solution**: Reload code tables or restart server:

```python
from unhcr_iati_mcp.resources.code_tables import reload_code_tables

# Reload all code tables
reload_code_tables()

# Or reload specific table
from unhcr_iati_mcp.resources.code_tables import _load_code_table
try:
    table = _load_code_table("codeCountry")
except Exception as e:
    print(f"Failed to load table: {e}")
```

## Performance Issues

### Issue: Slow queries

**Problem**: Queries are taking too long to execute.

**Solutions**:

1. **Use pagination**: Limit the number of records per request
   ```python
   data = await client.query(collection="activity", rows=100)  # Not 10000
   ```

2. **Use fetch_all with reasonable limits**:
   ```python
   data = await client.fetch_all(collection="activity", max_records=5000)
   ```

3. **Select specific fields**: Only request fields you need
   ```python
   data = await client.query(
       collection="activity",
       fl="iati_identifier,title_narrative,recipient_country_code"
   )
   ```

4. **Use filters**: Reduce the result set with filters
   ```python
   data = await client.query(
       collection="activity",
       q='reporting_org_ref:"XM-DAC-41121" AND recipient_country_code:SYR'
   )
   ```

### Issue: Memory usage too high

**Problem**: Server is using too much memory.

**Solutions**:

1. **Reduce cache size**: Code tables are cached; clear unused tables
2. **Use lazy loading**: Only load code tables when needed
3. **Limit page size**: Use smaller page sizes for queries
4. **Restart server**: Regularly restart to clear memory

## Data Quality Issues

### Issue: Incomplete activity data

**Problem**: Some activities have missing fields.

**Solution**: Handle missing data gracefully:

```python
# Use get() with defaults
name = activity.get("title_narrative", ["Unknown"])[0]

# Or use Activity model methods that handle missing data
sector_info = activity.get_sector_info()  # Returns empty list if no sectors
```

### Issue: Invalid date formats

**Problem**: Date fields have inconsistent formats.

**Solution**: Parse dates with error handling:

```python
from datetime import datetime
from dateutil.parser import parse

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return parse(date_str).date()
    except (ValueError, TypeError):
        return None

date = parse_date(activity.get("activity_date"))
```

### Issue: Currency conversion needed

**Problem**: Financial values are in different currencies.

**Solution**: Normalize to a base currency or handle per-currency:

```python
# Group by currency
from collections import defaultdict
by_currency = defaultdict(float)

for value, currency in zip(activity.budget_value, activity.budget_value_currency):
    by_currency[currency] += value

# Or use a currency conversion library
# Note: This requires external rate data
```

## Network Issues

### Issue: Connection timeout

**Problem**: Connection to IATI Datastore times out.

**Solutions**:

1. Increase timeout:
   ```bash
   TIMEOUT_SECONDS=300 python -m unhcr_iati_mcp.server
   ```

2. Check network connectivity:
   ```bash
   ping api.iatistandard.org
   curl -v https://api.iatistandard.org/datastore/activity/select
   ```

3. Check proxy settings:
   ```bash
   # If behind proxy
   export HTTP_PROXY=http://proxy:port
   export HTTPS_PROXY=http://proxy:port
   ```

### Issue: SSL/TLS errors

**Problem**: SSL certificate verification fails.

**Solutions**:

1. Update CA certificates:
   ```bash
   # On Ubuntu/Debian
   sudo apt-get update && sudo apt-get install --reinstall ca-certificates
   ```

2. Disable SSL verification (not recommended for production):
   ```python
   import ssl
   ssl._create_default_https_context = ssl._create_unverified_context
   ```

## Error Handling Best Practices

### Retry Logic

The client has built-in retry logic. Configure it appropriately:

```python
from unhcr_iati_mcp.client import IATIClient

# Custom retry configuration
client = IATIClient(
    max_retries=10,  # Default is 5
    retry_delay=2,   # Base delay in seconds
    max_delay=60     # Maximum delay in seconds
)
```

### Error Classification

Handle different error types appropriately:

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
    # Handle generic error
```

## Getting Help

### Check Server Status

```python
# Health check
health = await client.call_tool("health_check", {})

# System status
status = await client.call_tool("system_status", {})

# API limits
limits = await client.call_tool("api_limits", {})
```

### Review Logs

```bash
# View recent logs
journalctl -u unhcr-iati-mcp -n 100 --no-pager

# Filter logs by error
grep ERROR /var/log/unhcr_iati_mcp.log

# Follow logs in real-time
tail -f /var/log/unhcr_iati_mcp.log
```

### Common Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 400 | Bad Request | Check query syntax |
| 401 | Unauthorized | Verify API key |
| 403 | Forbidden | Check permissions |
| 404 | Not Found | Verify endpoint URL |
| 429 | Too Many Requests | Wait and retry |
| 500 | Internal Server Error | Check server logs |
| 502 | Bad Gateway | Check proxy/load balancer |
| 503 | Service Unavailable | Wait and retry |
| 504 | Gateway Timeout | Check backend services |
