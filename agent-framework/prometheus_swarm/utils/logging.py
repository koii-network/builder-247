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
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

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
        console_handler.setFormatter(logging.Formatter(log_format))
        self.logger.addHandler(console_handler)

        # Optional file logging
        if file_logging:
            self._setup_file_logging()

    def _setup_file_logging(self):
        """Set up file logging with rotation."""
        log_dir = _get_log_directory()
        log_filename = f"{datetime.now().strftime('%Y%m%d')}_prometheus.log"
        log_path = log_dir / log_filename

        # Timed rotating file handler (daily rotation)
        file_handler = TimedRotatingFileHandler(
            filename=log_path,
            when='midnight',
            interval=1,
            backupCount=10,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
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

            # Attempt to log as JSON if possible
            try:
                detailed_message = json.dumps(log_data, indent=2)
            except (TypeError, ValueError):
                detailed_message = str(log_data)

            self.logger.log(level, detailed_message)
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
        self.log(logging.ERROR, message, exc_info=True, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.log(logging.CRITICAL, message, exc_info=True, **kwargs)


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