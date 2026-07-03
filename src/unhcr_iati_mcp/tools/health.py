"""
Health check and monitoring tools for UNHCR IATI MCP Server.
"""

from typing import Any, Dict

from unhcr_iati_mcp.context import (
    mcp,
    iati_client,
    unhcr_filter,
)


@mcp.tool(
    name="metrics",
    description="Get Prometheus metrics for the server."
)
async def metrics() -> Dict[str, str]:
    """
    Retrieve Prometheus metrics from the server.
    
    Returns:
        Dictionary containing Prometheus metrics
    """
    # Import here to avoid circular imports
    from unhcr_iati_mcp.observability.metrics import prometheus_metrics
    
    return {
        "prometheus": prometheus_metrics().decode("utf-8")
    }


@mcp.tool(
    name="health_check",
    description="Check the health status of the server."
)
async def health_check() -> Dict[str, str]:
    """
    Perform a health check on the server.
    
    Returns:
        Dictionary containing health status information
    """
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
    """
    Check the status of system components.
    
    Returns:
        Dictionary containing status of each component
    """
    return {
        "api": "up",
        "version": "1.0.0"
    }


@mcp.tool(
    name="datastore_ping",
    description="Test connection to IATI Datastore."
)
async def datastore_ping() -> Dict[str, Any]:
    """
    Test the connection to the IATI Datastore API.
    
    Returns:
        Dictionary containing connection status
    """
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
    except Exception as e:
        return {
            "status": "down",
            "service": "Datastore",
            "message": str(e),
        }


@mcp.tool(
    name="api_limits",
    description="Get API rate limit information."
)
async def api_limits() -> Dict[str, Any]:
    """
    Get rate limit information for the IATI Datastore API.
    
    Note: IATI Datastore doesn't provide rate limit headers in its API.
    This is a placeholder for future implementation.
    
    Returns:
        Dictionary containing rate limit information
    """
    return {
        "rate_limit": "unknown",
        "remaining_requests": "unknown",
        "reset_time": "unknown"
    }
