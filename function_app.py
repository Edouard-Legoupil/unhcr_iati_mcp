"""
Azure Functions v4 Entry Point for UNHCR IATI MCP Server.

This module serves as the entry point for Azure Functions v4.
It imports and exposes the FunctionApp from the azure.host module.
"""
import os
import sys

## Set python path to include the src directory for module resolution
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "src")
)


# Import the FunctionApp from azure.host
from unhcr_iati_mcp.azure.host import app

# The FunctionApp instance is already created in azure.host
# Azure Functions v4 will automatically discover it
