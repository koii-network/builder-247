"""Enhanced logging configuration and utilities for Prometheus Swarm."""

import logging
import sys
import json
import traceback
from typing import Any, Dict, Optional
from pathlib import Path
from functools import wraps
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama for cross-platform color support
init(strip=False)  # Force color output even when not in a terminal

# Logging levels with custom attributes
TRACE = 5  # Lower than DEBUG
logging.addLevelName(TRACE, "TRACE")

class EnhancedLogger(logging.Logger):
    """
    Enhanced logger with additional methods and structured logging support.
    """

    def trace(self, msg, *args, **kwargs):
        """Log trace-level message."""
        return self.log(TRACE, msg, *args, **kwargs)

    def log_json(self, level, data: Dict[str, Any], **kwargs):
        """Log structured JSON data."""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": logging.getLevelName(level),
                **data
            }
            self.log(level, json.dumps(log_entry), **kwargs)
        except Exception as e:
            self.error(f"Failed to log JSON: {e}")

class ColoredFormatter(logging.Formatter):
    """Custom log formatter with color support."""

    COLORS = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
        TRACE: Fore.CYAN
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, Fore.WHITE)
        record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)

def configure_logging(
    log_level: int = logging.INFO,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configure a comprehensive logging system.

    Args:
        log_level: Minimum log level (default: INFO)
        log_file: Optional file path for logging

    Returns:
        Configured logger instance
    """
    # Custom logger class
    logging.setLoggerClass(EnhancedLogger)

    # Create logger
    logger = logging.getLogger('prometheus_swarm')
    logger.setLevel(log_level)

    # Clear existing handlers
    logger.handlers.clear()

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = ColoredFormatter(
        '%(asctime)s | %(levelname)8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File Handler (if specified)
    if log_file:
        try:
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                log_file, 
                maxBytes=10*1024*1024,  # 10 MB
                backupCount=5
            )
            file_handler.setLevel(log_level)
            file_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)8s | %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.error(f"Could not set up file logging: {e}")

    return logger

def log_exception(
    logger: logging.Logger,
    exception: Exception,
    context: Optional[Dict[str, Any]] = None
):
    """
    Standardized exception logging.

    Args:
        logger: Logger instance
        exception: Exception to log
        context: Optional context dictionary
    """
    context = context or {}
    log_data = {
        "exception_type": type(exception).__name__,
        "message": str(exception),
        "traceback": traceback.format_exc(),
        **context
    }
    logger.log_json(logging.ERROR, log_data)

def performance_log(func):
    """
    Performance logging decorator.
    Tracks execution time and logs performance metrics.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        import time
        logger = logging.getLogger('prometheus_swarm')
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.log_json(logging.INFO, {
                "event": "function_performance",
                "function": func.__name__,
                "execution_time_ms": execution_time * 1000
            })
            
            return result
        
        except Exception as e:
            execution_time = time.time() - start_time
            logger.log_json(logging.ERROR, {
                "event": "function_performance_error",
                "function": func.__name__,
                "execution_time_ms": execution_time * 1000,
                "error": str(e)
            })
            raise
    
    return wrapper