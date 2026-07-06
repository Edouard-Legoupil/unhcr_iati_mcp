from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

import structlog


def configure_logging(
    level: str = "INFO",
    log_dir: Optional[str] = None,
    log_file: Optional[str] = None,
) -> None:
    """
    Configure application-wide logging.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to save log files. If None, uses settings.log_dir or 'logs'
        log_file: Log file path. If None, auto-generates based on timestamp
    """
    # Import settings but handle circular imports
    try:
        from unhcr_iati_mcp.config import settings
        if log_dir is None:
            log_dir = settings.log_dir
        if log_file is None:
            log_file = settings.log_file
    except ImportError:
        pass
    
    # Set up log directory
    if log_dir is None:
        log_dir = Path("logs")
    else:
        log_dir = Path(log_dir)
    
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Set up log file
    if log_file is None:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"unhcr_iati_mcp_{timestamp}.log"
    else:
        log_file = Path(log_file)
    
    # Configure file handler
    file_handler = logging.FileHandler(
        filename=str(log_file),
        mode='a',
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, level.upper()))
    
    # Configure console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(
                fmt="iso",
                utc=True,
            ),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper())
        ),
        cache_logger_on_first_use=True,
        logger_factory=structlog.PrintLoggerFactory(file=file_handler.stream),
    )
    
    # Log startup information
    logger = get_logger(__name__)
    logger.info(
        "Logging configured",
        log_level=level,
        log_file=str(log_file),
        log_dir=str(log_dir)
    )


def get_logger(name: str):
    return structlog.get_logger(name)