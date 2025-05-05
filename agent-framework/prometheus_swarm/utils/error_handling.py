"""Comprehensive error handling utilities."""

import functools
import logging
import traceback
import sys
from typing import Any, Callable, Dict, Optional

from .logging import logger, log_error

class BasePrometheusError(Exception):
    """Base error for Prometheus Swarm framework."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Initialize a base error with context.

        Args:
            message: Error description
            context: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.context = context or {}
        if 'error_message' not in self.context:
            self.context['error_message'] = message

    def __str__(self):
        """Enhanced string representation with context."""
        base_str = super().__str__()
        context_keys = sorted(key for key in self.context.keys() if key != 'error_message')
        context_str = " | ".join(f"{k}: {self.context[k]}" for k in context_keys)
        return f"{base_str} (Context: {context_str})" if context_str else base_str

class ConfigurationError(BasePrometheusError):
    """Raised when configuration is invalid or missing."""
    pass

class AuthenticationError(BasePrometheusError):
    """Raised when authentication fails."""
    pass

class ResourceNotFoundError(BasePrometheusError):
    """Raised when a requested resource is not found."""
    pass

class NetworkError(BasePrometheusError):
    """Raised for network-related issues."""
    pass

def handle_and_log_errors(
    logger_func=logger.error,
    default_error_type: type = BasePrometheusError
):
    """
    Decorator for comprehensive error handling and logging.

    Args:
        logger_func: Logging function to use (default: logger.error)
        default_error_type: Default error type to raise if not specified
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Determine error context
                context = {
                    'function': func.__name__,
                    'module': func.__module__.split('.')[-1],  # Strip package names
                    'args': str(args),
                    'kwargs': str(kwargs)
                }

                # Log the full error with context
                log_error(e, func.__name__, include_traceback=True)

                # If the error is already a BasePrometheusError, re-raise it
                if isinstance(e, BasePrometheusError):
                    raise

                # Convert to a default error type if not already a BasePrometheusError
                if not isinstance(e, BasePrometheusError):
                    detailed_message = f"{type(e).__name__}: {str(e)}"
                    error = default_error_type(detailed_message, context)
                    raise error from e

        return wrapper
    return decorator

def retry_on_error(
    max_attempts: int = 3,
    allowed_exceptions: tuple = (BaseException,),
    delay: int = 1
):
    """
    Decorator to retry a function with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        allowed_exceptions: Tuple of exceptions to catch and retry
        delay: Base delay between retries in seconds
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        log_error(e, f"Max retry attempts ({max_attempts}) exceeded", include_traceback=True)
                        raise RuntimeError(f"Function {func.__name__} failed after {max_attempts} attempts") from e

                    wait_time = delay * (2 ** attempts)
                    logger.warning(
                        f"Attempt {attempts}/{max_attempts} failed. "
                        f"Retrying in {wait_time} seconds."
                    )
                    
                    import time
                    time.sleep(wait_time)

            raise RuntimeError(f"Function {func.__name__} failed after {max_attempts} attempts")
        return wrapper
    return decorator