"""
Tests for IATIClient in UNHCR IATI MCP Server.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from unhcr_iati_mcp.client import (
    IATIClient,
    IATIError,
    IATIAuthenticationError,
    IATIRateLimitError,
    IATIServerError,
)


class TestIATIClientQuery:
    """Tests for the query method."""

    @pytest.mark.asyncio
    async def test_query_success(self, mock_httpx_get):
        """Test successful query returns data."""
        client = IATIClient()
        result = await client.query("activity", "*:*", rows=10)
        
        assert result["response"]["numFound"] == 5
        assert len(result["response"]["docs"]) == 2
        await client.close()

    @pytest.mark.asyncio
    async def test_query_with_filter(self, mock_httpx_get):
        """Test query with UNHCR filter."""
        client = IATIClient()
        result = await client.query(
            "activity",
            'reporting_org_ref:"XM-DAC-41121"',
            rows=10
        )
        
        # Verify the request was made with correct params
        assert mock_httpx_get.called
        call_args = mock_httpx_get.call_args
        assert call_args.kwargs["params"]["q"] == 'reporting_org_ref:"XM-DAC-41121"'
        await client.close()

    @pytest.mark.asyncio
    async def test_query_authentication_error(self, mock_httpx_get_auth_error):
        """Test 401 authentication error handling."""
        client = IATIClient()
        
        with pytest.raises(IATIAuthenticationError) as exc_info:
            await client.query("activity", "*:*", rows=10)
        
        assert "Invalid API key" in str(exc_info.value)
        await client.close()

    @pytest.mark.asyncio
    async def test_query_rate_limit_error(self, mock_httpx_get_rate_limit):
        """Test 429 rate limit error handling."""
        client = IATIClient()
        
        with pytest.raises(IATIRateLimitError) as exc_info:
            await client.query("activity", "*:*", rows=10)
        
        assert "Rate limit exceeded" in str(exc_info.value)
        await client.close()

    @pytest.mark.asyncio
    async def test_query_server_error(self, mock_httpx_get_server_error):
        """Test 500 server error handling."""
        client = IATIClient()
        
        with pytest.raises(IATIServerError) as exc_info:
            await client.query("activity", "*:*", rows=10)
        
        assert "Internal Server Error" in str(exc_info.value)
        await client.close()

    @pytest.mark.asyncio
    async def test_query_timeout_error(self, mock_httpx_get_timeout):
        """Test timeout error handling."""
        client = IATIClient()
        
        with pytest.raises(httpx.TimeoutException):
            await client.query("activity", "*:*", rows=10)
        
        await client.close()

    @pytest.mark.asyncio
    async def test_query_malformed_response(self, mock_httpx_get):
        """Test malformed response handling."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"not_response": "invalid"}
        mock_response.raise_for_status = MagicMock()
        mock_httpx_get.return_value = mock_response
        
        client = IATIClient()
        
        with pytest.raises(IATIError) as exc_info:
            await client.query("activity", "*:*", rows=10)
        
        assert "Malformed Datastore response" in str(exc_info.value)
        await client.close()


class TestIATIClientFetchAll:
    """Tests for the fetch_all method."""

    @pytest.mark.asyncio
    async def test_fetch_all_success(self, mock_httpx_get):
        """Test successful fetch_all with pagination."""
        client = IATIClient()
        results = await client.fetch_all("activity", "*:*", max_records=10)
        
        assert isinstance(results, list)
        assert len(results) == 2
        await client.close()

    @pytest.mark.asyncio
    async def test_fetch_all_max_records(self, mock_httpx_get):
        """Test fetch_all with max_records limit."""
        client = IATIClient()
        results = await client.fetch_all("activity", "*:*", max_records=1)
        
        assert len(results) <= 1
        await client.close()


class TestIATIClientConvenienceMethods:
    """Tests for convenience methods."""

    @pytest.mark.asyncio
    async def test_activities(self, mock_httpx_get):
        """Test activities convenience method."""
        client = IATIClient()
        results = await client.activities("*:*")
        
        assert isinstance(results, list)
        assert len(results) == 2
        await client.close()

    @pytest.mark.asyncio
    async def test_transactions(self, mock_httpx_get):
        """Test transactions convenience method."""
        client = IATIClient()
        results = await client.transactions("*:*")
        
        assert isinstance(results, list)
        await client.close()

    @pytest.mark.asyncio
    async def test_budgets(self, mock_httpx_get):
        """Test budgets convenience method."""
        client = IATIClient()
        results = await client.budgets("*:*")
        
        assert isinstance(results, list)
        await client.close()

    @pytest.mark.asyncio
    async def test_fetch_page(self, mock_httpx_get):
        """Test fetch_page method."""
        client = IATIClient()
        result = await client.fetch_page("activity", "*:*", page=0)
        
        assert result["response"]["numFound"] == 5
        await client.close()


class TestIATIClientMetrics:
    """Tests for metrics integration."""

    @pytest.mark.asyncio
    async def test_metrics_imports(self):
        """Test that metrics module can be imported."""
        from unhcr_iati_mcp.observability.metrics import (
            prometheus_metrics,
            monitor_datastore,
            complete_datastore,
            datastore_error,
        )
        assert callable(prometheus_metrics)
        assert callable(monitor_datastore)
        assert callable(complete_datastore)
        assert callable(datastore_error)
