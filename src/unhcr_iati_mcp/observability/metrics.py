"""
Prometheus metrics for UNHCR IATI MCP Server.

This module provides Prometheus metrics for monitoring server health,
performance, and error rates.
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Request counters
datastore_requests = Counter(
    'iati_datastore_requests_total',
    'Total number of IATI Datastore requests',
    ['collection', 'status']
)

datastore_errors = Counter(
    'iati_datastore_errors_total',
    'Total number of IATI Datastore errors',
    ['collection', 'error_type']
)

# Latency tracking
datastore_latency = Histogram(
    'iati_datastore_latency_seconds',
    'Latency of IATI Datastore requests in seconds',
    ['collection'],
    buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60, 120]
)

# Active requests gauge (use Gauge for values that can go up and down)
active_requests = Gauge(
    'iati_active_requests',
    'Number of active requests',
    ['collection']
)


def monitor_datastore(collection: str):
    """
    Called when a datastore request starts.
    
    Args:
        collection: The collection being queried
    """
    datastore_requests.labels(collection=collection, status='started').inc()
    active_requests.labels(collection=collection).inc()


def complete_datastore(collection: str, status: str = 'success'):
    """
    Called when a datastore request completes.
    
    Args:
        collection: The collection that was queried
        status: The completion status (success, timeout, error, etc.)
    """
    datastore_requests.labels(collection=collection, status=status).inc()
    active_requests.labels(collection=collection).dec()


def datastore_error(collection: str, error_type: str):
    """
    Called when a datastore request fails.
    
    Args:
        collection: The collection that was queried
        error_type: The type of error that occurred
    """
    datastore_errors.labels(collection=collection, error_type=error_type).inc()


def prometheus_metrics() -> bytes:
    """
    Generate Prometheus metrics in the standard format.
    
    Returns:
        Bytes containing Prometheus-formatted metrics
    """
    return generate_latest()
