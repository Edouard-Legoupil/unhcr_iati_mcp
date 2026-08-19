"""
HTTP Server for UNHCR IATI MCP Server.

Refactored to use FastMCP's built-in HTTP support and eliminate duplicate tool implementations.

This significantly reduces context overhead by:
- Using FastMCP's built-in MCP tool handling (no duplicate implementations)
- Importing unhcr_filter once at module level (not 9 times)
- Delegating tool calls to the MCP registry

Features:
- MCP JSON-RPC over HTTP (via FastMCP + custom dispatch)
- X-API-Key header support for HuggingChat compatibility
- Health check endpoint
- Protected Resource Metadata endpoint (RFC 9728)
"""

import json
import time
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from unhcr_iati_mcp import resources as _resources_module  # noqa: F401
from unhcr_iati_mcp import tools as _tools_module  # noqa: F401
from unhcr_iati_mcp.config import settings
from unhcr_iati_mcp.context import mcp, iati_client, unhcr_filter
from unhcr_iati_mcp.observability.logging import configure_logging, get_logger
from unhcr_iati_mcp.observability.metrics import configure_metrics


logger = get_logger(__name__)

# Get resource URL
RESOURCE_URL = settings.resource_url or f"http://{settings.host}:{settings.port}"

# Create FastAPI app
app = FastAPI(
    title="UNHCR IATI MCP Server",
    description="MCP Server for accessing UNHCR's IATI data via HTTP",
    version="0.0.1",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add exception handler for HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTPException and return proper JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=dict(exc.headers) if exc.headers else None,
    )

# Add CORS middleware for Copilot Studio compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "https://copilotstudio.microsoft.com",
        "https://*.copilotstudio.microsoft.com",
        "https://copilot.microsoft.com",
        "https://*.copilot.microsoft.com",
        "https://m365.cloud.microsoft",
        "https://*.m365.cloud.microsoft",
        "http://localhost:*",
        "http://127.0.0.1:*",
         "https://claude.ai",
        "https://*.claude.ai",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=[
        "Mcp-Session-Id",
        "mcp-session-id",
        "Content-Type",
        "Content-Length"
    ],
    max_age=86400,
)


# ============================================================================
# Health Check Endpoint
# ============================================================================

@app.get("/health")
async def health_check():
    """Enhanced health check with Streamable HTTP verification."""
    try:
        from unhcr_iati_mcp.context import mcp
        mcp_status = "healthy" if mcp else "uninitialized"
        
        # Check Streamable HTTP transport is available
        try:
            mcp_app = mcp.create_app()
            http_app = mcp_app.http_app(transport="streamable-http")
            transport_ok = http_app is not None
        except Exception:
            transport_ok = False
    except Exception:
        mcp_status = "error"
        transport_ok = False
    
    try:
        client_status = "healthy" if iati_client else "uninitialized"
    except Exception:
        client_status = "error"
    
    return {
        "status": "ok",
        "service": "unhcr-iati-mcp",
        "version": "0.0.1",
        "transport": "streamable-http",
        "streamable_http_ready": transport_ok,
        "auth_methods": ["x-api-key"],
        "components": {
            "mcp": mcp_status, 
            "iati_client": client_status,
            "streamable_http": "healthy" if transport_ok else "unhealthy"
        },
        "endpoints": {
            "mcp": "/mcp",
            "health": "/health",
            "schema": "/.well-known/mcp/schema"
        },
        "uptime": time.time(),
    }


# ============================================================================
# Prometheus Metrics Endpoint
# ============================================================================

@app.get("/metrics")
async def get_metrics():
    """
    Prometheus Metrics Endpoint.
    
    Exposes Prometheus-compatible metrics for scraping.
    This endpoint returns metrics in the standard Prometheus text format.
    """
    try:
        from unhcr_iati_mcp.observability.metrics import prometheus_metrics
        metrics_data = prometheus_metrics()
        return Response(
            content=metrics_data,
            media_type="text/plain",
            headers={"Content-Type": "text/plain; version=0.0.4; charset=utf-8"}
        )
    except Exception as e:
        logger.error(f"Error generating metrics: {e}")
        return Response(
            content=f"# Error generating metrics: {e}\n",
            media_type="text/plain",
            status_code=500
        )


