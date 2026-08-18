"""
OAuth 2.1 Server for UNHCR IATI MCP Server.

This module implements a proper OAuth 2.1 authorization server with JWT tokens
signed using RS256 algorithm for Copilot Studio compatibility.

Based on MCP Authorization Specification and OAuth 2.1 (RFC 9728).
"""

import base64
import hashlib
import json
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException, status

from unhcr_iati_mcp.config import settings


# In-memory key storage shared across generated and validated tokens.
GLOBAL_API_KEY_STORE: Dict[str, str] = {}


# Generate or load RSA key pair
# In production, these should be loaded from environment variables or secret management
try:
    # Try to load from environment variables (base64 encoded)
    import os
    private_key_pem = os.environ.get("OAUTH_PRIVATE_KEY")
    public_key_pem = os.environ.get("OAUTH_PUBLIC_KEY")
    
    if private_key_pem and public_key_pem:
        # Decode and load existing keys
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=default_backend()
        )
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode(),
            backend=default_backend()
        )
    else:
        # Generate new keys (for development only)
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        # Serialize keys for potential storage
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode()
        
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
        
        # Store in environment for persistence (development only)
        os.environ["OAUTH_PRIVATE_KEY"] = private_key_pem
        os.environ["OAUTH_PUBLIC_KEY"] = public_key_pem

except Exception as e:
    # Fallback: Generate new keys if loading fails
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()


@dataclass
class OAuthToken:
    """Represents an OAuth access token with metadata."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    scope: str = "iati:read"
    client_id: str = "default"
    created_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert token to dictionary for JSON response."""
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "scope": self.scope,
        }


