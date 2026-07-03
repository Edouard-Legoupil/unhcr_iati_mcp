"""
OAuth 2.1 Server for UNHCR IATI MCP Server.

This module implements a built-in OAuth 2.1 authorization server with client credentials
grant type. It issues tokens that contain encrypted IATI API keys, eliminating the
need for external authentication services.

Based on MCP Authorization Specification and OAuth 2.1 (RFC 9728).
"""

import base64
import hashlib
import json
import secrets
import time
from dataclasses import dataclass
from typing import Any

from cryptography.fernet import Fernet
from fastapi import HTTPException, status

from unhcr_iati_mcp.config import settings


# Generate a key for encrypting API keys in tokens
# In production, this should be loaded from environment or secret management
FERNET_KEY = Fernet.generate_key()
_cipher_suite = Fernet(FERNET_KEY)


@dataclass
class OAuthToken:
    """Represents an OAuth access token with metadata."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    scope: str = "iati:read"
    client_id: str = "default"
    created_at: float = 0.0
    
    def to_dict(self) -> dict[str, Any]:
        """Convert token to dictionary for JSON response."""
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "scope": self.scope,
        }


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key for storage in a token."""
    return _cipher_suite.encrypt(api_key.encode()).decode()


def decrypt_api_key(encrypted: str) -> str:
    """Decrypt an API key from a token."""
    return _cipher_suite.decrypt(encrypted.encode()).decode()


def generate_token(client_id: str, api_key: str, expiry: int = 3600) -> OAuthToken:
    """
    Generate an OAuth access token containing an encrypted API key.
    
    Args:
        client_id: The client identifier
        api_key: The IATI API key to encrypt into the token
        expiry: Token expiry in seconds (default: 3600 = 1 hour)
    
    Returns:
        OAuthToken: The generated token with metadata
    """
    # Encrypt the API key
    encrypted_key = encrypt_api_key(api_key)
    
    # Create token payload
    payload = {
        "client_id": client_id,
        "api_key": encrypted_key,
        "exp": int(time.time()) + expiry,
        "iat": int(time.time()),
        "scope": "iati:read",
    }
    
    # Encode payload as JSON and base64
    token_payload = base64.urlsafe_b64encode(
        json.dumps(payload).encode()
    ).decode().rstrip("=")
    
    # Create a simple token (in production, use proper JWT signing)
    # For simplicity, we use a signed payload format
    signature = hashlib.sha256(
        (token_payload + FERNET_KEY.decode()).encode()
    ).hexdigest()[:16]
    
    access_token = f"{token_payload}.{signature}"
    
    return OAuthToken(
        access_token=access_token,
        token_type="Bearer",
        expires_in=expiry,
        scope="iati:read",
        client_id=client_id,
        created_at=time.time(),
    )


def verify_token(token: str) -> tuple[str, str]:
    """
    Verify an OAuth access token and extract the API key.
    
    Args:
        token: The access token to verify
    
    Returns:
        tuple: (client_id, api_key)
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Split token
        parts = token.split(".")
        if len(parts) != 2:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
            )
        
        token_payload, signature = parts
        
        # Verify signature
        expected_signature = hashlib.sha256(
            (token_payload + FERNET_KEY.decode()).encode()
        ).hexdigest()[:16]
        
        if signature != expected_signature:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token signature",
                headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
            )
        
        # Decode payload
        token_payload += "=" * (4 - len(token_payload) % 4)  # Add padding
        payload = json.loads(
            base64.urlsafe_b64decode(token_payload.encode())
        )
        
        # Check expiration
        if payload.get("exp", 0) < time.time():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
            )
        
        # Extract and decrypt API key
        client_id = payload.get("client_id", "default")
        encrypted_key = payload.get("api_key", "")
        api_key = decrypt_api_key(encrypted_key)
        
        return client_id, api_key
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
        )


class OAuthServer:
    """
    Built-in OAuth 2.1 authorization server.
    
    Implements the client credentials grant type as specified in RFC 6749.
    In this simplified implementation, the client_secret IS the IATI API key.
    
    This allows users to:
    1. Use their IATI API key directly as client_secret
    2. Receive an OAuth token containing their encrypted API key
    3. Use the token for subsequent requests
    
    Benefits:
    - No external authentication service required
    - Zero registration needed
    - Standards-compliant OAuth 2.1 flow
    - Works with all MCP clients that support OAuth
    """
    
    def __init__(self):
        """Initialize the OAuth server."""
        self.tokens: dict[str, OAuthToken] = {}  # token -> OAuthToken mapping
        self.clients: dict[str, str] = {}  # client_id -> api_key mapping
    
    def get_fixed_client_id(self) -> str:
        """Get the fixed client ID for simplified auth (any string works)."""
        return settings.oauth_client_id
    
    def validate_client(self, client_id: str, client_secret: str) -> bool:
        """
        Validate client credentials.
        
        In this implementation, we validate that the client_secret is non-empty
        and appears to be a valid API key format (at least 10 characters).
        
        Args:
            client_id: The client identifier (any string accepted)
            client_secret: The client secret (must be valid IATI API key)
        
        Returns:
            bool: True if valid, False otherwise
        """
        # Basic validation - client_secret should be a non-empty string
        # In production, you might want to validate against known API keys
        if not client_secret or len(client_secret) < 10:
            return False
        
        # Store the client mapping (optional, for token management)
        self.clients[client_id] = client_secret
        
        return True
    
    def issue_token(
        self, 
        client_id: str, 
        client_secret: str, 
        expiry: int = 3600
    ) -> OAuthToken:
        """
        Issue an access token for valid client credentials.
        
        Args:
            client_id: The client identifier
            client_secret: The client secret (IATI API key)
            expiry: Token expiry in seconds
        
        Returns:
            OAuthToken: The issued token
        """
        token = generate_token(client_id, client_secret, expiry)
        self.tokens[token.access_token] = token
        return token
    
    def verify_token(self, token: str) -> tuple[str, str]:
        """
        Verify an access token and extract credentials.
        
        Args:
            token: The access token
        
        Returns:
            tuple: (client_id, api_key)
        
        Raises:
            HTTPException: If token is invalid
        """
        return verify_token(token)
    
    def get_jwks(self) -> dict[str, Any]:
        """
        Get JWKS (JSON Web Key Set) for token verification.
        
        Returns:
            dict: JWKS representation
        """
        # In a full implementation, this would contain the actual keys
        # For simplicity, we return a minimal JWKS
        return {
            "keys": [
                {
                    "kty": "oct",
                    "use": "sig",
                    "kid": hashlib.sha256(FERNET_KEY).hexdigest()[:8],
                    "alg": "HS256",
                }
            ]
        }
    
    def get_metadata(self) -> dict[str, Any]:
        """
        Get OAuth Authorization Server Metadata (RFC 8414).
        
        Returns:
            dict: Authorization server metadata
        """
        resource_url = settings.resource_url or f"http://{settings.host}:{settings.port}"
        
        return {
            "issuer": resource_url,
            "authorization_endpoint": f"{resource_url}/oauth/authorize",
            "token_endpoint": f"{resource_url}/oauth/token",
            "jwks_uri": f"{resource_url}/.well-known/jwks.json",
            "response_types_supported": ["token"],
            "grant_types_supported": ["client_credentials"],
            "subject_types_supported": ["public"],
            "id_token_signing_alg_values_supported": ["HS256"],
            "scopes_supported": ["iati:read"],
            "token_endpoint_auth_methods_supported": ["client_secret_basic"],
        }