# ============================================================================
# MCP Schema Endpoint for Copilot Studio Discovery
# ============================================================================

@app.get("/.well-known/mcp/schema")
async def mcp_schema():
    """
    MCP Schema endpoint for Copilot Studio discovery.
    
    This endpoint implements the MCP schema discovery protocol as specified in:
    https://github.com/modelcontextprotocol/specification/blob/main/protocol/mcp-schema.md
    
    Returns a JSON schema describing the MCP server capabilities.
    """
    try:
        tools = await mcp.list_tools()
        resources = await mcp.list_resources()
        
        # Generate MCP-specific schema following the MCP specification
        schema = {
            "name": settings.MCP_SERVER_NAME if hasattr(settings, 'MCP_SERVER_NAME') else "unhcr-iati-mcp",
            "version": settings.MCP_SERVER_VERSION if hasattr(settings, 'MCP_SERVER_VERSION') else "0.0.1",
            "description": "UNHCR Refugee Data Portal MCP Server - Provides access to UNHCR refugee statistics and indicators",
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {},
                "prompts": {}
            },
            "serverInfo": {
                "name": settings.MCP_SERVER_NAME if hasattr(settings, 'MCP_SERVER_NAME') else "unhcr-iati-mcp",
                "version": settings.MCP_SERVER_VERSION if hasattr(settings, 'MCP_SERVER_VERSION') else "0.0.1",
                "environment": settings.ENVIRONMENT if hasattr(settings, 'ENVIRONMENT') else "production",
                "baseUrl": settings.get_resource_url() if hasattr(settings, 'get_resource_url') else f"http://{settings.host}:{settings.port}"
            },
            "endpoints": {
                "mcp": "/mcp",
                "health": "/health",
                "info": "/info",
                "openapi": "/openapi.json",
                "schema": "/.well-known/mcp/schema"
            }
        }
        
        # Add tool capabilities
        for tool in tools:
            tool_schema = {
                "description": tool.description or "",
                "inputSchema": {}
            }
            
            # Extract input schema from tool parameters
            if hasattr(tool, 'parameters') and isinstance(tool.parameters, dict):
                tool_schema["inputSchema"] = tool.parameters
            
            schema["capabilities"]["tools"][tool.name] = tool_schema
        
        # Add resource capabilities
        for resource in resources:
            resource_schema = {
                "description": resource.description or "",
                "mimeType": resource.mime_type or "application/json"
            }
            schema["capabilities"]["resources"][resource.uri] = resource_schema
        
        return JSONResponse(
            content=schema,
            headers={
                "Content-Type": "application/json",
                "Cache-Control": "public, max-age=3600",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Max-Age": "86400"
            }
        )
    except Exception as e:
        logger.error(f"MCP schema generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# MCP JSON-RPC Endpoint
# ============================================================================

def get_api_client_from_state(request: Request):
    """Dependency to get API client from request state."""
    if not hasattr(request.state, "api_client"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API client not initialized")
    return request.state.api_client


@app.post("/mcp")
async def mcp_endpoint(request: Request, api_client: Any = Depends(get_api_client_from_state)):
    """MCP JSON-RPC Endpoint."""
    try:
        body = await request.json()
        
        if "jsonrpc" not in body:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
                "jsonrpc": "2.0", "id": None, "error": {
                    "code": -32600, "message": "Invalid Request", "data": "Missing jsonrpc field"}
            })
        
        if body["jsonrpc"] != "2.0":
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
                "jsonrpc": "2.0", "id": None, "error": {
                    "code": -32600, "message": "Invalid Request", "data": "Unsupported jsonrpc version"}
            })
        
        request_id = body.get("id")
        method = body.get("method")
        
        # Route to appropriate handler
        if method == "tools/list":
            result = await _list_tools()
            return JSONResponse(content={"jsonrpc": "2.0", "id": request_id, "result": result})
        
        elif method == "tools/call":
            params = body.get("params", {})
            name = params.get("name")
            arguments = params.get("arguments", {})
            
            if not name:
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
                    "jsonrpc": "2.0", "id": request_id, "error": {
                        "code": -32602, "message": "Invalid params", "data": "Missing tool name"}
                })
            
            result = await _call_tool(name, arguments, api_client)
            return JSONResponse(content={"jsonrpc": "2.0", "id": request_id, "result": result})
        
        elif method == "resources/list":
            result = await _list_resources()
            return JSONResponse(content={"jsonrpc": "2.0", "id": request_id, "result": result})
        
        elif method == "resources/read":
            params = body.get("params", {})
            uri = params.get("uri")
            
            if not uri:
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
                    "jsonrpc": "2.0", "id": request_id, "error": {
                        "code": -32602, "message": "Invalid params", "data": "Missing uri"}
                })
            
            result = await _read_resource(uri)
            return JSONResponse(content={"jsonrpc": "2.0", "id": request_id, "result": result})
        
        else:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
                "jsonrpc": "2.0", "id": request_id, "error": {
                    "code": -32601, "message": "Method not found", 
                    "data": f"Unknown method: {method}"}
            })
    
    except json.JSONDecodeError:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "jsonrpc": "2.0", "id": None, "error": {
                "code": -32700, "message": "Parse error", "data": "Invalid JSON"}
        })
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={
            "jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": e.detail}
        }, headers=dict(e.headers))
    except Exception as e:
        logger.exception("MCP endpoint error")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "jsonrpc": "2.0", "id": None, "error": {
                "code": -32603, "message": f"Internal error: {str(e)}"}
        })


