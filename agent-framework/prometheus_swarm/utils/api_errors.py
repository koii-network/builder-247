"""
API Error Handling Module

This module provides custom exception classes and error handling utilities 
for API interactions in the Prometheus Swarm framework.
"""

class APIError(Exception):
    """Base class for API-related exceptions."""
    def __init__(self, message, status_code=None):
        """
        Initialize an API error.
        
        Args:
            message (str): Descriptive error message
            status_code (int, optional): HTTP status code associated with the error
        """
        super().__init__(message)
        self.status_code = status_code


class InvalidRequestError(APIError):
    """Raised when the API request is invalid or malformed."""
    def __init__(self, message="Invalid API request", status_code=400):
        super().__init__(message, status_code)


class AuthenticationError(APIError):
    """Raised when authentication fails."""
    def __init__(self, message="Authentication failed", status_code=401):
        super().__init__(message, status_code)


class ResourceNotFoundError(APIError):
    """Raised when a requested resource is not found."""
    def __init__(self, message="Resource not found", status_code=404):
        super().__init__(message, status_code)


class RateLimitError(APIError):
    """Raised when API rate limits are exceeded."""
    def __init__(self, message="Rate limit exceeded", status_code=429):
        super().__init__(message, status_code)


class ServerError(APIError):
    """Raised for internal server errors."""
    def __init__(self, message="Internal server error", status_code=500):
        super().__init__(message, status_code)


def validate_request_parameters(params, required_params):
    """
    Validate that all required parameters are present and non-None.
    
    Args:
        params (dict): Dictionary of parameters to validate
        required_params (list): List of required parameter names
    
    Raises:
        InvalidRequestError: If any required parameter is missing or None
    """
    for param in required_params:
        if param not in params or params[param] is None:
            raise InvalidRequestError(f"Missing required parameter: {param}")


def handle_api_error(func):
    """
    Decorator to provide consistent error handling for API methods.
    
    Args:
        func (callable): Function to wrap with error handling
    
    Returns:
        callable: Wrapped function with consistent error handling
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except InvalidRequestError:
            raise
        except AuthenticationError:
            raise
        except ResourceNotFoundError:
            raise
        except Exception as e:
            # Log the original exception for debugging
            # In a real-world scenario, you'd use proper logging
            print(f"Unexpected error in {func.__name__}: {e}")
            raise ServerError(f"Unexpected error: {str(e)}")
    return wrapper