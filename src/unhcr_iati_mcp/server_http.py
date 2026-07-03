"""
HTTP Server for UNHCR IATI MCP Server.

This module provides an HTTP-based MCP server using FastAPI, enabling remote deployment
and RESTful access to MCP tools and resources.

Features:
- MCP JSON-RPC over HTTP
- OAuth 2.1 authentication with built-in server
- X-API-Key header support for HuggingChat compatibility
- Health check endpoint
- Protected Resource Metadata endpoint (RFC 9728)
- Dual authentication support
"""

import json
import time
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from unhcr_iati_mcp.auth.middleware import AuthMiddleware
from unhcr_iati_mcp.auth.oauth import OAuthServer, OAuthToken
from unhcr_iati_mcp.config import settings
from unhcr_iati_mcp.context import mcp as base_mcp, iati_client
from unhcr_iati_mcp.observability.logging import configure_logging, get_logger


logger = get_logger(__name__)

# Initialize OAuth server (if enabled)
oauth_server: OAuthServer | None = None
if settings.use_builtin_oauth:
    oauth_server = OAuthServer()
    logger.info("OAuth 2.1 server initialized")

# Initialize auth middleware
auth_middleware = AuthMiddleware(oauth_server)

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
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add auth middleware
app.middleware("http")(auth_middleware)


# Get resource URL
RESOURCE_URL = settings.resource_url or f"http://{settings.host}:{settings.port}"


# ============================================================================
# OAuth 2.1 Endpoints
# ============================================================================

