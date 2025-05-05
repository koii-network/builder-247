"""Enhanced logging configuration and utilities."""

import logging
import sys
import traceback
from typing import Any, Dict, Optional
from pathlib import Path
from functools import wraps
import ast
import json
from colorama import init, Fore, Style

from .errors import PrometheusBaseError, ErrorSeverity

# Initialize colorama for cross-platform color support
init(strip=False)  # Force color output even when not in a terminal

# Track if logging has been configured
_logging_configured = False

def configure_logging(
    log_level: int = logging.INFO, 
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configures a centralized logging system with console and optional file output.
    
    Args:
        log_level: Logging level (default: INFO)
        log_file: Optional file path for log storage
    
    Returns:
        Configured logger instance
    """
    global _logging_configured
    
    # Create logger
    logger = logging.getLogger("prometheus")
    logger.setLevel(log_level)
    logger.propagate = False
    
    # Prevent reconfiguration
    if _logging_configured:
        return logger
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler with color support
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = ColoredFormatter()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Optional file logging
    if log_file:
        try:
            from logging.handlers import RotatingFileHandler
            
            # Ensure log directory exists
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = RotatingFileHandler(
                log_file, 
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(log_level)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
    
    _logging_configured = True
    return logger

class ColoredFormatter(logging.Formatter):
    """
    Custom colored log formatter with advanced display features.
    """
    COLORS = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA
    }
    
    def format(self, record):
        # Colorize log level
        log_color = self.COLORS.get(record.levelno, Fore.WHITE)
        record.levelname = f"{log_color}{record.levelname}{Style.RESET_ALL}"
        
        # Format message
        message = super().format(record)
        
        return message

def log_error(
    error: Exception, 
    context: Optional[Dict[str, Any]] = None, 
    logger: Optional[logging.Logger] = None
) -> None:
    """
    Comprehensive error logging with extended details.
    
    Args:
        error: The exception to log
        context: Optional additional context dictionary
        logger: Optional logger to use (defaults to root logger)
    """
    logger = logger or logging.getLogger('prometheus')
    
    # Determine error properties
    if isinstance(error, PrometheusBaseError):
        severity = error.severity.name
        details = error.context
    else:
        severity = 'UNKNOWN'
        details = {}
    
    # Merge provided context with error context
    details.update(context or {})
    
    # Log error details
    logger.error(f"Error Severity: {severity}")
    logger.error(f"Error Message: {str(error)}")
    
    # Log additional context
    if details:
        logger.error("Error Context:")
        for key, value in details.items():
            logger.error(f"  {key}: {value}")
    
    # Log stack trace
    logger.error("Stack Trace:")
    for line in traceback.format_exc().splitlines():
        logger.error(line)

def log_structured(
    message: str, 
    level: int = logging.INFO, 
    data: Optional[Dict[str, Any]] = None,
    logger: Optional[logging.Logger] = None
) -> None:
    """
    Log a structured message with optional data.
    
    Args:
        message: Primary log message
        level: Logging level
        data: Optional structured data
        logger: Optional logger to use
    """
    logger = logger or logging.getLogger('prometheus')
    
    # Prepare log message
    log_entry = {"message": message}
    
    # Add structured data
    if data:
        log_entry.update(data)
    
    # Log as JSON for easier parsing
    logger.log(level, json.dumps(log_entry))

def performance_log(func):
    """
    Decorator to log function performance metrics.
    
    Args:
        func: Function to be monitored
    
    Returns:
        Wrapped function with performance logging
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        import time
        
        logger = logging.getLogger('prometheus')
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            
            # Log performance metrics
            execution_time = time.time() - start_time
            log_structured(
                f"Function Performance: {func.__name__}",
                data={
                    "function": func.__name__,
                    "execution_time_seconds": execution_time,
                    "module": func.__module__
                },
                logger=logger
            )
            
            return result
        
        except Exception as e:
            execution_time = time.time() - start_time
            log_error(
                e, 
                context={
                    "function": func.__name__,
                    "execution_time_seconds": execution_time
                },
                logger=logger
            )
            raise
    
    return wrapper

# Default logger configuration
logger = configure_logging()