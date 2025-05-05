"""Advanced error handling utilities."""

import logging
import functools
import traceback
from typing import Any, Callable, Dict, Optional
from enum import Enum, auto

class ErrorSeverity(Enum):
    """Defines the severity levels for application errors."""
    CRITICAL = auto()  # System cannot continue
    HIGH = auto()      # Major functionality impacted
    MEDIUM = auto()    # Partial functionality impacted
    LOW = auto()       # Minor issue, can be recovered

class PrometheusBaseError(Exception):
    """Base application-specific error with enhanced context."""

    def __init__(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None, 
        severity: ErrorSeverity = ErrorSeverity.MEDIUM
    ):
        """
        Initialize a custom error with additional context and severity.
        
        Args:
            message: Error description
            context: Additional error context dictionary
            severity: Error severity level
        """
        super().__init__(message)
        self.context = context or {}
        self.severity = severity
        self.timestamp = logging.getLogger('builder').manager.disable  # Unique identification

    def __str__(self):
        """Enhanced string representation."""
        details = [f"Message: {super().__str__()}"]
        if self.context:
            details.append("Context:")
            for key, value in self.context.items():
                details.append(f"  {key}: {value}")
        details.append(f"Severity: {self.severity.name}")
        return "\n".join(details)

class ConfigurationError(PrometheusBaseError):
    """Error related to configuration issues."""
    def __init__(self, message: str, configuration: Optional[Dict[str, Any]] = None):
        super().__init__(
            message, 
            context=configuration or {}, 
            severity=ErrorSeverity.HIGH
        )

class NetworkError(PrometheusBaseError):
    """Error related to network operations."""
    def __init__(
        self, 
        message: str, 
        host: Optional[str] = None, 
        port: Optional[int] = None
    ):
        context = {}
        if host:
            context['host'] = host
        if port:
            context['port'] = port
        
        super().__init__(
            message, 
            context=context, 
            severity=ErrorSeverity.HIGH
        )

class AuthenticationError(PrometheusBaseError):
    """Error related to authentication failures."""
    def __init__(
        self, 
        message: str, 
        username: Optional[str] = None
    ):
        context = {'username': username} if username else {}
        super().__init__(
            message, 
            context=context, 
            severity=ErrorSeverity.CRITICAL
        )

def handle_error(
    logger: logging.Logger, 
    error_type: type = PrometheusBaseError, 
    default_message: str = "An unexpected error occurred",
    default_severity: ErrorSeverity = ErrorSeverity.MEDIUM
) -> Callable:
    """
    Decorator for error handling and logging.
    
    Wraps a function to catch and log errors with standard handling.
    
    Args:
        logger: Logging instance to use
        error_type: Type of error to raise
        default_message: Default error message if none provided
        default_severity: Default error severity
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_context = {
                    'function': func.__name__,
                    'module': func.__module__,
                    'args': str(args),
                    'kwargs': str(kwargs)
                }
                
                # Log full traceback
                logger.error(
                    f"Error in {func.__name__}: {str(e)}\n" +
                    "".join(traceback.format_tb(e.__traceback__))
                )
                
                # Raise custom error
                raise error_type(
                    default_message, 
                    context=error_context, 
                    severity=default_severity
                ) from e
        return wrapper
    return decorator

# Preserve original ClientAPIError
class ClientAPIError(PrometheusBaseError):
    """Error for API calls with status code."""

    def __init__(self, original_error: Exception):
        context = {}
        if hasattr(original_error, "status_code"):
            context['status_code'] = original_error.status_code
        
        message = (
            original_error.message 
            if hasattr(original_error, "message") 
            else str(original_error)
        )
        
        super().__init__(
            message, 
            context=context, 
            severity=ErrorSeverity.HIGH
        )