"""Enhanced error types for better exception handling and logging."""

from typing import Optional, Any, Dict
import traceback


class BasePrometheusError(Exception):
    """Base custom error for the Prometheus framework."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Initialize a base error with optional context.

        Args:
            message: Descriptive error message
            context: Optional dictionary with additional error context
        """
        self.context = context or {}
        super().__init__(message)


class ClientAPIError(BasePrometheusError):
    """Detailed error for API call failures."""

    def __init__(
        self,
        original_error: Optional[Exception] = None,
        message: Optional[str] = None,
        status_code: int = 500,
        api_response: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a client API error.

        Args:
            original_error: The original exception that occurred
            message: Custom error message
            status_code: HTTP status code (default 500)
            api_response: Optional API response details
        """
        self.status_code = status_code
        self.api_response = api_response or {}

        # Construct comprehensive error context
        context: Dict[str, Any] = {
            "status_code": status_code,
            "api_response": api_response
        }

        # Determine the most appropriate error message
        if message:
            error_message = message
        elif original_error:
            error_message = str(original_error)
        else:
            error_message = "Unspecified API error"

        # Add traceback to context if original error exists
        if original_error:
            context["traceback"] = traceback.format_exc()

        super().__init__(error_message, context)


class ConfigurationError(BasePrometheusError):
    """Error raised when configuration is invalid or missing."""

    def __init__(self, message: str, missing_keys: Optional[list] = None):
        """
        Initialize a configuration error.

        Args:
            message: Descriptive error message
            missing_keys: Optional list of missing configuration keys
        """
        context = {"missing_keys": missing_keys} if missing_keys else {}
        super().__init__(message, context)


class ResourceAccessError(BasePrometheusError):
    """Error raised when accessing external resources fails."""

    def __init__(
        self,
        message: str,
        resource: Optional[str] = None,
        error_type: Optional[str] = None
    ):
        """
        Initialize a resource access error.

        Args:
            message: Descriptive error message
            resource: The resource that could not be accessed
            error_type: Type of resource access error
        """
        context = {
            "resource": resource,
            "error_type": error_type
        }
        super().__init__(message, context)


def handle_error(
    error: Exception,
    default_message: str = "An unexpected error occurred",
    log_func: Optional[callable] = None
) -> Dict[str, Any]:
    """
    Standardized error handling function.

    Args:
        error: The exception to handle
        default_message: Default error message if not specified
        log_func: Optional logging function

    Returns:
        A standardized error response dictionary
    """
    # Log the error if a logging function is provided
    if log_func:
        log_func(error)

    # Handle known error types with more specific responses
    if isinstance(error, ClientAPIError):
        return {
            "success": False,
            "error": str(error),
            "status_code": error.status_code,
            "context": error.context
        }
    elif isinstance(error, ConfigurationError):
        return {
            "success": False,
            "error": str(error),
            "type": "configuration_error",
            "context": error.context
        }
    elif isinstance(error, ResourceAccessError):
        return {
            "success": False,
            "error": str(error),
            "type": "resource_access_error",
            "context": error.context
        }

    # Generic error handling
    return {
        "success": False,
        "error": str(error) or default_message,
        "traceback": traceback.format_exc()
    }