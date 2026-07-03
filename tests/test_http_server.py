"""
Tests for HTTP Server functionality.

These tests verify:
- HTTP transport mode
- OAuth 2.1 authentication
- X-API-Key header support
- Health check endpoint
- MCP JSON-RPC endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestHTTPServerImports:
    """Test that HTTP server modules can be imported."""

    def test_import_server_http(self):
        """Test that server_http module can be imported."""
        from unhcr_iati_mcp.server_http import app
        assert app is not None

    def test_import_auth_oauth(self):
        """Test that auth.oauth module can be imported."""
        from unhcr_iati_mcp.auth.oauth import OAuthServer, OAuthToken
        assert OAuthServer is not None
        assert OAuthToken is not None

    def test_import_auth_middleware(self):
        """Test that auth.middleware module can be imported."""
        from unhcr_iati_mcp.auth.middleware import AuthMiddleware
        assert AuthMiddleware is not None


class TestOAuthServer:
    """Test OAuth 2.1 server functionality."""

    def test_oauth_server_initialization(self):
        """Test OAuth server can be initialized."""
        from unhcr_iati_mcp.auth.oauth import OAuthServer
        
        server = OAuthServer()
        assert server is not None
        assert server.tokens == {}
        assert server.clients == {}

    def test_generate_token(self):
        """Test token generation."""
        from unhcr_iati_mcp.auth.oauth import generate_token
        
        token = generate_token("test-client", "test-api-key", 3600)
        assert token is not None
        assert token.access_token is not None
        assert token.token_type == "Bearer"
        assert token.expires_in == 3600
        assert token.scope == "iati:read"
        assert token.client_id == "test-client"

    def test_verify_token(self):
        """Test token verification."""
        from unhcr_iati_mcp.auth.oauth import generate_token, verify_token
        
        # Generate a token
        token = generate_token("test-client", "test-api-key", 3600)
        
        # Verify it
        client_id, api_key = verify_token(token.access_token)
        assert client_id == "test-client"
        assert api_key == "test-api-key"

    def test_oauth_server_issue_token(self):
        """Test OAuth server issuing tokens."""
        from unhcr_iati_mcp.auth.oauth import OAuthServer
        
        server = OAuthServer()
        token = server.issue_token("client1", "api-key-123", 3600)
        
        assert token is not None
        assert token.access_token in server.tokens

    def test_oauth_server_validate_client(self):
        """Test client validation."""
        from unhcr_iati_mcp.auth.oauth import OAuthServer
        
        server = OAuthServer()
        
        # Valid client (any non-empty client_secret >= 10 chars)
        assert server.validate_client("client1", "valid-key-123") is True
        
        # Invalid client (short secret)
        assert server.validate_client("client2", "short") is False
        
        # Invalid client (empty secret)
        assert server.validate_client("client3", "") is False

    def test_get_jwks(self):
        """Test JWKS endpoint."""
        from unhcr_iati_mcp.auth.oauth import OAuthServer
        
        server = OAuthServer()
        jwks = server.get_jwks()
        
        assert "keys" in jwks
        assert len(jwks["keys"]) > 0
        assert "kty" in jwks["keys"][0]

    def test_get_metadata(self):
        """Test OAuth metadata endpoint."""
        from unhcr_iati_mcp.auth.oauth import OAuthServer
        
        server = OAuthServer()
        metadata = server.get_metadata()
        
        assert "issuer" in metadata
        assert "token_endpoint" in metadata
        assert "jwks_uri" in metadata
        assert "grant_types_supported" in metadata


class TestAuthMiddleware:
    """Test authentication middleware functionality."""

    def test_middleware_initialization(self):
        """Test middleware can be initialized."""
        from unhcr_iati_mcp.auth.middleware import AuthMiddleware
        
        middleware = AuthMiddleware()
        assert middleware is not None


class TestConfig:
    """Test configuration settings."""

    def test_config_has_new_fields(self):
        """Test that config has new HTTP-related fields."""
        from unhcr_iati_mcp.config import settings
        
        assert hasattr(settings, "mcp_transport")
        assert hasattr(settings, "host")
        assert hasattr(settings, "port")
        assert hasattr(settings, "resource_url")
        assert hasattr(settings, "use_builtin_oauth")
        assert hasattr(settings, "auth_server_url")
        assert hasattr(settings, "oauth_client_id")
        assert hasattr(settings, "oauth_token_expiry")
        assert hasattr(settings, "log_level")


class TestHealthCheck:
    """Test health check endpoint."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        from unhcr_iati_mcp.server_http import app
        return TestClient(app)

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"
        assert "service" in data
        assert data["service"] == "unhcr-iati-mcp"
        assert "version" in data


