"""
Pytest configuration and fixtures for UNHCR IATI MCP Server tests.
"""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Set test environment variables
os.environ["IATI_API_KEY"] = "test-api-key"
os.environ["IATI_BASE_URL"] = "https://api.iatistandard.org/datastore"
os.environ["UNHCR_PUBLISHER_REF"] = "XM-DAC-41121"


@pytest.fixture
def mock_httpx_get():
    """Fixture for mocking httpx.AsyncClient.get method."""
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        # Default mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": {
                "numFound": 5,
                "docs": [
                    {"iati_identifier": "1", "title_narrative": ["Test Activity"]},
                    {"iati_identifier": "2", "title_narrative": ["Test Activity 2"]},
                ]
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def mock_httpx_get_error():
    """Fixture for mocking httpx errors."""
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        yield mock_get


@pytest.fixture
def mock_httpx_get_timeout():
    """Fixture for mocking timeout errors."""
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        import httpx
        mock_get.side_effect = httpx.TimeoutException("Request timed out")
        yield mock_get


@pytest.fixture
def mock_httpx_get_auth_error():
    """Fixture for mocking authentication errors."""
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def mock_httpx_get_rate_limit():
    """Fixture for mocking rate limit errors."""
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def mock_httpx_get_server_error():
    """Fixture for mocking server errors."""
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response
        yield mock_get
