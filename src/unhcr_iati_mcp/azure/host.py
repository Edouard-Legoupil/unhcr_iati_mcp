"""
Azure Functions host for UNHCR MCP Server.

This module provides a production-ready Azure Function App that exposes
the UNHCR MCP server with Streamable HTTP transport for Copilot Studio integration.

The MCP endpoint is exposed at /mcp (which becomes /api/mcp in Azure Functions v4).
Copilot Studio requires Streamable HTTP transport, which is fully supported.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, Optional

import azure.functions as func

from starlette.middleware.cors import CORSMiddleware

from ..config import settings
from ..client import UNHCRClient
from ..server import get_server
from ..context import mcp
from ..auth.oauth import OAuthServer

logger = logging.getLogger(__name__)

# Global server and ASGI middleware instances
_server = None
_http_app = None
_asgi_middleware = None
_startup_lock = asyncio.Lock()
_startup_done = False

# Initialize OAuth server for Azure Function App
oauth_server = OAuthServer()
logger.info("OAuth 2.1 server initialized with RS256 signing")


def get_mcp_app():
    """Get or create the FastMCP server instance."""
    global _server
    if _server is None:
        _server = get_server()
    return _server.create_app()


def get_asgi_middleware():
    """Get or create the AsgiMiddleware instance for FastMCP."""
    global _http_app, _asgi_middleware
    if _asgi_middleware is None:
        mcp_app = get_mcp_app()
        # FastMCP Starlette app route path must match the Azure Functions route prefix (/api/mcp)
        base_app = mcp_app.http_app(
            transport="streamable-http",
            path="/api/mcp",
            stateless_http=True,
            json_response=True,
        )
        # Add CORSMiddleware so Copilot Studio browser preflights succeed and Mcp-Session-Id is exposed
        _http_app = CORSMiddleware(
            base_app,
            allow_origins=[
                "*",
                # Microsoft Copilot Studio and related domains
                "https://copilotstudio.microsoft.com",
                "https://*.copilotstudio.microsoft.com",
                "https://copilot.microsoft.com",
                "https://*.copilot.microsoft.com",
                "https://m365.cloud.microsoft",
                "https://*.m365.cloud.microsoft",
                # Claude AI domains
                "https://claude.ai",
                "https://*.claude.ai",
                # Local development
                "http://localhost:*",
                "http://127.0.0.1:*",
            ],
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
            allow_headers=["*"],
            expose_headers=["Mcp-Session-Id", "mcp-session-id", "Content-Type", "Content-Length"],
            allow_credentials=True,
            max_age=86400,
        )
        _asgi_middleware = func.AsgiMiddleware(_http_app)
    return _asgi_middleware


async def ensure_asgi_startup():
    """Ensure FastMCP ASGI lifespan startup has executed on the current event loop."""
    global _startup_done
    if not _startup_done:
        async with _startup_lock:
            if not _startup_done:
                middleware = get_asgi_middleware()
                logger.info("Initializing FastMCP ASGI lifespan startup...")
                await middleware.notify_startup()
                _startup_done = True


# Create the Azure Function App
# Note: In Azure Functions v4 Python, HTTP functions are automatically prefixed with /api
# So our /mcp route becomes /api/mcp, which is the standard Azure Functions behavior
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


# ============================================================================
# OAuth 2.1 Endpoints for Azure Function App
# ============================================================================

@app.function_name(name="oauth_token")
@app.route(route="oauth/token", methods=["POST"])
async def oauth_token_handler(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """
    OAuth 2.1 Token Endpoint (Client Credentials Grant) with RS256 JWT tokens.
    
    This endpoint issues JWT tokens signed with RS256 algorithm for Copilot Studio compatibility.
    Accessible at /api/oauth/token
    """
    try:
        form_data = await req.form()
        grant_type = form_data.get("grant_type")
        client_id = form_data.get("client_id", settings.oauth_client_id)
        client_secret = form_data.get("client_secret")
        
        if grant_type != "client_credentials":
            return func.HttpResponse(
                body=json.dumps({
                    "error": "unsupported_grant_type", 
                    "error_description": "Only client_credentials grant type is supported"
                }),
                status_code=400,
                mimetype="application/json",
                headers={"WWW-Authenticate": 'Bearer error="unsupported_grant_type"'}
            )
        
        if not client_secret:
            return func.HttpResponse(
                body=json.dumps({
                    "error": "invalid_request",
                    "error_description": "client_secret (IATI API key) is required"
                }),
                status_code=400,
                mimetype="application/json",
                headers={"WWW-Authenticate": 'Bearer error="invalid_request"'}
            )
        
        if not oauth_server.validate_client(client_id, client_secret):
            return func.HttpResponse(
                body=json.dumps({
                    "error": "invalid_client",
                    "error_description": "Invalid client credentials - check your IATI API key"
                }),
                status_code=401,
                mimetype="application/json",
                headers={"WWW-Authenticate": 'Bearer error="invalid_client"'}
            )
        
        token = oauth_server.issue_token(
            client_id=client_id,
            client_secret=client_secret,
            expiry=settings.oauth_token_expiry,
        )
        
        return func.HttpResponse(
            body=json.dumps(token.to_dict()),
            status_code=200,
            mimetype="application/json",
            headers={
                "Cache-Control": "no-store",
                "Pragma": "no-cache",
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        )
    except Exception as e:
        logger.error(f"Token endpoint error: {e}", exc_info=True)
        return func.HttpResponse(
            body=json.dumps({
                "error": "server_error",
                "error_description": str(e)
            }),
            status_code=500,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )


@app.function_name(name="oauth_authorization_server")
@app.route(route=".well-known/oauth-authorization-server", methods=["GET"])
async def oauth_authorization_server_metadata(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """
    OAuth 2.1 Authorization Server Metadata (RFC 8414).
    
    Accessible at /api/.well-known/oauth-authorization-server
    """
    try:
        metadata = oauth_server.get_metadata()
        return func.HttpResponse(
            body=json.dumps(metadata),
            status_code=200,
            mimetype="application/json",
            headers={
                "Content-Type": "application/json",
                "Cache-Control": "public, max-age=86400",
                "Access-Control-Allow-Origin": "*"
            }
        )
    except Exception as e:
        logger.error(f"OAuth metadata error: {e}", exc_info=True)
        return func.HttpResponse(
            body=json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )


@app.function_name(name="jwks")
@app.route(route=".well-known/jwks.json", methods=["GET"])
async def jwks_handler(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """
    JSON Web Key Set (JWKS) endpoint for JWT token verification.
    
    Accessible at /api/.well-known/jwks.json
    """
    try:
        jwks_data = oauth_server.get_jwks()
        return func.HttpResponse(
            body=json.dumps(jwks_data),
            status_code=200,
            mimetype="application/json",
            headers={
                "Content-Type": "application/json",
                "Cache-Control": "public, max-age=86400",
                "Access-Control-Allow-Origin": "*"
            }
        )
    except Exception as e:
        logger.error(f"JWKS error: {e}", exc_info=True)
        return func.HttpResponse(
            body=json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )


@app.function_name(name="oauth_protected_resource")
@app.route(route=".well-known/oauth-protected-resource", methods=["GET"])
async def oauth_protected_resource_metadata(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """
    OAuth Protected Resource Metadata (RFC 9728).
    
    Accessible at /api/.well-known/oauth-protected-resource
    """
    try:
        resource_url = settings.get_resource_url()
        auth_servers = [resource_url]
        
        metadata = {
            "resource": resource_url,
            "authorization_servers": auth_servers
        }
        
        return func.HttpResponse(
            body=json.dumps(metadata),
            status_code=200,
            mimetype="application/json",
            headers={
                "Content-Type": "application/json",
                "Cache-Control": "public, max-age=86400",
                "Access-Control-Allow-Origin": "*"
            }
        )
    except Exception as e:
        logger.error(f"Protected resource metadata error: {e}", exc_info=True)
        return func.HttpResponse(
            body=json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )


@app.function_name(name="mcp")
@app.route(route="mcp/{*path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"])
async def mcp_handler(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """
    Main MCP HTTP handler for Streamable HTTP transport.
    
    This endpoint handles all MCP protocol requests and routes them to the
    FastMCP server via Azure Functions AsgiMiddleware.
    
    The endpoint path is /mcp, which Azure Functions v4 automatically exposes as /api/mcp.
    Copilot Studio should be configured to connect to: https://<function-app>.azurewebsites.net/api/mcp
    
    Args:
        req: Azure Functions HTTP request
        context: Azure Functions context
        
    Returns:
        HTTP response from the MCP server
    """
    try:
        method = req.method.upper()
        url = req.url
        query_string = dict(req.params)
        headers_dict = dict(req.headers)

        # Parse MCP method from JSON-RPC body if POST
        mcp_method = None
        body_bytes = req.get_body()
        if method == "POST" and body_bytes:
            try:
                body_json = json.loads(body_bytes.decode("utf-8"))
                mcp_method = body_json.get("method")
            except Exception:
                pass

        sanitized_headers = {
            k: ("***" if k.lower() in ["authorization", "x-functions-key"] else v)
            for k, v in headers_dict.items()
        }

        logger.info(
            f"[MCP INCOMING] Method={method} URL={url} Query={query_string} "
            f"McpMethod={mcp_method} Headers={json.dumps(sanitized_headers)}"
        )

        # 1. Explicit OPTIONS handling for Copilot Studio probes and CORS preflights
        if method == "OPTIONS":
            origin = req.headers.get("origin", "*")
            ac_req_headers = req.headers.get(
                "access-control-request-headers",
                "content-type, mcp-session-id, accept, authorization, x-requested-with"
            )
            headers = {
                "Access-Control-Allow-Origin": origin if origin != "*" else "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, HEAD",
                "Access-Control-Allow-Headers": ac_req_headers,
                "Access-Control-Expose-Headers": "Mcp-Session-Id, mcp-session-id, Content-Type",
                "Access-Control-Max-Age": "86400",
                "Allow": "GET, POST, PUT, DELETE, OPTIONS, HEAD",
                "Content-Type": "text/plain; charset=utf-8",
            }
            if origin != "*":
                headers["Vary"] = "Origin"
                headers["Access-Control-Allow-Credentials"] = "true"

            logger.info(f"[MCP RESPONSE] Method={method} URL={url} Status=200 Headers={headers}")
            return func.HttpResponse(body="OK", status_code=200, headers=headers)

        # 2. Explicit HEAD handling
        if method == "HEAD":
            head_headers = {
                "Content-Type": "application/json",
                "Allow": "GET, POST, PUT, DELETE, OPTIONS, HEAD"
            }
            logger.info(f"[MCP RESPONSE] Method={method} URL={url} Status=200 Headers={head_headers}")
            return func.HttpResponse(
                body="",
                status_code=200,
                headers=head_headers
            )

        # 3. For GET, POST, DELETE, pass to ASGI middleware
        await ensure_asgi_startup()
        middleware = get_asgi_middleware()
        res = await middleware.handle_async(req, context)

        logger.info(
            f"[MCP RESPONSE] Method={method} URL={url} McpMethod={mcp_method} "
            f"Status={res.status_code} ResponseHeaders={dict(res.headers)}"
        )
        return res
    except Exception as e:
        logger.error(f"Error in MCP handler: {e}", exc_info=True)
        return func.HttpResponse(
            body=json.dumps({"error": "Internal Server Error", "message": str(e)}),
            status_code=500,
            mimetype="application/json",
        )


@app.function_name(name="health")
@app.route(route="health", methods=["GET"])
async def health_handler(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """
    Health check endpoint.
    
    Returns the health status of the MCP server and UNHCR API.
    Accessible at /api/health
    """
    try:
        async with UNHCRClient() as client:
            health = await client.get_health()
        
        body = {
            "status": "healthy",
            "server": {
                "name": settings.MCP_SERVER_NAME,
                "version": settings.MCP_SERVER_VERSION,
                "environment": settings.ENVIRONMENT,
            },
            "api": {
                "base_url": settings.get_api_base_url(),
                "status": health.get("status", "unknown"),
            },
            "endpoints": {
                "mcp": "/api/mcp",
                "health": "/api/health",
                "info": "/api/info",
                "openapi": "/api/openapi.json",
            },
        }
        
        return func.HttpResponse(
            body=json.dumps(body),
            status_code=200,
            mimetype="application/json",
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return func.HttpResponse(
            body=json.dumps({"status": "unhealthy", "error": str(e)}),
            status_code=500,
            mimetype="application/json",
        )


@app.function_name(name="info")
@app.route(route="info", methods=["GET"])
async def info_handler(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """
    Server information endpoint.
    
    Returns information about the MCP server and available tools.
    Accessible at /api/info
    """
    try:
        mcp_app = get_mcp_app()
        tools = await mcp_app.list_tools()
        
        body = {
            "server": {
                "name": settings.MCP_SERVER_NAME,
                "version": settings.MCP_SERVER_VERSION,
                "environment": settings.ENVIRONMENT,
            },
            "api": {
                "base_url": settings.get_api_base_url(),
                "version": settings.UNHCR_API_VERSION,
            },
            "transport": {
                "type": "streamable-http",
                "path": "/mcp",
                "full_url": f"https://{os.environ.get('WEBSITE_HOSTNAME', 'localhost')}/api/mcp",
            },
            "tools": [tool.name for tool in tools],
            "tool_count": len(tools),
        }
        
        return func.HttpResponse(
            body=json.dumps(body),
            status_code=200,
            mimetype="application/json",
        )
    except Exception as e:
        logger.error(f"Info endpoint failed: {e}", exc_info=True)
        return func.HttpResponse(
            body=json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
        )


@app.function_name(name="openapi")
@app.route(route="openapi.json", methods=["GET"])
async def openapi_handler(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """
    OpenAPI schema endpoint for Copilot Studio discovery.
    
    This endpoint provides an OpenAPI 3.0 schema that describes all available
    MCP tools, which Copilot Studio uses for server discovery and integration.
    
    Accessible at /api/openapi.json
    """
    try:
        mcp_app = get_mcp_app()
        tools = await mcp_app.list_tools()
        
        # Generate OpenAPI schema dynamically from MCP tools
        openapi_schema = {
            "openapi": "3.0.0",
            "info": {
                "title": settings.MCP_SERVER_NAME,
                "version": settings.MCP_SERVER_VERSION,
                "description": "UNHCR Refugee Data Portal MCP Server - Provides access to UNHCR refugee statistics and indicators",
                "contact": {
                    "name": "UNHCR Data Team",
                    "email": "data@unhcr.org"
                }
            },
            "servers": [
                {
                    "url": f"https://{os.environ.get('WEBSITE_HOSTNAME', 'localhost')}/api",
                    "description": "Production server"
                }
            ],
            "paths": {},
            "components": {
                "schemas": {}
            }
        }
        
        # Add paths for each MCP tool
        for tool in tools:
            tool_name = tool.name
            tool_path = f"/mcp/{tool_name}"
            
            # Get tool parameters from the tool's JSON schema
            tool_params = {}
            required_params = []
            
            if hasattr(tool, 'parameters') and isinstance(tool.parameters, dict):
                # tool.parameters contains the full JSON schema
                properties = tool.parameters.get('properties', {})
                required_params = tool.parameters.get('required', [])
                
                for param_name, param_schema in properties.items():
                    if isinstance(param_schema, dict):
                        tool_params[param_name] = {
                            "description": param_schema.get('description', ''),
                            "type": param_schema.get('type', 'string'),
                            "default": param_schema.get('default')
                        }
            
            openapi_schema["paths"][tool_path] = {
                "post": {
                    "tags": ["MCP Tools"],
                    "summary": tool.description or tool_name,
                    "description": tool.description or f"Execute {tool_name} tool",
                    "operationId": tool_name,
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": tool_params,
                                    "required": required_params
                                }
                            }
                        },
                        "required": True
                    },
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        
        # Add MCP-specific endpoints
        openapi_schema["paths"]["/mcp"] = {
            "post": {
                "tags": ["MCP Protocol"],
                "summary": "MCP Protocol Endpoint",
                "description": "Main MCP protocol endpoint for Streamable HTTP transport",
                "operationId": "mcp_protocol",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "jsonrpc": {"type": "string", "enum": ["2.0"]},
                                    "id": {"type": "integer"},
                                    "method": {"type": "string"},
                                    "params": {"type": "object"}
                                },
                                "required": ["jsonrpc", "id", "method"]
                            }
                        }
                    },
                    "required": True
                },
                "responses": {
                    "200": {
                        "description": "MCP protocol response"
                    }
                }
            }
        }
        
        return func.HttpResponse(
            body=json.dumps(openapi_schema, indent=2),
            status_code=200,
            mimetype="application/json",
        )
    except Exception as e:
        logger.error(f"OpenAPI schema generation failed: {e}", exc_info=True)
        return func.HttpResponse(
            body=json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
        )


@app.function_name(name="mcp_schema")
@app.route(route=".well-known/mcp/schema", methods=["GET"])
async def mcp_schema_handler(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """
    MCP Schema Discovery Endpoint for Copilot Studio.
    
    This endpoint implements the MCP schema discovery protocol as specified in:
    https://github.com/modelcontextprotocol/specification/blob/main/protocol/mcp-schema.md
    
    Returns a JSON schema describing the MCP server capabilities.
    Accessible at /.well-known/mcp/schema
    """
    try:
        mcp_app = get_mcp_app()
        tools = await mcp_app.list_tools()
        
        # Generate MCP-specific schema following the MCP specification
        schema = {
            "name": settings.MCP_SERVER_NAME,
            "version": settings.MCP_SERVER_VERSION,
            "description": "UNHCR Refugee Data Portal MCP Server - Provides access to UNHCR refugee statistics and indicators",
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {},
                "prompts": {}
            },
            "serverInfo": {
                "name": settings.MCP_SERVER_NAME,
                "version": settings.MCP_SERVER_VERSION,
                "environment": settings.ENVIRONMENT,
                "baseUrl": f"https://{os.environ.get('WEBSITE_HOSTNAME', 'localhost')}/api"
            },
            "endpoints": {
                "mcp": "/api/mcp",
                "health": "/api/health",
                "info": "/api/info",
                "openapi": "/api/openapi.json",
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
        
        return func.HttpResponse(
            body=json.dumps(schema, indent=2),
            status_code=200,
            mimetype="application/json",
            headers={
                "Cache-Control": "public, max-age=3600",
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Max-Age": "86400"
            }
        )
    except Exception as e:
        logger.error(f"MCP schema generation failed: {e}", exc_info=True)
        return func.HttpResponse(
            body=json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )


@app.function_name(name="mcp_protocol")
@app.route(route=".well-known/mcp", methods=["GET"])
async def mcp_protocol_handler(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """
    MCP Protocol Schema Endpoint.
    
    Provides the MCP protocol schema for validation.
    Accessible at /.well-known/mcp
    """
    try:
        protocol_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "MCP Protocol Schema",
            "description": "Model Context Protocol JSON-RPC 2.0 Schema",
            "type": "object",
            "properties": {
                "jsonrpc": {
                    "type": "string",
                    "enum": ["2.0"],
                    "description": "JSON-RPC version"
                },
                "id": {
                    "type": ["integer", "string"],
                    "description": "Request identifier"
                },
                "method": {
                    "type": "string",
                    "description": "MCP method name"
                },
                "params": {
                    "type": "object",
                    "description": "Method parameters",
                    "additionalProperties": True
                }
            },
            "required": ["jsonrpc", "id", "method"],
            "additionalProperties": False,
            "examples": [
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "CopilotStudio", "version": "1.0"}
                    }
                },
                {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {}
                }
            ]
        }
        
        return func.HttpResponse(
            body=json.dumps(protocol_schema, indent=2),
            status_code=200,
            mimetype="application/json",
            headers={
                "Cache-Control": "public, max-age=86400",
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Max-Age": "86400"
            }
        )
    except Exception as e:
        logger.error(f"MCP protocol schema failed: {e}", exc_info=True)
        return func.HttpResponse(
            body=json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )


@app.function_name(name="well_known_openapi")
@app.route(route=".well-known/openapi.json", methods=["GET"])
async def well_known_openapi_handler(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """
    Well-known OpenAPI Schema Endpoint.
    
    Redirects to the main OpenAPI schema.
    Accessible at /.well-known/openapi.json
    """
    try:
        # Redirect to the main OpenAPI endpoint
        hostname = os.environ.get('WEBSITE_HOSTNAME', 'localhost')
        redirect_url = f"https://{hostname}/api/openapi.json"
        
        return func.HttpResponse(
            status_code=302,
            headers={
                "Location": redirect_url,
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS"
            }
        )
    except Exception as e:
        logger.error(f"Well-known OpenAPI redirect failed: {e}", exc_info=True)
        return func.HttpResponse(
            body=json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )

