# Observability

This document describes the observability features of the UNHCR IATI MCP Server, including structured logging and Prometheus metrics.

## Overview

The server provides comprehensive observability through:

- **Structured Logging**: JSON-formatted logs with rich context
- **Prometheus Metrics**: Performance and health metrics for monitoring
- **Health Checks**: Endpoints to verify system status

## Structured Logging

The server uses `structlog` for structured JSON logging with context enrichment.

### Basic Usage

```python
from unhcr_iati_mcp.observability.logging import get_logger

logger = get_logger(__name__)

# Log with context
logger.info("Processing request", 
            request_id="abc-123", 
            collection="activity",
            start=0,
            rows=100)

# Log errors
logger.error("API error", 
              error="Timeout", 
              collection="transaction", 
              retry_count=3)
```

### Log Format

All logs are output in JSON format for easy parsing and analysis:

```json
{
  "timestamp": "2024-07-03T10:30:00.123456Z",
  "level": "INFO",
  "logger": "unhcr_iati_mcp.client",
  "event": "Querying activity",
  "request_id": "abc-123",
  "collection": "activity",
  "start": 0,
  "rows": 100
}
```

### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General operational information
- **WARNING**: Warning conditions
- **ERROR**: Error conditions
- **CRITICAL**: Critical errors requiring immediate attention

### Configuring Log Level

Set the `LOG_LEVEL` environment variable:

```bash
# In .env file
LOG_LEVEL="DEBUG"

# Or when running
LOG_LEVEL=DEBUG python -m unhcr_iati_mcp.server
```

### Log Context

All major operations include contextual information:

- **Request ID**: Unique identifier for tracking requests across services
- **Collection**: Which IATI collection is being queried
- **Operation**: Type of operation (query, export, etc.)
- **Parameters**: Query parameters and filters
- **Duration**: Execution time for operations
- **Result Count**: Number of records returned

## Prometheus Metrics

The server exposes Prometheus metrics for monitoring performance and health.

### Available Metrics

| Metric | Type | Description | Labels |
|--------|------|-------------|--------|
| `iati_datastore_requests_total` | Counter | Total API requests to IATI Datastore | `collection`, `status` |
| `iati_datastore_latency_seconds` | Histogram | Request latency in seconds | `collection` |
| `iati_datastore_errors_total` | Counter | Total errors from IATI Datastore | `collection`, `error_type` |
| `iati_mcp_tool_calls_total` | Counter | Total MCP tool calls | `tool_name`, `status` |
| `iati_mcp_tool_latency_seconds` | Histogram | MCP tool execution time | `tool_name` |
| `iati_code_table_loads_total` | Counter | Total code table loads | `table_name`, `status` |
| `iati_code_table_cache_size` | Gauge | Current size of code table cache | - |
| `iati_active_connections` | Gauge | Current number of active connections | - |
| `iati_cache_hits_total` | Counter | Total cache hits | `cache_type` |
| `iati_cache_misses_total` | Counter | Total cache misses | `cache_type` |

### Accessing Metrics

Use the `metrics` tool to retrieve Prometheus metrics:

```python
# Via MCP tool call
metrics = await client.call_tool("metrics", {})
print(metrics)
```

Or access the metrics endpoint directly if configured.

### Metric Buckets

Latency histograms use the following buckets (in seconds):
- 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, +Inf

## Health Checks

### Server Health

Check the overall health of the MCP server:

```python
# Via tool call
health = await client.call_tool("health_check", {})
print(health)
```

### System Status

Get detailed status of all system components:

```python
# Via tool call
status = await client.call_tool("system_status", {})
print(status)
```

### IATI Datastore Connection

Test the connection to the IATI Datastore API:

```python
# Via tool call
ping = await client.call_tool("datastore_ping", {})
print(ping)
```

### API Rate Limits

Check current API rate limit information:

```python
# Via tool call
limits = await client.call_tool("api_limits", {})
print(limits)
```

### Cache Statistics

Get cache performance statistics:

```python
# Via tool call
cache_stats = await client.call_tool("cache_stats", {})
print(cache_stats)
```

## Monitoring Dashboard

### Recommended Grafana Dashboard

Create a Grafana dashboard with the following panels:

1. **Request Rate**: `rate(iati_datastore_requests_total[5m])` by collection
2. **Error Rate**: `rate(iati_datastore_errors_total[5m])` by error_type
3. **Latency**: `histogram_quantile(0.95, iati_datastore_latency_seconds_bucket)` by collection
4. **Cache Hit Ratio**: `rate(iati_cache_hits_total[5m]) / (rate(iati_cache_hits_total[5m]) + rate(iati_cache_misses_total[5m]))`
5. **Active Connections**: `iati_active_connections`

### Alert Rules

Recommended alerting rules:

```yaml
# High error rate
- alert: HighIATIErrorRate
  expr: rate(iati_datastore_errors_total[5m]) > 0.1
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High IATI API error rate"

# High latency
- alert: HighIATILatency
  expr: histogram_quantile(0.95, iati_datastore_latency_seconds_bucket) > 10
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High IATI API latency"

# Connection issues
- alert: IATIConnectionIssues
  expr: increase(iati_datastore_errors_total{error_type="connection"}[5m]) > 5
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "IATI Datastore connection issues"
```

## Distributed Tracing (Future)

The architecture supports distributed tracing with OpenTelemetry. While not currently implemented, the following integration points are available:

- Request ID propagation through context
- Structured logging with trace IDs
- Metrics with trace context

## Performance Monitoring

### Key Performance Indicators

Track these KPIs for optimal performance:

1. **Request Latency**: Average and 95th percentile response times
2. **Error Rate**: Percentage of failed requests
3. **Cache Hit Ratio**: Efficiency of code table caching
4. **Connection Utilization**: Number of active connections vs. pool size

### Performance Tuning

Adjust these configuration parameters based on monitoring:

- `TIMEOUT_SECONDS`: Increase for slow responses (max 300)
- `PAGE_SIZE`: Adjust based on typical result sizes (default 1000)
- `MAX_CONNECTIONS`: Increase for higher throughput (max 100)

## Logging Best Practices

### For Development

```bash
# Enable debug logging
LOG_LEVEL=DEBUG python -m unhcr_iati_mcp.server
```

### For Production

```bash
# Use INFO level for production
LOG_LEVEL=INFO python -m unhcr_iati_mcp.server

# Or WARNING for minimal logs
LOG_LEVEL=WARNING python -m unhcr_iati_mcp.server
```

### Log Rotation

For long-running deployments, consider configuring log rotation:

```python
# In your deployment configuration
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'unhcr_iati_mcp.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
handler.setFormatter(logging.JSONFormatter())
logging.getLogger().addHandler(handler)
```
