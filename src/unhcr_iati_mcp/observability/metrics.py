"""
Prometheus metrics for UNHCR IATI MCP Server.

This module provides Prometheus metrics for monitoring server health,
performance, and error rates.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

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

# Metrics file path
_metrics_file: Optional[Path] = None


def configure_metrics(metrics_dir: Optional[str] = None, metrics_file: Optional[str] = None) -> None:
    """
    Configure metrics file export.
    
    Args:
        metrics_dir: Directory to save metrics files. If None, uses settings.metrics_dir or 'metrics'
        metrics_file: Metrics file path. If None, uses settings.metrics_file or defaults
    """
    global _metrics_file
    
    # Import settings but handle circular imports
    try:
        from unhcr_iati_mcp.config import settings
        if metrics_dir is None:
            metrics_dir = settings.metrics_dir
        if metrics_file is None:
            metrics_file = settings.metrics_file
    except ImportError:
        pass
    
    if metrics_dir is None:
        metrics_dir = Path("metrics")
    else:
        metrics_dir = Path(metrics_dir)
    
    metrics_dir.mkdir(parents=True, exist_ok=True)
    
    if metrics_file is None:
        _metrics_file = metrics_dir / "prometheus_metrics.txt"
    else:
        _metrics_file = Path(metrics_file)
    
    # Log configuration
    from unhcr_iati_mcp.observability.logging import get_logger
    logger = get_logger(__name__)
    logger.info(
        "Metrics configured",
        metrics_file=str(_metrics_file)
    )
    
    # Generate and save initial metrics
    try:
        save_metrics_to_file()
    except Exception:
        pass  # Don't fail if we can't save metrics initially


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
    metrics_data = generate_latest()
    
    # Save to file if configured
    if _metrics_file is not None:
        try:
            _metrics_file.write_bytes(metrics_data)
        except Exception:
            pass  # Don't fail if we can't write to file
    
    return metrics_data


def save_metrics_to_file(metrics_data: Optional[bytes] = None) -> None:
    """
    Save metrics to the configured file.
    
    Args:
        metrics_data: Optional metrics data to save. If None, generates current metrics.
    """
    if _metrics_file is None:
        return
    
    if metrics_data is None:
        metrics_data = prometheus_metrics()
    
    try:
        _metrics_file.write_bytes(metrics_data)
    except Exception:
        pass  # Don't fail if we can't write to file
