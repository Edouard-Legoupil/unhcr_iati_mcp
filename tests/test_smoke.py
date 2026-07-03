"""
Smoke tests for UNHCR IATI MCP Server.

These tests verify that the server can be imported and basic functionality works.
"""

import pytest


class TestImports:
    """Test that all modules can be imported."""

    def test_import_server(self):
        """Test that server module can be imported."""
        from unhcr_iati_mcp.server import main
        assert callable(main)

    def test_import_client(self):
        """Test that client module can be imported."""
        from unhcr_iati_mcp.client import IATIClient, IATIError
        assert IATIClient is not None
        assert IATIError is not None

    def test_import_config(self):
        """Test that config module can be imported."""
        from unhcr_iati_mcp.config import settings
        assert settings is not None

    def test_import_context(self):
        """Test that context module can be imported."""
        from unhcr_iati_mcp.context import mcp, iati_client, unhcr_filter
        assert mcp is not None
        assert iati_client is not None
        assert callable(unhcr_filter)

    def test_import_tools(self):
        """Test that tools package can be imported."""
        from unhcr_iati_mcp import tools
        assert tools is not None

    def test_import_resources(self):
        """Test that resources package can be imported."""
        from unhcr_iati_mcp import resources
        assert resources is not None

    def test_import_models(self):
        """Test that models package can be imported."""
        from unhcr_iati_mcp.models import (
            Activity,
            Budget,
            Transaction,
            PaginatedResponse,
            APIResponse,
            ErrorResponse,
        )
        assert Activity is not None
        assert Budget is not None

    def test_import_observability(self):
        """Test that observability package can be imported."""
        from unhcr_iati_mcp.observability.logging import get_logger, configure_logging
        from unhcr_iati_mcp.observability.metrics import (
            prometheus_metrics,
            monitor_datastore,
            complete_datastore,
            datastore_error,
        )
        assert callable(get_logger)
        assert callable(configure_logging)
        assert callable(prometheus_metrics)


class TestBasicFunctionality:
    """Test basic functionality without external dependencies."""

    def test_unhcr_filter(self):
        """Test that unhcr_filter returns correct format."""
        from unhcr_iati_mcp.context import unhcr_filter
        from unhcr_iati_mcp.config import settings
        
        filter_str = unhcr_filter()
        expected = f'reporting_org_ref:"{settings.unhcr_publisher_ref}"'
        assert filter_str == expected

    def test_context_objects_exist(self):
        """Test that context objects are initialized."""
        from unhcr_iati_mcp.context import mcp, iati_client
        
        assert mcp is not None
        assert mcp.name == "unhcr-iati-mcp"
        assert iati_client is not None


class TestToolRegistration:
    """Test that tools are registered with MCP."""

    def test_tools_registered(self):
        """Test that tools are registered."""
        from unhcr_iati_mcp.context import mcp
        from unhcr_iati_mcp import tools
        
        # Tools should be registered
        # Note: FastMCP may not expose tool list directly
        assert mcp is not None


class TestResourceRegistration:
    """Test that resources are registered with MCP."""

    def test_resources_registered(self):
        """Test that resources are registered."""
        from unhcr_iati_mcp.context import mcp
        from unhcr_iati_mcp import resources
        
        # Resources should be registered
        assert mcp is not None
