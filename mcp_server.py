#!/usr/bin/env python3
"""
Entry point for UNHCR IATI MCP Server.

This script is designed to be used with Vibe's MCP server configuration.
It sets up the correct Python path and runs the FastMCP server in stdio mode.
"""

import sys
import asyncio
import os
from pathlib import Path

# Change to the project root directory to ensure .env file is found
# and paths are resolved correctly
project_root = Path(__file__).parent
os.chdir(project_root)

# Explicitly load environment variables from .env file
env_path = project_root / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

# Add the src directory to Python path to ensure we use the local package
# This takes precedence over any other installed unhcr_mcp packages
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Now import and run the server
from unhcr_iati_mcp.server import app


async def main():
    """Run the MCP server in stdio mode."""
    await app.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())