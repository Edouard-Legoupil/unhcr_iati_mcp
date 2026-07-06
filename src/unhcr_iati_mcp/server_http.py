"""
HTTP Server for UNHCR IATI MCP Server.

Refactored to use FastMCP's built-in HTTP support and eliminate duplicate tool implementations.

This significantly reduces context overhead by:
- Using FastMCP's built-in MCP tool handling (no duplicate implementations)
- Importing unhcr_filter once at module level (not 9 times)
- Delegating tool calls to the MCP registry

Features:
- MCP JSON-RPC over HTTP (via FastMCP + custom dispatch)
- OAuth 2.1 authentication with built-in server
- X-API-Key header support for HuggingChat compatibility
- Health check endpoint
- Protected Resource Metadata endpoint (RFC 9728)
- Dual authentication support
"""

import json
import time
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from unhcr_iati_mcp.auth.middleware import AuthMiddleware
from unhcr_iati_mcp.auth.oauth import OAuthServer
from unhcr_iati_mcp.config import settings
from unhcr_iati_mcp.context import mcp, iati_client, unhcr_filter
from unhcr_iati_mcp.observability.logging import configure_logging, get_logger
from unhcr_iati_mcp.observability.metrics import configure_metrics


logger = get_logger(__name__)

# Initialize OAuth server (if enabled)
oauth_server: OAuthServer | None = None
if settings.use_builtin_oauth:
    oauth_server = OAuthServer()
    logger.info("OAuth 2.1 server initialized")

# Initialize auth middleware
auth_middleware = AuthMiddleware(oauth_server)

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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add auth middleware
app.middleware("http")(auth_middleware)


# ============================================================================
# OAuth 2.1 Endpoints
# ============================================================================

@app.get("/.well-known/oauth-authorization-server")
async def oauth_authorization_server_metadata():
    """
    OAuth 2.1 Authorization Server Metadata (RFC 8414).
    """
    if oauth_server:
        return oauth_server.get_metadata()
    
    return {
        "issuer": RESOURCE_URL,
        "token_endpoint": f"{RESOURCE_URL}/oauth/token",
        "jwks_uri": f"{RESOURCE_URL}/.well-known/jwks.json",
        "response_types_supported": ["token"],
        "grant_types_supported": ["client_credentials"],
    }


@app.get("/.well-known/jwks.json")
async def jwks():
    """JSON Web Key Set (JWKS) endpoint."""
    if oauth_server:
        return oauth_server.get_jwks()
    return {"keys": []}


@app.get("/.well-known/oauth-protected-resource")
async def oauth_protected_resource_metadata():
    """OAuth Protected Resource Metadata (RFC 9728)."""
    auth_servers = []
    if settings.use_builtin_oauth:
        auth_servers = [RESOURCE_URL]
    elif settings.auth_server_url:
        auth_servers = [settings.auth_server_url]
    return {"resource": RESOURCE_URL, "authorization_servers": auth_servers}


@app.post("/oauth/token")
async def token_endpoint(request: Request):
    """OAuth 2.1 Token Endpoint (Client Credentials Grant)."""
    if not oauth_server:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OAuth server not configured",
        )
    
    form_data = await request.form()
    grant_type = form_data.get("grant_type")
    client_id = form_data.get("client_id", settings.oauth_client_id)
    client_secret = form_data.get("client_secret")
    
    if grant_type != "client_credentials":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "unsupported_grant_type", 
                    "error_description": "Only client_credentials grant type is supported"},
        )
    
    if not client_secret:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "invalid_request",
                    "error_description": "client_secret (IATI API key) is required"},
        )
    
    if not oauth_server.validate_client(client_id, client_secret):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "invalid_client",
                    "error_description": "Invalid client credentials - check your IATI API key"},
        )
    
    token = oauth_server.issue_token(
        client_id=client_id,
        client_secret=client_secret,
        expiry=settings.oauth_token_expiry,
    )
    return token.to_dict()