def generate_jwt_token(client_id: str, api_key: str, expiry: int = 3600, 
                       additional_claims: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate a JWT token signed with RS256 algorithm.
    
    Args:
        client_id: The client identifier
        api_key: The IATI API key (stored as a reference, not the actual key in production)
        expiry: Token expiry in seconds (default: 3600 = 1 hour)
        additional_claims: Additional claims to include in the token
        
    Returns:
        str: The signed JWT token
    """
    now = datetime.now(timezone.utc)
    
    # Create token payload with standard OAuth 2.1 claims
    payload = {
        "iss": settings.get_resource_url(),  # Issuer
        "sub": client_id,  # Subject (client identifier)
        "aud": settings.get_resource_url(),  # Audience
        "exp": now + timedelta(seconds=expiry),  # Expiration time
        "nbf": now,  # Not before
        "iat": now,  # Issued at
        "jti": secrets.token_urlsafe(16),  # JWT ID
        "scope": "iati:read",
        # Custom claims for API key reference
        "api_key_ref": hashlib.sha256(api_key.encode()).hexdigest(),  # Store hash, not actual key
        "client_id": client_id,
    }
    
    # Add additional claims if provided
    if additional_claims:
        payload.update(additional_claims)
    
    # Sign the token with RS256
    token = jwt.encode(payload, private_key, algorithm="RS256")
    
    return token


def verify_jwt_token(token: str) -> Dict[str, Any]:
    """
    Verify a JWT token and extract its claims.
    
    Args:
        token: The JWT token to verify
        
    Returns:
        Dict[str, Any]: The decoded token claims
        
    Raises:
        HTTPException: If token is invalid, expired, or verification fails
    """
    try:
        # Decode and verify the token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=settings.get_resource_url(),
            issuer=settings.get_resource_url(),
            options={
                "require": ["exp", "iat", "sub", "iss", "aud"],
                "verify_exp": True,
                "verify_iat": True,
                "verify_iss": True,
                "verify_aud": True,
            }
        )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token", error_description="Token has expired"'}
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token"'}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token"'}
        )


def get_jwks() -> Dict[str, Any]:
    """
    Get JWKS (JSON Web Key Set) for token verification.
    
    Returns:
        Dict[str, Any]: JWKS representation with the public key
    """
    # Serialize public key to PEM format
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    
    # Convert PEM to JWK format
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
    
    if isinstance(public_key, RSAPublicKey):
        # Extract key components
        public_numbers = public_key.public_numbers()
        
        # Convert to base64url encoding
        def to_base64url(data: bytes) -> str:
            return base64.urlsafe_b64encode(data).decode().rstrip("=")
        
        # Create JWK
        jwk = {
            "kty": "RSA",
            "use": "sig",
            "kid": hashlib.sha256(public_key_pem.encode()).hexdigest()[:8],
            "alg": "RS256",
            "n": to_base64url(public_numbers.n.to_bytes((public_numbers.n.bit_length() + 7) // 8, 'big')),
            "e": to_base64url(public_numbers.e.to_bytes(3, 'big')),  # Public exponent (usually 65537)
        }
        
        return {
            "keys": [jwk]
        }
    else:
        # Fallback: Return minimal JWKS
        return {
            "keys": [
                {
                    "kty": "RSA",
                    "use": "sig",
                    "kid": hashlib.sha256(public_key_pem.encode()).hexdigest()[:8],
                    "alg": "RS256",
                }
            ]
        }


def get_metadata() -> Dict[str, Any]:
    """
    Get OAuth Authorization Server Metadata (RFC 8414).
    
    Returns:
        Dict[str, Any]: Authorization server metadata
    """
    resource_url = settings.get_resource_url()
    
    return {
        "issuer": resource_url,
        "authorization_endpoint": f"{resource_url}/oauth/authorize",
        "token_endpoint": f"{resource_url}/oauth/token",
        "jwks_uri": f"{resource_url}/.well-known/jwks.json",
        "response_types_supported": ["token"],
        "grant_types_supported": ["client_credentials"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["RS256"],
        "scopes_supported": ["iati:read"],
        "token_endpoint_auth_methods_supported": ["client_secret_basic", "client_secret_post"],
        "code_challenge_methods_supported": [],
        "tls_client_certificate_bound_access_tokens": False,
    }


class OAuthServer:
    """
    OAuth 2.1 authorization server with proper JWT support.
    
    Implements the client credentials grant type as specified in RFC 6749.
    Uses RS256 signing for JWT tokens to ensure compatibility with Copilot Studio.
    """
    
    def __init__(self):
        """Initialize the OAuth server."""
        self.tokens: Dict[str, OAuthToken] = {}  # token -> OAuthToken mapping
        self.clients: Dict[str, str] = {}  # client_id -> api_key mapping
        self.api_key_store: Dict[str, str] = {}  # Store API keys securely (in production, use proper storage)
    
    def get_fixed_client_id(self) -> str:
        """Get the fixed client ID for simplified auth (any string works)."""
        return settings.oauth_client_id
    
    def validate_client(self, client_id: str, client_secret: str) -> bool:
        """
        Validate client credentials.
        
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

        # Store the API key (in production, use proper secure storage)
        self.api_key_store[client_id] = client_secret
        GLOBAL_API_KEY_STORE[client_id] = client_secret

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
        # Generate JWT token
        access_token = generate_jwt_token(client_id, client_secret, expiry)
        
        token = OAuthToken(
            access_token=access_token,
            token_type="Bearer",
            expires_in=expiry,
            scope="iati:read",
            client_id=client_id,
            created_at=time.time()
        )
        
        self.tokens[access_token] = token
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
        try:
            # Verify and decode the JWT token
            payload = verify_jwt_token(token)

            # Extract client_id and API key reference
            client_id = payload.get("sub", "default")
            api_key_ref = payload.get("api_key_ref", "")

            api_key = self.api_key_store.get(client_id) or GLOBAL_API_KEY_STORE.get(client_id)
            if not api_key and api_key_ref:
                for stored_key in list(self.api_key_store.values()) + list(GLOBAL_API_KEY_STORE.values()):
                    if hashlib.sha256(stored_key.encode()).hexdigest() == api_key_ref:
                        api_key = stored_key
                        break

            if not api_key:
                api_key = settings.iati_api_key

            if not api_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid client credentials",
                    headers={"WWW-Authenticate": 'Bearer error="invalid_client"'}
                )

            return client_id, api_key

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
                headers={"WWW-Authenticate": 'Bearer error="invalid_token"'}
            )
    
    def get_jwks(self) -> Dict[str, Any]:
        """
        Get JWKS (JSON Web Key Set) for token verification.
        
        Returns:
            Dict[str, Any]: JWKS representation
        """
        return get_jwks()
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get OAuth Authorization Server Metadata (RFC 8414).
        
        Returns:
            Dict[str, Any]: Authorization server metadata
        """
        return get_metadata()


# Backwards compatibility functions
def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key for storage in a token (legacy method)."""
    from cryptography.fernet import Fernet
    from cryptography.fernet import Fernet
    # Generate a key for encrypting API keys in tokens
    FERNET_KEY = Fernet.generate_key()
    _cipher_suite = Fernet(FERNET_KEY)
    return _cipher_suite.encrypt(api_key.encode()).decode()


def decrypt_api_key(encrypted: str) -> str:
    """Decrypt an API key from a token (legacy method)."""
    from cryptography.fernet import Fernet
    FERNET_KEY = Fernet.generate_key()
    _cipher_suite = Fernet(FERNET_KEY)
    return _cipher_suite.decrypt(encrypted.encode()).decode()


def generate_token(client_id: str, api_key: str, expiry: int = 3600) -> OAuthToken:
    """Generate an OAuth access token (legacy method)."""
    # Use the new JWT-based method and retain the API-key mapping for verification.
    GLOBAL_API_KEY_STORE[client_id] = api_key
    access_token = generate_jwt_token(client_id, api_key, expiry)
    return OAuthToken(
        access_token=access_token,
        token_type="Bearer",
        expires_in=expiry,
        scope="iati:read",
        client_id=client_id,
        created_at=time.time()
    )


def verify_token(token: str) -> tuple[str, str]:
    """Verify an OAuth access token and extract the API key (legacy method)."""
    # Create a temporary OAuth server for verification
    oauth_server = OAuthServer()
    return oauth_server.verify_token(token)
