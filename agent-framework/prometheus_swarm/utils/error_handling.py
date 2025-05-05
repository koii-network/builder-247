"""Comprehensive Error Handling and Logging Module.

This module provides advanced error handling utilities, custom exception types,
and enhanced logging capabilities for robust error tracking and debugging.
"""

import functools
import logging
import traceback
import sys
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union

from .logging import logger, log_error, configure_logging

T = TypeVar('T')

class BaseCustomError(Exception):
    """Base class for custom exceptions with enhanced error tracking."""

    def __init__(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None, 
        original_error: Optional[Exception] = None
    ):
        """
        Initialize a custom error with context and optional original error.

        Args:
            message (str): Error message
            context (dict, optional): Additional context about the error
            original_error (Exception, optional): Original exception that triggered this error
        """
        super().__init__(message)
        self.context = context or {}
        self.original_error = original_error
        self.context['error_type'] = self.__class__.__name__

    def __str__(self) -> str:
        """Provide a detailed string representation of the error."""
        error_str = f"{self.__class__.__name__}: {super().__str__()}"
        if self.context:
            error_str += f"\nContext: {self.context}"
        return error_str

class ValidationError(BaseCustomError):
    """Error raised for input validation failures."""
    pass

class ConfigurationError(BaseCustomError):
    """Error raised for configuration-related issues."""
    pass

class ExternalServiceError(BaseCustomError):
    """Error raised for failures in external service calls."""
    pass

def retry(
    max_attempts: int = 3, 
    exceptions: Union[Type[Exception], tuple[Type[Exception], ...]] = Exception,
    delay: Union[int, float] = 1, 
    backoff_factor: float = 2
) -> Callable:
    """
    Decorator for retrying a function in case of specified exceptions.

    Args:
        max_attempts (int): Maximum number of retry attempts
        exceptions (Exception or tuple): Exception type(s) to catch and retry
        delay (int/float): Initial delay between retries in seconds
        backoff_factor (float): Multiplicative factor for increasing delay
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            current_attempt = 0
            current_delay = delay

            while current_attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    current_attempt += 1
                    log_error(
                        e, 
                        context=f"Retry {current_attempt}/{max_attempts} for {func.__name__}"
                    )

                    if current_attempt == max_attempts:
                        raise

                    import time
                    time.sleep(current_delay)
                    current_delay *= backoff_factor

            raise RuntimeError(f"Failed after {max_attempts} attempts")
        return wrapper
    return decorator

def handle_errors(
    log_context: Optional[str] = None,
    fallback_return: Any = None,
    raise_on_error: bool = True
) -> Callable:
    """
    Decorator for comprehensive error handling and logging.

    Args:
        log_context (str, optional): Custom context for logging
        fallback_return (Any, optional): Value to return if error occurs and raise_on_error is False
        raise_on_error (bool): Whether to re-raise caught exceptions
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Ensure logging is configured
            configure_logging()

            context_name = log_context or func.__name__
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log the error with traceback
                log_error(e, context=context_name)

                # Convert to custom error type with context
                error_context = {
                    'function': func.__name__,
                    'module': func.__module__,
                    'args': str(args),
                    'kwargs': str(kwargs)
                }
                custom_error = BaseCustomError(
                    message=str(e), 
                    context=error_context,
                    original_error=e
                )

                # Raise or return fallback based on configuration
                if raise_on_error:
                    raise custom_error
                else:
                    logger.warning(f"Error suppressed: {custom_error}")
                    return fallback_return

        return wrapper
    return decorator

def handle_context_errors(context_extractor: Callable[[Any], Dict[str, Any]]):
    """
    Advanced error handler that dynamically extracts context from function arguments.

    Args:
        context_extractor (Callable): Function to extract context from arguments
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            configure_logging()
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Extract dynamic context
                try:
                    error_context = context_extractor(*args, **kwargs)
                except Exception as context_err:
                    error_context = {
                        'context_extraction_error': str(context_err)
                    }

                # Annotate with function details
                error_context.update({
                    'function': func.__name__,
                    'module': func.__module__
                })

                # Log and raise custom error
                log_error(e, context=func.__name__)
                
                custom_error = BaseCustomError(
                    message=str(e), 
                    context=error_context,
                    original_error=e
                )
                raise custom_error

        return wrapper
    return decorator