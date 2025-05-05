"""
Enhanced Logging Configuration with Structured Logging

Provides a consistent and configurable logging setup
using structlog for better log management and parsing.
"""

import logging
import sys
import structlog
from typing import Any, Dict

def configure_logging(
    log_level: str = "INFO", 
    use_json: bool = False
) -> structlog.BoundLogger:
    """
    Configure logging with flexible options.
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json (bool): Whether to output logs in JSON format
    
    Returns:
        structlog.BoundLogger: Configured logger
    """
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
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

    # Create and return a logger
    return structlog.get_logger()

def log_with_context(
    logger: structlog.BoundLogger, 
    context: Dict[str, Any]
) -> structlog.BoundLogger:
    """
    Add context to an existing logger.
    
    Args:
        logger (structlog.BoundLogger): Base logger
        context (Dict[str, Any]): Context to add to logs
    
    Returns:
        structlog.BoundLogger: Logger with added context
    """
    return logger.bind(**context)