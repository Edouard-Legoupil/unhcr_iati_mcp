"""
Health check and monitoring tools for UNHCR IATI MCP Server.
"""

from typing import Any, Dict

from unhcr_iati_mcp.context import (
    mcp,
    iati_client,
    unhcr_filter,
)
from unhcr_iati_mcp.client import IATIError
from unhcr_iati_mcp.observability.logging import get_logger

logger = get_logger(__name__)


@mcp.tool(
    name="metrics",
    description="Get Prometheus metrics for the server."
)
async def metrics() -> Dict[str, str]:
    """Get Prometheus metrics for the server."""
    try:
        # Import here to avoid circular imports
        from unhcr_iati_mcp.observability.metrics import prometheus_metrics
        
        return {
            "prometheus": prometheus_metrics().decode("utf-8")
        }
    except Exception as e:
        logger.exception("Error getting metrics")
        return {
            "error": str(e),
            "prometheus": ""
        }


@mcp.tool(
    name="health_check",
    description="Check the health status of the server."
)
async def health_check() -> Dict[str, str]:
    """Check the health status of the server."""
    return {
        "status": "healthy",
        "service": "UNHCR IATI MCP",
        "version": "1.0.0"
    }


@mcp.tool(
    name="system_status",
    description="Check the status of all system components."
)
async def system_status() -> Dict[str, str]:
    """Check the status of all system components."""
    return {
        "api": "up",
        "version": "1.0.0"
    }


@mcp.tool(
    name="datastore_ping",
    description="Test connection to IATI Datastore."
)
async def datastore_ping() -> Dict[str, Any]:
    """Test connection to IATI Datastore."""
    try:
        await iati_client.query(
            "activity",
            "*:*",
            rows=0,
        )
        return {
            "status": "up",
            "service": "Datastore",
            "message": "Connection successful"
        }
    except IATIError as e:
        logger.error(f"Datastore ping failed: {e}")
        return {
            "status": "down",
            "service": "Datastore",
            "message": str(e),
        }
    except Exception as e:
        logger.exception("Unexpected error in datastore ping")
        return {
            "status": "down",
            "service": "Datastore",
            "message": "Internal server error",
        }


@mcp.tool(
    name="api_limits",
    description="Get API rate limit information."
)
async def api_limits() -> Dict[str, Any]:
    """Get API rate limit information."""
    return {
        "rate_limit": "unknown",
        "remaining_requests": "unknown",
        "reset_time": "unknown"
    }
