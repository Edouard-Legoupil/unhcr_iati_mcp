"""
Authentication module for UNHCR IATI MCP Server.

This module provides OAuth 2.1 authentication support including:
- Built-in OAuth server (no external dependencies)
- X-API-Key header support for HuggingChat and similar clients
- Token validation middleware
- Protected Resource Metadata (RFC 9728) endpoint
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from unhcr_iati_mcp.auth.oauth import OAuthServer, OAuthToken
    from unhcr_iati_mcp.auth.middleware import AuthMiddleware


def get_oauth_server():
    """Lazy import of OAuthServer to avoid circular imports."""
    from unhcr_iati_mcp.auth.oauth import OAuthServer
    return OAuthServer


def get_auth_middleware():
    """Lazy import of AuthMiddleware to avoid circular imports."""
    from unhcr_iati_mcp.auth.middleware import AuthMiddleware
    return AuthMiddleware
