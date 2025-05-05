"""Comprehensive error handling utilities for the agent framework."""

import traceback
import functools
from typing import Any, Callable, Optional, Type, Union


class PrometheusBaseError(Exception):
    """Base error class for all Prometheus framework errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        context: Optional[dict] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize a Prometheus base error.

        Args:
            message: Descriptive error message
            error_code: Unique error code for identification
            context: Additional context about the error
            original_error: The original exception that triggered this error
        """
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.original_error = original_error

        # Combine error details for a comprehensive error representation
        error_details = [
            f"Error Code: {self.error_code}",
            f"Message: {self.message}"
        ]
        if self.context:
            error_details.append(f"Context: {self.context}")
        
        # Include original error details if available
        if original_error:
            error_details.append(f"Original Error: {str(original_error)}")
            error_details.append(f"Traceback:\n{traceback.format_exc()}")

        super().__init__("\n".join(error_details))


class ClientAPIError(PrometheusBaseError):
    """Error for API calls with detailed status information."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "API_ERROR",
        context: Optional[dict] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize a Client API Error.

        Args:
            message: Descriptive error message
            status_code: HTTP status code
            error_code: Unique error code
            context: Additional context about the error
            original_error: The original exception
        """
        self.status_code = status_code
        super().__init__(
            message=message,
            error_code=error_code,
            context=context or {},
            original_error=original_error
        )


class ConfigurationError(PrometheusBaseError):
    """Error related to configuration and environment setup."""
    def __init__(
        self,
        message: str,
        context: Optional[dict] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            error_code="CONFIG_ERROR",
            context=context,
            original_error=original_error
        )


def handle_and_log_error(
    logger_func=None,
    error_type: Type[PrometheusBaseError] = PrometheusBaseError,
    context: Optional[dict] = None
):
    """
    Decorator to handle and log errors with consistent formatting.

    Args:
        logger_func: Optional custom logging function
        error_type: Custom error type to raise
        context: Additional context for the error

    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., Any]):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Default context if not provided
                error_context = context or {}
                error_context.update({
                    "function": func.__name__,
                    "module": func.__module__
                })

                # Create custom error
                custom_error = error_type(
                    message=str(e),
                    context=error_context,
                    original_error=e
                )

                # Log the error if logger is available
                if logger_func:
                    logger_func(custom_error)

                # Re-raise the custom error
                raise custom_error from e
        return wrapper
    return decorator


def safe_execute(
    func: Callable[..., Any],
    default_return: Any = None,
    error_handler: Optional[Callable[[Exception], None]] = None
) -> Union[Any, None]:
    """
    Execute a function safely with optional error handling.

    Args:
        func: Function to execute
        default_return: Default return value if function fails
        error_handler: Optional custom error handling function

    Returns:
        Function result or default_return
    """
    try:
        return func()
    except Exception as e:
        if error_handler:
            error_handler(e)
        return default_return