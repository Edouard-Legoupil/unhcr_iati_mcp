"""
Tests for UNHCR IATI MCP Server tools.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from unhcr_iati_mcp.context import mcp, iati_client, unhcr_filter


class TestActivityTools:
    """Tests for activity-related tools."""

    @pytest.mark.asyncio
    async def test_unhcr_activities(self, mock_httpx_get):
        """Test unhcr_activities tool."""
        from unhcr_iati_mcp.tools.activities import unhcr_activities
        
        result = await unhcr_activities(rows=10, start=0)
        
        assert isinstance(result, dict)
        assert "response" in result

    @pytest.mark.asyncio
    async def test_unhcr_activity(self, mock_httpx_get):
        """Test unhcr_activity tool."""
        from unhcr_iati_mcp.tools.activities import unhcr_activity
        
        result = await unhcr_activity(iati_identifier="test-id")
        
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_unhcr_activity_by_country(self, mock_httpx_get):
        """Test unhcr_activity_by_country tool."""
        from unhcr_iati_mcp.tools.activities import unhcr_activity_by_country
        
        result = await unhcr_activity_by_country(country_code="AFG", rows=10)
        
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_unhcr_activity_by_sector(self, mock_httpx_get):
        """Test unhcr_activity_by_sector tool."""
        from unhcr_iati_mcp.tools.activities import unhcr_activity_by_sector
        
        result = await unhcr_activity_by_sector(sector_code="1", rows=10)
        
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_unhcr_activity_by_year(self, mock_httpx_get):
        """Test unhcr_activity_by_year tool."""
        from unhcr_iati_mcp.tools.activities import unhcr_activity_by_year
        
        result = await unhcr_activity_by_year(year=2024)
        
        assert isinstance(result, list)


class TestDonorTools:
    """Tests for donor-related tools."""

    @pytest.mark.asyncio
    async def test_unhcr_top_donors(self, mock_httpx_get):
        """Test unhcr_top_donors tool."""
        from unhcr_iati_mcp.tools.donors import unhcr_top_donors
        
        # Mock transaction data with donor information
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": {
                "numFound": 2,
                "docs": [
                    {
                        "transaction_provider_org_narrative": ["Donor A"],
                        "transaction_value": [1000.0]
                    },
                    {
                        "transaction_provider_org_narrative": ["Donor B"],
                        "transaction_value": [2000.0]
                    },
                ]
            }
        }
        mock_response.raise_for_status = MagicMock()
        
        with patch("httpx.AsyncClient.get", return_value=mock_response) as mock_get:
            result = await unhcr_top_donors(top_n=10)
            
            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0][0] == "Donor B"  # Highest amount first


class TestCountryTools:
    """Tests for country-related tools."""

    @pytest.mark.asyncio
    async def test_unhcr_top_countries(self, mock_httpx_get):
        """Test unhcr_top_countries tool."""
        from unhcr_iati_mcp.tools.countries import unhcr_top_countries
        
        # Mock activity data with country codes
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": {
                "numFound": 2,
                "docs": [
                    {"recipient_country_code": ["AFG", "SYR"]},
                    {"recipient_country_code": ["AFG"]},
                ]
            }
        }
        mock_response.raise_for_status = MagicMock()
        
        with patch("httpx.AsyncClient.get", return_value=mock_response) as mock_get:
            result = await unhcr_top_countries(top_n=10)
            
            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0][0] == "AFG"  # Most common first


class TestSectorTools:
    """Tests for sector-related tools."""

    @pytest.mark.asyncio
    async def test_unhcr_sector_summary(self, mock_httpx_get):
        """Test unhcr_sector_summary tool."""
        from unhcr_iati_mcp.tools.sectors import unhcr_sector_summary
        
        # Mock activity data with sector codes
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": {
                "numFound": 2,
                "docs": [
                    {"sector_code": ["1", "2"]},
                    {"sector_code": ["1"]},
                ]
            }
        }
        mock_response.raise_for_status = MagicMock()
        
        with patch("httpx.AsyncClient.get", return_value=mock_response) as mock_get:
            result = await unhcr_sector_summary()
            
            assert isinstance(result, dict)
            assert "1" in result
            assert result["1"] == 2


class TestTransactionTools:
    """Tests for transaction-related tools."""

    @pytest.mark.asyncio
    async def test_unhcr_transactions(self, mock_httpx_get):
        """Test unhcr_transactions tool."""
        from unhcr_iati_mcp.tools.transactions import unhcr_transactions
        
        result = await unhcr_transactions(year=2024)
        
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_unhcr_transaction_search(self, mock_httpx_get):
        """Test unhcr_transaction_search tool."""
        from unhcr_iati_mcp.tools.transactions import unhcr_transaction_search
        
        result = await unhcr_transaction_search(query="value:1000")
        
        assert isinstance(result, list)


class TestBudgetTools:
    """Tests for budget-related tools."""

    @pytest.mark.asyncio
    async def test_unhcr_budgets(self, mock_httpx_get):
        """Test unhcr_budgets tool."""
        from unhcr_iati_mcp.tools.budgets import unhcr_budgets
        
        result = await unhcr_budgets(year=2024)
        
        assert isinstance(result, list)


class TestAnalyticsTools:
    """Tests for analytics tools."""

    @pytest.mark.asyncio
    async def test_unhcr_portfolio_summary(self, mock_httpx_get):
        """Test unhcr_portfolio_summary tool."""
        from unhcr_iati_mcp.tools.analytics import unhcr_portfolio_summary
        
        result = await unhcr_portfolio_summary()
        
        assert isinstance(result, dict)
        assert "activities" in result
        assert "budgets" in result
        assert "transactions" in result


class TestExportTools:
    """Tests for export tools."""

    @pytest.mark.asyncio
    async def test_unhcr_export_json(self, mock_httpx_get):
        """Test unhcr_export_json tool."""
        from unhcr_iati_mcp.tools.export import unhcr_export_json
        import json
        
        result = await unhcr_export_json(collection="activity", query="")
        
        # Should be valid JSON
        parsed = json.loads(result)
        assert isinstance(parsed, list)

    @pytest.mark.asyncio
    async def test_unhcr_export_csv(self, mock_httpx_get):
        """Test unhcr_export_csv tool."""
        from unhcr_iati_mcp.tools.export import unhcr_export_csv
        
        result = await unhcr_export_csv(collection="activity", query="")
        
        # Should contain CSV headers
        assert "iati_identifier" in result or len(result) > 0


class TestHealthTools:
    """Tests for health check tools."""

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health_check tool."""
        from unhcr_iati_mcp.tools.health import health_check
        
        result = await health_check()
        
        assert result["status"] == "healthy"
        assert result["service"] == "UNHCR IATI MCP"

    @pytest.mark.asyncio
    async def test_system_status(self):
        """Test system_status tool."""
        from unhcr_iati_mcp.tools.health import system_status
        
        result = await system_status()
        
        assert result["api"] == "up"

    @pytest.mark.asyncio
    async def test_datastore_ping(self, mock_httpx_get):
        """Test datastore_ping tool."""
        from unhcr_iati_mcp.tools.health import datastore_ping
        
        result = await datastore_ping()
        
        assert result["status"] == "up"
        assert result["service"] == "Datastore"

    @pytest.mark.asyncio
    async def test_api_limits(self):
        """Test api_limits tool."""
        from unhcr_iati_mcp.tools.health import api_limits
        
        result = await api_limits()
        
        assert "rate_limit" in result