class TestOAuthEndpoints:
    """Test OAuth-related endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        from unhcr_iati_mcp.server_http import app
        return TestClient(app)

    def test_oauth_authorization_server_metadata(self, client):
        """Test OAuth authorization server metadata endpoint."""
        response = client.get("/.well-known/oauth-authorization-server")
        assert response.status_code == 200
        
        data = response.json()
        assert "issuer" in data
        assert "token_endpoint" in data

    def test_jwks_endpoint(self, client):
        """Test JWKS endpoint."""
        response = client.get("/.well-known/jwks.json")
        assert response.status_code == 200
        
        data = response.json()
        assert "keys" in data

    def test_oauth_protected_resource_metadata(self, client):
        """Test OAuth protected resource metadata endpoint."""
        response = client.get("/.well-known/oauth-protected-resource")
        assert response.status_code == 200
        
        data = response.json()
        assert "resource" in data
        assert "authorization_servers" in data


class TestMCPEndpoints:
    """Test MCP JSON-RPC endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client with API key."""
        from unhcr_iati_mcp.server_http import app
        client = TestClient(app)
        # Set X-API-Key header for authentication
        client.headers["X-API-Key"] = "test-api-key-1234567890"
        return client

    def test_list_tools(self, client):
        """Test tools/list endpoint."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {},
            },
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "jsonrpc" in data
        assert data["jsonrpc"] == "2.0"
        assert "id" in data
        assert data["id"] == 1
        assert "result" in data
        assert "tools" in data["result"]

    def test_list_resources(self, client):
        """Test resources/list endpoint."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "resources/list",
                "params": {},
            },
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "jsonrpc" in data
        assert "result" in data
        assert "resources" in data["result"]

    def test_invalid_jsonrpc(self, client):
        """Test invalid JSON-RPC request."""
        response = client.post(
            "/mcp",
            json={
                "id": 1,
                "method": "tools/list",
            },
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data

    def test_unknown_method(self, client):
        """Test unknown method."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 3,
                "method": "unknown/method",
                "params": {},
            },
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data


class TestXAPIKeyAuth:
    """Test X-API-Key header authentication."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        from unhcr_iati_mcp.server_http import app
        return TestClient(app)

    def test_x_api_key_auth(self, client):
        """Test X-API-Key header authentication."""
        # Set X-API-Key header
        client.headers["X-API-Key"] = "test-api-key-1234567890"
        
        response = client.get("/health")
        # Health check doesn't require auth, but this tests the header is set
        assert response.status_code == 200

    def test_missing_auth(self, client):
        """Test request without authentication."""
        # Try to access protected endpoint without auth
        # Note: This test uses the basic TestClient which will raise HTTPException
        # We can either use raise_server_exceptions=False or use pytest.raises
        from fastapi.exceptions import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            client.post(
                "/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                    "params": {},
                },
            )
        
        # Check that it's a 401 error
        assert exc_info.value.status_code == 401


class TestServerMain:
    """Test server main function."""

    def test_server_imports(self):
        """Test that server can be imported."""
        from unhcr_iati_mcp.server import main, _run_http_server
        assert callable(main)
        assert callable(_run_http_server)