# ============================================================================
# Helper Functions - Now using FastMCP registry (NO DUPLICATE HANDLERS!)
# ============================================================================

async def _list_tools() -> dict[str, Any]:
    """List all available MCP tools by querying FastMCP's registry."""
    try:
        tools_list = await mcp.list_tools()
        tools = []
        for tool in tools_list:
            tools.append({
                "name": tool.name,
                "description": tool.description or "",
                "inputSchema": tool.parameters or {},
            })
        return {"tools": tools}
    except Exception as e:
        logger.warning(f"Failed to get tools from mcp: {e}")
        return {"tools": []}


async def _call_tool(name: str, arguments: dict[str, Any], api_client: Any) -> dict[str, Any]:
    """
    Call a specific MCP tool by delegating to FastMCP's call_tool.
    
    This is the KEY IMPROVEMENT: Instead of having duplicate _handle_* functions,
    we simply call the tool via FastMCP's registry, which will invoke the
    @mcp.tool() decorated function from tools/activities.py, tools/transactions.py, etc.
    """
    try:
        # Call the tool via FastMCP's call_tool method
        # This automatically uses the registered @mcp.tool() implementation
        result = await mcp.call_tool(name, arguments)
        return {"content": [{"type": "text", "text": str(result)}]}
    except Exception as e:
        logger.warning(f"Failed to call tool {name}: {e}")
        return {
            "content": [{"type": "text", "text": f"Error calling tool {name}: {str(e)}"}],
            "isError": True,
        }


async def _list_resources() -> dict[str, Any]:
    """List all available MCP resources by querying FastMCP's registry."""
    try:
        resources_list = await mcp.list_resources()
        resources = []
        for resource in resources_list:
            uri_value = str(resource.uri)
            resources.append({
                "uri": uri_value,
                "name": resource.name or uri_value.split("://")[-1],
                "description": resource.description or "",
                "mimeType": resource.mime_type or "application/json",
            })
        return {"resources": resources}
    except Exception as e:
        logger.warning(f"Failed to get resources from mcp: {e}")
        return {"resources": []}


async def _read_resource(uri: str) -> dict[str, Any]:
    """Read a specific MCP resource by delegating to FastMCP's registry."""
    try:
        result = await mcp.read_resource(uri)
        return {"contents": [{"uri": uri, "mimeType": "application/json", "text": str(result)}]}
    except Exception as e:
        logger.warning(f"Failed to read resource {uri}: {e}")
        return {"contents": []}


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    configure_logging(
        level=settings.log_level,
        log_dir=settings.log_dir,
        log_file=settings.log_file
    )
    configure_metrics(
        metrics_dir=settings.metrics_dir,
        metrics_file=settings.metrics_file
    )
    logger.info("Starting UNHCR IATI MCP HTTP Server")
    logger.info(f"Host: {settings.host}, Port: {settings.port}")
    logger.info("Metrics endpoint available at /metrics")
    uvicorn.run(app, host=settings.host, port=settings.port, log_level=settings.log_level.lower())