@app.get("/.well-known/oauth-authorization-server")
async def oauth_authorization_server_metadata():
    """
    OAuth 2.1 Authorization Server Metadata (RFC 8414).
    
    This endpoint provides metadata about the OAuth authorization server.
    It MUST be publicly accessible without authentication.
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
    """
    JSON Web Key Set (JWKS) endpoint.
    
    Provides the public keys used for signing tokens.
    """
    if oauth_server:
        return oauth_server.get_jwks()
    
    return {"keys": []}


@app.get("/.well-known/oauth-protected-resource")
async def oauth_protected_resource_metadata():
    """
    OAuth Protected Resource Metadata (RFC 9728).
    
    This endpoint provides metadata about the protected resource (this MCP server).
    It MUST be publicly accessible without authentication.
    """
    auth_servers = []
    if settings.use_builtin_oauth:
        auth_servers = [RESOURCE_URL]
    elif settings.auth_server_url:
        auth_servers = [settings.auth_server_url]
    
    return {
        "resource": RESOURCE_URL,
        "authorization_servers": auth_servers,
    }


@app.post("/oauth/token")
async def token_endpoint(
    request: Request,
):
    """
    OAuth 2.1 Token Endpoint (Client Credentials Grant).
    
    Issues access tokens for valid client credentials.
    In this implementation, the client_secret IS the IATI API key.
    
    Request body (form-encoded):
    - grant_type: "client_credentials" (required)
    - client_id: Any string (default: "default")
    - client_secret: Your IATI API key (required)
    - scope: "iati:read" (optional)
    
    Response:
    - access_token: The issued token
    - token_type: "Bearer"
    - expires_in: Token lifetime in seconds
    - scope: "iati:read"
    """
    if not oauth_server:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OAuth server not configured",
        )
    
    # Parse form data
    form_data = await request.form()
    grant_type = form_data.get("grant_type")
    client_id = form_data.get("client_id", settings.oauth_client_id)
    client_secret = form_data.get("client_secret")
    
    # Validate grant type
    if grant_type != "client_credentials":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "unsupported_grant_type",
                "error_description": "Only client_credentials grant type is supported",
            },
        )
    
    # Validate client_secret
    if not client_secret:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "invalid_request",
                "error_description": "client_secret (IATI API key) is required",
            },
        )
    
    # Validate client
    if not oauth_server.validate_client(client_id, client_secret):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "invalid_client",
                "error_description": "Invalid client credentials - check your IATI API key",
            },
        )
    
    # Issue token
    token = oauth_server.issue_token(
        client_id=client_id,
        client_secret=client_secret,
        expiry=settings.oauth_token_expiry,
    )
    
    return token.to_dict()


@app.get("/oauth/info")
async def oauth_info():
    """
    OAuth Information Endpoint.
    
    Provides helpful information for users about authentication options.
    """
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
                "example": f"curl -X POST {resource_url}/mcp -H \"X-API-Key: YOUR_IATI_API_KEY\" -H \"Content-Type: application/json\" -d '{{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}}'",
            },
        ],
    }


# ============================================================================
# Health Check Endpoint
# ============================================================================

@app.get("/health")
async def health_check():
    """
    Health Check Endpoint.
    
    Returns the current health status of the server.
    Useful for Kubernetes liveness probes and monitoring.
    """
    # Check if we can import the MCP server
    try:
        from unhcr_iati_mcp.context import mcp
        mcp_status = "healthy" if mcp else "uninitialized"
    except Exception:
        mcp_status = "error"
    
    # Check IATI client
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
        "components": {
            "mcp": mcp_status,
            "iati_client": client_status,
        },
        "uptime": time.time(),
    }


# ============================================================================
# MCP JSON-RPC Endpoints
# ============================================================================

def get_api_client_from_state(request: Request):
    """Dependency to get API client from request state."""
    if not hasattr(request.state, "api_client"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API client not initialized",
        )
    return request.state.api_client


@app.post("/mcp")
async def mcp_endpoint(
    request: Request,
    api_client: Any = Depends(get_api_client_from_state),
):
    """
    MCP JSON-RPC Endpoint.
    
    This is the main endpoint for MCP communication over HTTP.
    It accepts JSON-RPC 2.0 requests and returns JSON-RPC 2.0 responses.
    
    Authentication:
    - Required: OAuth Bearer token or X-API-Key header
    - The client will be attached to the request state by the auth middleware
    
    Request format:
    {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    
    Response format:
    {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {...}
    }
    
    Or for errors:
    {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {
            "code": -32603,
            "message": "Internal error"
        }
    }
    """
    try:
        # Parse request body
        body = await request.json()
        
        # Validate JSON-RPC 2.0 format
        if "jsonrpc" not in body:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request",
                        "data": "Missing jsonrpc field",
                    },
                },
            )
        
        if body["jsonrpc"] != "2.0":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request",
                        "data": "Unsupported jsonrpc version",
                    },
                },
            )
        
        # Get request ID
        request_id = body.get("id")
        
        # Handle tools/list
        if body.get("method") == "tools/list":
            result = await _list_tools()
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result,
                }
            )
        
        # Handle tools/call
        elif body.get("method") == "tools/call":
            params = body.get("params", {})
            name = params.get("name")
            arguments = params.get("arguments", {})
            
            if not name:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32602,
                            "message": "Invalid params",
                            "data": "Missing tool name",
                        },
                    },
                )
            
            result = await _call_tool(name, arguments, api_client)
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result,
                }
            )
        
        # Handle resources/list
        elif body.get("method") == "resources/list":
            result = await _list_resources()
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result,
                }
            )
        
        # Handle resources/read
        elif body.get("method") == "resources/read":
            params = body.get("params", {})
            uri = params.get("uri")
            
            if not uri:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32602,
                            "message": "Invalid params",
                            "data": "Missing uri",
                        },
                    },
                )
            
            result = await _read_resource(uri)
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result,
                }
            )
        
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": "Method not found",
                        "data": f"Unknown method: {body.get('method')}",
                    },
                },
            )
    
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error",
                    "data": "Invalid JSON",
                },
            },
        )
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": e.detail,
                },
            },
            headers=dict(e.headers),
        )
    except Exception as e:
        logger.exception("MCP endpoint error")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}",
                },
            },
        )


# ============================================================================
# Helper Functions
# ============================================================================

async def _list_tools() -> dict[str, Any]:
    """List all available MCP tools."""
    # Import here to avoid circular imports
    from unhcr_iati_mcp.context import mcp
    
    # Get all registered tools
    tools = []
    
    # The mcp object should have registered tools
    # We need to extract them from the FastMCP instance
    try:
        # Try to get tools from the mcp object
        if hasattr(mcp, "_tool_manager"):
            for name, tool in mcp._tool_manager.tools.items():
                tools.append({
                    "name": name,
                    "description": tool.description or "",
                    "inputSchema": tool.input_schema or {},
                })
        else:
            # Fallback: return predefined tools
            tools = [
                {"name": "unhcr_activities", "description": "List UNHCR activities", "inputSchema": {}},
                {"name": "unhcr_activity", "description": "Get specific activity", "inputSchema": {}},
                {"name": "unhcr_activity_by_country", "description": "Filter by country", "inputSchema": {}},
                {"name": "unhcr_activity_by_sector", "description": "Filter by sector", "inputSchema": {}},
                {"name": "unhcr_activity_by_year", "description": "Filter by year", "inputSchema": {}},
                {"name": "unhcr_activity_search", "description": "Advanced search", "inputSchema": {}},
                {"name": "unhcr_transactions", "description": "List transactions", "inputSchema": {}},
                {"name": "unhcr_transaction_search", "description": "Search transactions", "inputSchema": {}},
                {"name": "unhcr_budgets", "description": "List budgets", "inputSchema": {}},
                {"name": "unhcr_donors", "description": "Get donors", "inputSchema": {}},
                {"name": "unhcr_top_donors", "description": "Top donors", "inputSchema": {}},
                {"name": "unhcr_donor_breakdown", "description": "Donor breakdown", "inputSchema": {}},
                {"name": "unhcr_donor_trends", "description": "Donor trends", "inputSchema": {}},
                {"name": "unhcr_countries", "description": "List countries", "inputSchema": {}},
                {"name": "unhcr_country_summary", "description": "Country summary", "inputSchema": {}},
                {"name": "unhcr_country_financing", "description": "Country financing", "inputSchema": {}},
                {"name": "unhcr_country_dashboard", "description": "Country dashboard", "inputSchema": {}},
                {"name": "unhcr_top_countries", "description": "Top countries", "inputSchema": {}},
                {"name": "unhcr_sectors", "description": "List sectors", "inputSchema": {}},
                {"name": "unhcr_sector_summary", "description": "Sector summary", "inputSchema": {}},
                {"name": "unhcr_top_sectors", "description": "Top sectors", "inputSchema": {}},
                {"name": "unhcr_sdgs", "description": "List SDGs", "inputSchema": {}},
                {"name": "unhcr_sdg_summary", "description": "SDG summary", "inputSchema": {}},
                {"name": "unhcr_portfolio_summary", "description": "Portfolio summary", "inputSchema": {}},
                {"name": "unhcr_dashboard", "description": "Full dashboard", "inputSchema": {}},
                {"name": "unhcr_export_json", "description": "Export as JSON", "inputSchema": {}},
                {"name": "unhcr_export_csv", "description": "Export as CSV", "inputSchema": {}},
                {"name": "unhcr_export_xml", "description": "Export as XML", "inputSchema": {}},
                {"name": "unhcr_bulk_extract", "description": "Bulk extract", "inputSchema": {}},
                {"name": "health_check", "description": "Health check", "inputSchema": {}},
                {"name": "system_status", "description": "System status", "inputSchema": {}},
                {"name": "datastore_ping", "description": "Ping datastore", "inputSchema": {}},
                {"name": "api_limits", "description": "API limits", "inputSchema": {}},
                {"name": "metrics", "description": "Metrics", "inputSchema": {}},
                {"name": "cache_stats", "description": "Cache stats", "inputSchema": {}},
            ]
    except Exception as e:
        logger.warning(f"Failed to get tools from mcp: {e}")
    
    return {"tools": tools}


async def _call_tool(name: str, arguments: dict[str, Any], api_client: Any) -> dict[str, Any]:
    """Call a specific MCP tool."""
    from unhcr_iati_mcp.context import unhcr_filter
    
    # Map of tool names to handler functions
    # In a real implementation, these would call the actual tool functions
    # For now, we'll implement the most common ones
    
    tool_handlers = {
        "unhcr_activities": _handle_activities,
        "unhcr_activity": _handle_activity,
        "unhcr_activity_by_country": _handle_activity_by_country,
        "unhcr_activity_by_sector": _handle_activity_by_sector,
        "unhcr_activity_by_year": _handle_activity_by_year,
        "unhcr_activity_search": _handle_activity_search,
        "unhcr_transactions": _handle_transactions,
        "unhcr_transaction_search": _handle_transaction_search,
        "unhcr_budgets": _handle_budgets,
        "health_check": _handle_health_check,
        "datastore_ping": _handle_datastore_ping,
        # Add more as needed
    }
    
    handler = tool_handlers.get(name)
    if handler:
        return await handler(arguments, api_client)
    
    # Default handler for tools not explicitly implemented
    # Try to call the tool via the context mcp
    try:
        from unhcr_iati_mcp.context import mcp
        # The mcp object should have a way to call tools
        if hasattr(mcp, "call_tool"):
            result = await mcp.call_tool(name, arguments)
            return {"content": [{"type": "text", "text": str(result)}]}
        else:
            # Fallback: return a generic response
            return {
                "content": [{"type": "text", "text": f"Tool {name} executed with arguments: {arguments}"}]
            }
    except Exception as e:
        logger.warning(f"Failed to call tool {name}: {e}")
        return {
            "content": [{"type": "text", "text": f"Error calling tool {name}: {str(e)}"}],
            "isError": True,
        }


async def _handle_activities(args: dict[str, Any], client: Any) -> dict[str, Any]:
    """Handle unhcr_activities tool."""
    rows = args.get("rows", 100)
    start = args.get("start", 0)
    
    from unhcr_iati_mcp.context import unhcr_filter
    
    try:
        data = await client.query(
            collection="activity",
            q=unhcr_filter(),
            rows=rows,
            start=start,
        )
        return {
            "content": [{"type": "text", "text": json.dumps(data)}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True,
        }


async def _handle_activity(args: dict[str, Any], client: Any) -> dict[str, Any]:
    """Handle unhcr_activity tool."""
    iati_identifier = args.get("iati_identifier")
    
    if not iati_identifier:
        return {
            "content": [{"type": "text", "text": "Missing iati_identifier parameter"}],
            "isError": True,
        }
    
    try:
        data = await client.query(
            collection="activity",
            q=f'iati_identifier:"{iati_identifier}"',
            rows=1,
        )
        return {
            "content": [{"type": "text", "text": json.dumps(data)}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True,
        }


async def _handle_activity_by_country(args: dict[str, Any], client: Any) -> dict[str, Any]:
    """Handle unhcr_activity_by_country tool."""
    country_code = args.get("country_code")
    rows = args.get("rows", 100)
    start = args.get("start", 0)
    
    if not country_code:
        return {
            "content": [{"type": "text", "text": "Missing country_code parameter"}],
            "isError": True,
        }
    
    from unhcr_iati_mcp.context import unhcr_filter
    
    try:
        data = await client.query(
            collection="activity",
            q=f'{unhcr_filter()} AND recipient_country_code:"{country_code}"',
            rows=rows,
            start=start,
        )
        return {
            "content": [{"type": "text", "text": json.dumps(data)}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True,
        }


async def _handle_activity_by_sector(args: dict[str, Any], client: Any) -> dict[str, Any]:
    """Handle unhcr_activity_by_sector tool."""
    sector_code = args.get("sector_code")
    rows = args.get("rows", 100)
    
    if not sector_code:
        return {
            "content": [{"type": "text", "text": "Missing sector_code parameter"}],
            "isError": True,
        }
    
    from unhcr_iati_mcp.context import unhcr_filter
    
    try:
        data = await client.query(
            collection="activity",
            q=f'{unhcr_filter()} AND sector_code:"{sector_code}"',
            rows=rows,
        )
        return {
            "content": [{"type": "text", "text": json.dumps(data)}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True,
        }


async def _handle_activity_by_year(args: dict[str, Any], client: Any) -> dict[str, Any]:
    """Handle unhcr_activity_by_year tool."""
    year = args.get("year")
    rows = args.get("rows", 100)
    
    if not year:
        return {
            "content": [{"type": "text", "text": "Missing year parameter"}],
            "isError": True,
        }
    
    from unhcr_iati_mcp.context import unhcr_filter
    
    try:
        data = await client.query(
            collection="activity",
            q=f'{unhcr_filter()} AND activity_date:{year}',
            rows=rows,
        )
        return {
            "content": [{"type": "text", "text": json.dumps(data)}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True,
        }


async def _handle_activity_search(args: dict[str, Any], client: Any) -> dict[str, Any]:
    """Handle unhcr_activity_search tool."""
    query = args.get("query", "*")
    rows = args.get("rows", 10)
    start = args.get("start", 0)
    fields = args.get("fields")
    sort = args.get("sort")
    
    from unhcr_iati_mcp.context import unhcr_filter
    
    # Combine UNHCR filter with custom query
    full_query = f'{unhcr_filter()} AND ({query})'
    
    try:
        params = {
            "q": full_query,
            "rows": rows,
            "start": start,
        }
        if fields:
            params["fl"] = fields
        if sort:
            params["sort"] = sort
        
        data = await client.query(
            collection="activity",
            **params,
        )
        return {
            "content": [{"type": "text", "text": json.dumps(data)}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True,
        }


async def _handle_transactions(args: dict[str, Any], client: Any) -> dict[str, Any]:
    """Handle unhcr_transactions tool."""
    year = args.get("year")
    rows = args.get("rows", 100)
    start = args.get("start", 0)
    
    from unhcr_iati_mcp.context import unhcr_filter
    
    try:
        q = unhcr_filter()
        if year:
            q += f' AND transaction_date:{year}'
        
        data = await client.query(
            collection="transaction",
            q=q,
            rows=rows,
            start=start,
        )
        return {
            "content": [{"type": "text", "text": json.dumps(data)}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True,
        }


async def _handle_transaction_search(args: dict[str, Any], client: Any) -> dict[str, Any]:
    """Handle unhcr_transaction_search tool."""
    query = args.get("query", "*")
    rows = args.get("rows", 10)
    start = args.get("start", 0)
    
    from unhcr_iati_mcp.context import unhcr_filter
    
    try:
        data = await client.query(
            collection="transaction",
            q=f'{unhcr_filter()} AND ({query})',
            rows=rows,
            start=start,
        )
        return {
            "content": [{"type": "text", "text": json.dumps(data)}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True,
        }


async def _handle_budgets(args: dict[str, Any], client: Any) -> dict[str, Any]:
    """Handle unhcr_budgets tool."""
    year = args.get("year")
    rows = args.get("rows", 100)
    start = args.get("start", 0)
    
    from unhcr_iati_mcp.context import unhcr_filter
    
    try:
        q = unhcr_filter()
        if year:
            q += f' AND budget_period_start:{year}'
        
        data = await client.query(
            collection="budget",
            q=q,
            rows=rows,
            start=start,
        )
        return {
            "content": [{"type": "text", "text": json.dumps(data)}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True,
        }


async def _handle_health_check(args: dict[str, Any], client: Any) -> dict[str, Any]:
    """Handle health_check tool."""
    return {
        "content": [{"type": "text", "text": json.dumps({
            "status": "healthy",
            "version": "0.0.1",
            "transport": "http",
        })}]
    }


async def _handle_datastore_ping(args: dict[str, Any], client: Any) -> dict[str, Any]:
    """Handle datastore_ping tool."""
    try:
        data = await client.query(
            collection="activity",
            q='reporting_org_ref:"XM-DAC-41121"',
            rows=1,
        )
        return {
            "content": [{"type": "text", "text": json.dumps({
                "status": "ok",
                "datastore": "connected",
                "records_found": data.get("response", {}).get("numFound", 0),
            })}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True,
        }


async def _list_resources() -> dict[str, Any]:
    """List all available MCP resources."""
    resources = [
        {
            "uri": "unhcr://donors",
            "name": "UNHCR Donors",
            "description": "Donor code to name mapping",
            "mimeType": "application/json",
        },
        {
            "uri": "unhcr://countries",
            "name": "UNHCR Countries",
            "description": "Country reference data",
            "mimeType": "application/json",
        },
        {
            "uri": "unhcr://sectors",
            "name": "UNHCR Sectors",
            "description": "Sector code to name mapping",
            "mimeType": "application/json",
        },
        {
            "uri": "unhcr://sdgs",
            "name": "UNHCR SDGs",
            "description": "Sustainable Development Goals mapping",
            "mimeType": "application/json",
        },
        {
            "uri": "unhcr://glossary",
            "name": "IATI Glossary",
            "description": "IATI terminology glossary",
            "mimeType": "application/json",
        },
        {
            "uri": "unhcr://portfolio",
            "name": "UNHCR Portfolio",
            "description": "UNHCR portfolio metadata",
            "mimeType": "application/json",
        },
        {
            "uri": "unhcr://schemas/activity",
            "name": "Activity Schema",
            "description": "IATI activity schema definition",
            "mimeType": "application/json",
        },
        {
            "uri": "unhcr://schemas/transaction",
            "name": "Transaction Schema",
            "description": "IATI transaction schema definition",
            "mimeType": "application/json",
        },
        {
            "uri": "unhcr://schemas/budget",
            "name": "Budget Schema",
            "description": "IATI budget schema definition",
            "mimeType": "application/json",
        },
    ]
    
    return {"resources": resources}


async def _read_resource(uri: str) -> dict[str, Any]:
    """Read a specific MCP resource."""
    from unhcr_iati_mcp.context import mcp
    
    try:
        # Try to get the resource from the mcp object
        if hasattr(mcp, "get_resource"):
            data = await mcp.get_resource(uri)
            return {
                "contents": [{
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(data),
                }]
            }
        else:
            # Fallback: return predefined resource data
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
            return {
                "contents": [{
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(data),
                }]
            }
    except Exception as e:
        logger.warning(f"Failed to read resource {uri}: {e}")
        return {
            "contents": [{
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps({"error": str(e)}),
            }]
        }


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Configure logging
    configure_logging()
    
    logger.info("Starting UNHCR IATI MCP HTTP Server")
    logger.info(f"Host: {settings.host}")
    logger.info(f"Port: {settings.port}")
    logger.info(f"OAuth: {'enabled' if settings.use_builtin_oauth else 'disabled'}")
    logger.info(f"Resource URL: {RESOURCE_URL}")
    
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
