"""Enhanced error handling utilities for the Prometheus Swarm framework."""

import traceback
from typing import Optional, Dict, Any, Union

class BaseSwarmError(Exception):
    """Base custom error for the Prometheus Swarm framework."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a BaseSwarmError.

        Args:
            message: A human-readable error description
            error_code: A unique identifier for the error type
            context: Additional context information about the error
        """
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.context = context or {}
        self.traceback = traceback.format_exc()
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error to a dictionary representation.

        Returns:
            A structured dictionary with error details
        """
        return {
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "traceback": self.traceback
        }

class ClientAPIError(BaseSwarmError):
    """
    Specialized error for API-related exceptions.

    Captures detailed information about API call failures.
    """

    def __init__(
        self,
        original_error: Union[Exception, str],
        status_code: int = 500,
        service: Optional[str] = None,
        endpoint: Optional[str] = None
    ):
        """
        Initialize a ClientAPIError.

        Args:
            original_error: The original exception or error message
            status_code: HTTP status code of the error (default: 500)
            service: Name of the service where the error occurred
            endpoint: The specific API endpoint that failed
        """
        context = {
            "status_code": status_code,
            "service": service,
            "endpoint": endpoint
        }

        if isinstance(original_error, Exception):
            message = str(original_error)
            context["original_exception"] = type(original_error).__name__
        else:
            message = str(original_error)

        super().__init__(
            message=message,
            error_code="CLIENT_API_ERROR",
            context=context
        )
        self.status_code = status_code

class ConfigurationError(BaseSwarmError):
    """Error raised when there's an issue with configuration."""

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        expected_value: Optional[Any] = None
    ):
        """
        Initialize a ConfigurationError.

        Args:
            message: Description of the configuration error
            config_key: The specific configuration key that caused the error
            expected_value: The expected value for the configuration
        """
        context = {
            "config_key": config_key,
            "expected_value": expected_value
        }

        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            context=context
        )

def handle_and_log_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    logger=None
) -> Dict[str, Any]:
    """
    Standardized error handling and logging utility.

    Args:
        error: The exception to handle
        context: Optional additional context about the error
        logger: Optional logger to use for logging the error

    Returns:
        A dictionary representation of the error
    """
    context = context or {}

    if isinstance(error, BaseSwarmError):
        error_dict = error.to_dict()
    else:
        error_dict = BaseSwarmError(
            message=str(error),
            context=context
        ).to_dict()

    # Log the error if a logger is provided
    if logger:
        logger.error(f"Error Details: {error_dict}")

    return error_dict

# Add error handling configuration
def configure_error_handling(global_error_handler=None):
    """
    Configure global error handling strategy.

    Args:
        global_error_handler: Optional function to handle unhandled exceptions
    """
    if global_error_handler:
        import sys
        sys.excepthook = global_error_handler