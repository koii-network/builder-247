"""Enhanced error handling for the project."""

import traceback
from typing import Optional, Dict, Any


class PrometheusBaseError(Exception):
    """Base exception for all Prometheus framework errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a base error with enhanced context.

        Args:
            message: A descriptive error message
            error_code: A unique error code for categorization
            context: Additional context about the error
        """
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.context = context or {}
        self.traceback = traceback.format_exc()
        super().__init__(self.formatted_message)

    @property
    def formatted_message(self) -> str:
        """Provide a comprehensive error message."""
        base_msg = f"[{self.error_code}] {self.message}"
        
        if self.context:
            context_str = " | ".join(f"{k}: {v}" for k, v in self.context.items())
            base_msg += f" (Context: {context_str})"
        
        return base_msg


class ConfigurationError(PrometheusBaseError):
    """Raised when there's an issue with configuration."""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="CONFIG_ERROR", context=context)


class ClientAPIError(PrometheusBaseError):
    """Error for API calls with additional details."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        original_error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an API error with status code and context.

        Args:
            message: A descriptive error message
            status_code: HTTP status code or error code
            original_error: The original exception if available
            context: Additional context about the API error
        """
        context = context or {}
        context.update({
            "status_code": status_code,
            "original_error": str(original_error) if original_error else None
        })
        super().__init__(
            message,
            error_code=f"API_ERROR_{status_code}",
            context=context
        )
        self.status_code = status_code


class NetworkError(PrometheusBaseError):
    """Raised for network-related issues."""
    def __init__(
        self,
        message: str,
        host: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        context = context or {}
        if host:
            context["host"] = host
        super().__init__(message, error_code="NETWORK_ERROR", context=context)


class ResourceError(PrometheusBaseError):
    """Raised when there are resource constraints or access issues."""
    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        context = context or {}
        if resource_type:
            context["resource_type"] = resource_type
        super().__init__(
            message,
            error_code="RESOURCE_ERROR",
            context=context
        )


def create_error(
    error_type: str,
    message: str,
    **kwargs
) -> PrometheusBaseError:
    """
    Factory method to create specific error types.

    Args:
        error_type: Type of error to create
        message: Error message
        **kwargs: Additional parameters for specific error types

    Returns:
        A specific error instance
    """
    error_map = {
        "config": ConfigurationError,
        "api": ClientAPIError,
        "network": NetworkError,
        "resource": ResourceError
    }

    error_class = error_map.get(error_type.lower(), PrometheusBaseError)
    return error_class(message, **kwargs)