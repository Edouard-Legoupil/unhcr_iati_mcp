"""
Authentication Middleware for UNHCR IATI MCP Server.

This module provides FastAPI middleware for:
- OAuth 2.1 Bearer token validation
- X-API-Key header validation
- Request context management for API clients
"""

from typing import Any, Callable, Optional

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer

from unhcr_iati_mcp.config import settings


# Security schemes
bearer_scheme = HTTPBearer(auto_error=False)


class AuthMiddleware:
    """
    Middleware for handling authentication in HTTP mode.
    
    Supports two authentication methods:
    1. OAuth 2.1 Bearer tokens (primary)
    2. X-API-Key header (fallback for HuggingChat, etc.)
    
    The middleware:
    - Validates credentials
    - Creates IATIClient instances per request
    - Attaches client to request state
    - Skips authentication for public endpoints
    """
    
    # Public endpoints that don't require authentication
    PUBLIC_PATHS = [
        "/health",
        "/.well-known/oauth-authorization-server",
        "/.well-known/jwks.json",
        "/.well-known/oauth-protected-resource",
        "/oauth/token",
        "/oauth/info",
        "/docs",
        "/openapi.json",
        "/redoc",
    ]
    
    def __init__(self, oauth_server: Optional[Any] = None):
        """
        Initialize the auth middleware.
        
        Args:
            oauth_server: Optional OAuth server instance for token validation
        """
        self.oauth_server = oauth_server
    
    async def __call__(
        self, 
        request: Request, 
        call_next: Callable
    ):
        """
        Process a request, validating authentication and attaching client.
        
        Args:
            request: The incoming FastAPI request
            call_next: The next middleware/route handler
        
        Returns:
            Response from the next handler
        """
        # Check if this is a public endpoint
        path = request.url.path
        if any(path == public_path or path.startswith(public_path + "/") for public_path in self.PUBLIC_PATHS):
            # Skip authentication for public endpoints
            return await call_next(request)
        
        # Import here to avoid circular imports
        from unhcr_iati_mcp.client import IATIClient
        
        # Check for X-API-Key header first (for HuggingChat and similar clients)
        api_key_header = request.headers.get("X-API-Key")
        auth_header = request.headers.get("Authorization")
        
        api_client = None
        auth_method = None
        client_id = None
        
        if api_key_header:
            # X-API-Key header authentication
            api_key = api_key_header
            
            # Validate API key format (basic check)
            if not api_key or len(api_key) < 10:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid X-API-Key header",
                    headers={"WWW-Authenticate": 'Bearer error="invalid_api_key"'},
                )
            
            # Create API client with the API key
            api_client = IATIClient(api_key=api_key)
            auth_method = "api-key"
            client_id = "api-key-user"
            
        elif auth_header:
            # OAuth Bearer token authentication
            parts = auth_header.split(" ")
            if len(parts) != 2 or parts[0].lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Authorization header format",
                    headers={"WWW-Authenticate": 'Bearer error="invalid_request"'},
                )
            
            token = parts[1]
            
            # Verify token and extract API key
            if self.oauth_server:
                try:
                    from unhcr_iati_mcp.auth.oauth import verify_token
                    client_id, api_key = verify_token(token)
                    api_client = IATIClient(api_key=api_key)
                    auth_method = "oauth"
                except HTTPException as e:
                    # Add proper WWW-Authenticate header
                    resource_url = settings.resource_url or f"http://{settings.host}:{settings.port}"
                    e.headers["WWW-Authenticate"] = f'Bearer resource="{resource_url}/.well-known/oauth-protected-resource", error="invalid_token"'
                    raise
            else:
                # If no OAuth server, try to use the token as API key directly
                # This is a fallback for development
                api_key = token
                api_client = IATIClient(api_key=api_key)
                auth_method = "bearer"
                client_id = "default"
        else:
            # No authentication provided
            resource_url = settings.resource_url or f"http://{settings.host}:{settings.port}"
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization required",
                headers={"WWW-Authenticate": f'Bearer resource="{resource_url}/.well-known/oauth-protected-resource", error="unauthorized"'},
            )
        
        # Attach client and auth info to request state
        request.state.api_client = api_client
        request.state.auth_method = auth_method
        request.state.client_id = client_id
        
        # Process request
        response = await call_next(request)
        
        return response


def get_api_client(request: Request):
    """
    Dependency to get the authenticated IATI client from request state.
    
    Args:
        request: The FastAPI request
    
    Returns:
        IATIClient: The authenticated client for this request
    
    Raises:
        HTTPException: If client is not attached to request
    """
    if not hasattr(request.state, "api_client") or request.state.api_client is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API client not initialized - authentication required",
        )
    return request.state.api_client


def require_auth(request: Request) -> None:
    """
    Dependency to ensure request is authenticated.
    
    Args:
        request: The FastAPI request
    
    Raises:
        HTTPException: If not authenticated
    """
    if not hasattr(request.state, "api_client") or request.state.api_client is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
