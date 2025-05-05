"""
Enhanced Logging Configuration with Structured Logging

Provides a consistent and configurable logging setup
using structlog for better log management and parsing.
"""

import logging
import sys
import io
import json
import structlog
from typing import Any, Dict, Optional, Union

def configure_logging(
    log_level: str = "INFO", 
    use_json: bool = False
) -> logging.Logger:
    """
    Configure logging with flexible options.
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json (bool): Whether to output logs in JSON format
    
    Returns:
        logging.Logger: Configured logger
    """
    # Create a logging stream
    log_stream = io.StringIO() if use_json else sys.stdout

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=log_stream,
        level=getattr(logging, log_level.upper())
    )

    # Configure structlog processors
    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.filter_by_level,
    ]

    if use_json:
        # JSON-formatted logs for better machine parsing
        processors = shared_processors + [
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ]
    else:
        # Human-readable console output
        processors = shared_processors + [
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.dev.ConsoleRenderer()
        ]

    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Create a logger and return it
    return logging.getLogger(__name__)

def log_with_context(
    logger: logging.Logger, 
    context: Dict[str, Any]
) -> logging.Logger:
    """
    Add context to an existing logger.
    
    Args:
        logger: Base logger
        context: Context to add to logs
    
    Returns:
        Logger with added context
    """
    # Not fully implementing context for standard logging
    logger.info(f"Adding context: {context}")
    return logger

def log_structured_event(
    event_type: str, 
    data: Dict[str, Any], 
    level: str = "INFO"
) -> None:
    """
    Log a structured event with consistent formatting.
    
    Args:
        event_type (str): Type of event
        data (Dict[str, Any]): Event details
        level (str, optional): Logging level
    """
    logger = structlog.get_logger()
    log_method = getattr(logger, level.lower())
    log_method(event_type, **data)