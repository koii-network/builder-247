"""Enhanced error types and handling for the application."""

from typing import Any, Dict, Optional


class BaseCustomError(Exception):
    """Base class for custom exceptions with additional context."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize a custom error with optional context and original error.

        Args:
            message (str): Descriptive error message
            context (dict, optional): Additional error context
            original_error (Exception, optional): Original exception that caused this error
        """
        self.message = message
        self.context = context or {}
        self.original_error = original_error
        super().__init__(self.message)

    def __str__(self) -> str:
        """Override str representation to include full error information."""
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error to a dictionary for logging and serialization.

        Returns:
            Dict containing error details
        """
        error_dict = {
            "message": self.message,
            "type": self.__class__.__name__,
        }
        if self.context:
            error_dict["context"] = self.context
        if self.original_error:
            error_dict["original_error"] = str(self.original_error)
        return error_dict


class ClientAPIError(BaseCustomError):
    """Specific error for API call failures."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        context: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize an API error with status code.

        Args:
            message (str): Error message
            status_code (int): HTTP status code, defaults to 500
            context (dict, optional): Additional context
            original_error (Exception, optional): Original exception
        """
        self.status_code = status_code
        super().__init__(
            message=message,
            context=context or {},
            original_error=original_error
        )

    def __str__(self) -> str:
        """Override str representation to include status code."""
        return f"{self.message} (Status {self.status_code})"

    def to_dict(self) -> Dict[str, Any]:
        """Extend base method with status code."""
        error_dict = super().to_dict()
        error_dict["status_code"] = self.status_code
        return error_dict


class ConfigurationError(BaseCustomError):
    """Error raised for configuration-related issues."""
    pass


class ResourceNotFoundError(BaseCustomError):
    """Error raised when a requested resource is not found."""
    pass


class AuthenticationError(BaseCustomError):
    """Error raised for authentication and authorization failures."""
    pass


def handle_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    log_func: Optional[callable] = None
) -> BaseCustomError:
    """
    Standardized error handling and conversion.

    Args:
        error (Exception): Original exception
        context (dict, optional): Additional context
        log_func (callable, optional): Optional logging function

    Returns:
        BaseCustomError: Converted and potentially logged error
    """
    context = context or {}

    if isinstance(error, BaseCustomError):
        if log_func:
            log_func(error.to_dict())
        return error

    # Determine the most appropriate custom error type
    if "api" in str(error).lower():
        custom_error = ClientAPIError(
            message=str(error),
            context=context,
            original_error=error
        )
    elif "authentication" in str(error).lower():
        custom_error = AuthenticationError(
            message=str(error),
            context=context,
            original_error=error
        )
    elif "configuration" in str(error).lower():
        custom_error = ConfigurationError(
            message=str(error),
            context=context,
            original_error=error
        )
    else:
        custom_error = BaseCustomError(
            message=str(error),
            context=context,
            original_error=error
        )

    if log_func:
        log_func(custom_error.to_dict())

    return custom_error