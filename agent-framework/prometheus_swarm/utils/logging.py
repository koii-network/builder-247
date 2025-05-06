"""Enhanced logging utility with extended features."""

import os
import sys
import json
import logging
import traceback
from typing import Any, Dict, Optional
from pathlib import Path
from functools import wraps
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Default configuration
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def _get_log_directory() -> Path:
    """
    Get or create the log directory.

    Returns:
        Path to the log directory
    """
    log_dir = Path(os.getenv('PROMETHEUS_LOG_DIR', './logs'))
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


class StructuredLogger:
    """Enhanced logger with structured logging capabilities."""

    def __init__(
        self,
        name: str = "prometheus",
        log_level: int = DEFAULT_LOG_LEVEL,
        file_logging: bool = True,
        log_format: str = DEFAULT_LOG_FORMAT
    ):
        """
        Initialize a structured logger.

        Args:
            name: Logger name
            log_level: Logging level
            file_logging: Enable file logging
            log_format: Log message format
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        self.logger.handlers.clear()  # Clear any existing handlers

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # Optional file logging
        if file_logging:
            self._setup_file_logging()

    def _setup_file_logging(self):
        """Set up file logging with rotation."""
        log_dir = _get_log_directory()
        log_filename = f"{datetime.now().strftime('%Y%m%d')}_prometheus.log"
        log_path = log_dir / log_filename

        # Rotating file handler
        file_handler = RotatingFileHandler(
            filename=log_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    def log(
        self,
        level: int,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: bool = False
    ):
        """
        Log a message with optional structured data.

        Args:
            level: Logging level
            message: Log message
            extra: Additional context data
            exc_info: Include exception traceback
        """
        try:
            log_data = {"message": message}
            if extra:
                log_data.update(extra)

            # Add exception info if available
            if exc_info and sys.exc_info()[0]:
                log_data['exception'] = {
                    'type': str(sys.exc_info()[0]),
                    'message': str(sys.exc_info()[1]),
                    'traceback': traceback.format_exc()
                }

            # Log JSON-structured message
            structured_message = json.dumps(log_data, indent=2)
            self.logger.log(level, structured_message)
        except Exception as e:
            print(f"Logging error: {e}", file=sys.stderr)

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message."""
        self.log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message."""
        kwargs['exc_info'] = kwargs.get('exc_info', True)
        self.log(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message."""
        kwargs['exc_info'] = kwargs.get('exc_info', True)
        self.log(logging.CRITICAL, message, **kwargs)


# Global structured logger
logger = StructuredLogger()


def log_execution_time(func):
    """
    Decorator to log function execution time and result.

    Args:
        func: Function to be decorated

    Returns:
        Wrapped function with logging
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        import time
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(
                f"Function {func.__name__} executed successfully",
                extra={
                    "function": func.__name__,
                    "execution_time_ms": round(duration * 1000, 2),
                    "args": str(args),
                    "kwargs": str(kwargs)
                }
            )
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Function {func.__name__} execution failed",
                extra={
                    "function": func.__name__,
                    "execution_time_ms": round(duration * 1000, 2),
                    "exception": str(e)
                }
            )
            raise

    return wrapper