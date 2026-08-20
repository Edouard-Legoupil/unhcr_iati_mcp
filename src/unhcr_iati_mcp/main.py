"""
Main entry point for UNHCR Refugee Data Portal MCP Server.

Provides CLI commands for running the server and testing connectivity.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

import uvicorn

from .server import app, get_server
from .config import settings
from .client import IATIClient as UNHCRClient
from .client import IATIError as UNHCRBaseException

logger = logging.getLogger(__name__)


def setup_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """Configure logging for the application."""
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    if log_format == "json":
        try:
            import json_logging
            json_logging.init_non_web()
            handler = logging.StreamHandler()
            handler.setFormatter(json_logging.JSONFormatter())
            logging.getLogger().handlers.clear()
            logging.getLogger().addHandler(handler)
        except ImportError:
            # Fall back to text logging if json_logging not available
            logging.basicConfig(
                level=level,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
    else:
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(level)
    logging.getLogger("aiohttp").setLevel(level)


async def test_connection() -> bool:
    """Test connection to UNHCR API."""
    try:
        client = UNHCRClient()
        async with client:
            # Test health endpoint
            health = await client.get_health()
            logger.info(f"Connection test successful: {health.get('status', 'unknown')}")
            return True
    except UNHCRBaseException as e:
        logger.error(f"Connection test failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during connection test: {e}")
        return False


async def list_tools() -> None:
    """List all available MCP tools."""
    server = get_server()
    mcp_app = server.create_app()
    
    print("Available UNHCR IATI MCP Tools:")
    print("=" * 50)
    
    # Get all registered tools
    tools = []
    for route in mcp_app.routes:
        if hasattr(route, 'endpoint') and hasattr(route.endpoint, '__name__'):
            tools.append(route.endpoint.__name__)
    
    # Sort and display
    for tool_name in sorted(set(tools)):
        if not tool_name.startswith('_'):
            print(f"  - {tool_name}")
    
    print(f"\nTotal: {len(tools)} tools")


async def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    log_level: str = "info",
) -> None:
    """Run the MCP server using Uvicorn."""
    setup_logging(log_level.upper(), settings.LOG_FORMAT)
    
    logger.info(f"Starting UNHCR IATI MCP Server on {host}:{port}")
    logger.info(f"API Base URL: {settings.get_api_base_url()}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Configure Uvicorn
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        access_log=True,
    )
    
    server = uvicorn.Server(config)
    
    try:
        await server.serve()
    except KeyboardInterrupt:
        logger.info("Server shutdown by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="UNHCR IATI MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
        # Run the server
        python -m unhcr_mcp.main run
        
        # Run with custom port
        python -m unhcr_mcp.main run --port 8080
        
        # Test connection
        python -m unhcr_mcp.main test-connection
        
        # List available tools
        python -m unhcr_mcp.main list-tools
        
        # Run with hot reload (development)
        python -m unhcr_mcp.main run --reload
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run the MCP server")
    run_parser.add_argument(
        "--host",
        default=settings.MCP_SERVER_HOST,
        help="Host to bind to (default: 0.0.0.0)",
    )
    run_parser.add_argument(
        "--port",
        type=int,
        default=settings.MCP_SERVER_PORT,
        help="Port to listen on (default: 8000)",
    )
    run_parser.add_argument(
        "--reload",
        action="store_true",
        default=settings.MCP_SERVER_DEBUG,
        help="Enable auto-reload for development",
    )
    run_parser.add_argument(
        "--log-level",
        default=settings.LOG_LEVEL,
        choices=["debug", "info", "warning", "error", "critical"],
        help="Logging level (default: info)",
    )
    
    # Test connection command
    subparsers.add_parser("test-connection", help="Test connection to UNHCR API")
    
    # List tools command
    subparsers.add_parser("list-tools", help="List all available MCP tools")
    
    # Info command
    subparsers.add_parser("info", help="Show server information")
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "run":
        asyncio.run(run_server(
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level,
        ))
    elif args.command == "test-connection":
        success = asyncio.run(test_connection())
        sys.exit(0 if success else 1)
    elif args.command == "list-tools":
        asyncio.run(list_tools())
    elif args.command == "info":
        print(f"UNHCR MCP Server v{settings.MCP_SERVER_VERSION}")
        print(f"Environment: {settings.ENVIRONMENT}")
        print(f"API Base URL: {settings.get_api_base_url()}")
        print(f"Server Host: {settings.MCP_SERVER_HOST}")
        print(f"Server Port: {settings.MCP_SERVER_PORT}")
        print(f"Rate Limit: {settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_PERIOD}s")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