@app.get("/oauth/info")
async def oauth_info():
    """OAuth Information Endpoint."""
    resource_url = RESOURCE_URL
    return {
        "message": "Built-in OAuth Server - No registration required",
        "auth_methods": [
            {
                "name": "OAuth 2.1 (Recommended)",
                "description": "For Claude, OpenAI, and OAuth-compliant clients",
                "instructions": {
                    "client_id": oauth_server.get_fixed_client_id() if oauth_server else "default",
                    "client_secret": "Your IATI API key from https://developer.iatistandard.org/",
                    "token_endpoint": f"{resource_url}/oauth/token",
                    "grant_type": "client_credentials",
                },
                "example": f"curl -X POST {resource_url}/oauth/token -d \"grant_type=client_credentials&client_id=default&client_secret=YOUR_IATI_API_KEY\"",
            },
            {
                "name": "X-API-Key Header",
                "description": "For HuggingChat and clients without OAuth support",
                "instructions": {
                    "header_name": "X-API-Key",
                    "header_value": "Your IATI API key from https://developer.iatistandard.org/",
                },
                "example": f'curl -X POST {resource_url}/mcp -H "X-API-Key: YOUR_IATI_API_KEY" -H "Content-Type: application/json" -d \'{{"jsonrpc":"2.0","id":1,"method":"tools/list"}}\'',
            },
        ],
    }


# ============================================================================
# Health Check Endpoint
# ============================================================================

@app.get("/health")
async def health_check():
    """Health Check Endpoint."""
    try:
        from unhcr_iati_mcp.context import mcp
        mcp_status = "healthy" if mcp else "uninitialized"
    except Exception:
        mcp_status = "error"
    
    try:
        client_status = "healthy" if iati_client else "uninitialized"
    except Exception:
        client_status = "error"
    
    return {
        "status": "ok",
        "service": "unhcr-iati-mcp",
        "version": "0.0.1",
        "transport": "http",
        "oauth": "built-in" if settings.use_builtin_oauth else "disabled",
        "auth_methods": ["oauth", "x-api-key"] if settings.use_builtin_oauth else ["x-api-key"],
        "components": {"mcp": mcp_status, "iati_client": client_status},
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
    """List all available MCP resources."""
    resources = [
        {"uri": "unhcr://donors", "name": "UNHCR Donors", 
         "description": "Donor code to name mapping", "mimeType": "application/json"},
        {"uri": "unhcr://countries", "name": "UNHCR Countries", 
         "description": "Country reference data", "mimeType": "application/json"},
        {"uri": "unhcr://sectors", "name": "UNHCR Sectors", 
         "description": "Sector code to name mapping", "mimeType": "application/json"},
        {"uri": "unhcr://sdgs", "name": "UNHCR SDGs", 
         "description": "Sustainable Development Goals mapping", "mimeType": "application/json"},
        {"uri": "unhcr://glossary", "name": "IATI Glossary", 
         "description": "IATI terminology glossary", "mimeType": "application/json"},
        {"uri": "unhcr://portfolio", "name": "UNHCR Portfolio", 
         "description": "UNHCR portfolio metadata", "mimeType": "application/json"},
        {"uri": "unhcr://schemas/activity", "name": "Activity Schema", 
         "description": "IATI activity schema definition", "mimeType": "application/json"},
        {"uri": "unhcr://schemas/transaction", "name": "Transaction Schema", 
         "description": "IATI transaction schema definition", "mimeType": "application/json"},
        {"uri": "unhcr://schemas/budget", "name": "Budget Schema", 
         "description": "IATI budget schema definition", "mimeType": "application/json"},
    ]
    return {"resources": resources}


async def _read_resource(uri: str) -> dict[str, Any]:
    """Read a specific MCP resource."""
    resource_data = {
        "unhcr://donors": {"DEU": "Germany", "USA": "United States", "GBR": "United Kingdom"},
        "unhcr://countries": {"AF": "Afghanistan", "SYR": "Syria", "KE": "Kenya"},
        "unhcr://sectors": {"12220": "Basic health care", "12181": "Health education"},
        "unhcr://sdgs": {"1": {"name": "No Poverty"}, "3": {"name": "Good Health and Well-being"}},
        "unhcr://glossary": {"activity": "IATI project/programme"},
        "unhcr://portfolio": {"publisher": "XM-DAC-41121", "organisation": "UNHCR"},
        "unhcr://schemas/activity": {"iati_identifier": "string", "title_narrative": "string[]"},
        "unhcr://schemas/transaction": {"transaction_value": "float[]"},
        "unhcr://schemas/budget": {"budget_value": "float[]"},
    }
    data = resource_data.get(uri, {})
    return {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(data)}]}


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
    logger.info(f"OAuth: {'enabled' if settings.use_builtin_oauth else 'disabled'}")
    logger.info("Metrics endpoint available at /metrics")
    uvicorn.run(app, host=settings.host, port=settings.port, log_level=settings.log_level.lower())
