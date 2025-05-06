"""Custom error types and error handling utilities."""

from typing import Optional, Any


class PrometheusBaseError(Exception):
    """Base error class for all Prometheus framework errors."""

    def __init__(self, message: str, error_code: Optional[int] = None):
        """
        Initialize a base error with message and optional error code.

        Args:
            message (str): Descriptive error message
            error_code (Optional[int]): Numeric error code, defaults to None
        """
        self.error_code = error_code
        super().__init__(message)


class ClientAPIError(PrometheusBaseError):
    """Error for API calls with status code."""

    def __init__(self, original_error: Exception):
        """
        Initialize ClientAPIError with an original error.

        Args:
            original_error (Exception): The original exception
        """
        status_code = getattr(original_error, "status_code", 500)
        message = getattr(original_error, "message", str(original_error))
        super().__init__(message, status_code)


class ConfigurationError(PrometheusBaseError):
    """Error raised when configuration is invalid or missing."""

    def __init__(self, message: str, config_key: Optional[str] = None):
        """
        Initialize ConfigurationError.

        Args:
            message (str): Descriptive error message
            config_key (Optional[str]): The specific configuration key causing the issue
        """
        self.config_key = config_key
        super().__init__(message)


class ValidationError(PrometheusBaseError):
    """Error raised when data validation fails."""

    def __init__(self, message: str, invalid_data: Any = None):
        """
        Initialize ValidationError.

        Args:
            message (str): Descriptive error message
            invalid_data (Any): The data that failed validation
        """
        self.invalid_data = invalid_data
        super().__init__(message)


def handle_api_error(error: Exception) -> ClientAPIError:
    """
    Convert an exception to a standardized ClientAPIError.

    Args:
        error (Exception): The original exception

    Returns:
        ClientAPIError: Standardized API error
    """
    if isinstance(error, ClientAPIError):
        return error
    return ClientAPIError(error)