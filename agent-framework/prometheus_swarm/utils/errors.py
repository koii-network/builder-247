"""Comprehensive error handling for API and client interactions."""

from typing import Optional, Any


class PrometheusSwarmBaseError(Exception):
    """Base error for all Prometheus Swarm errors."""
    def __init__(self, message: str, code: int = 500):
        super().__init__(message)
        self.code = code


class ClientAPIError(PrometheusSwarmBaseError):
    """Detailed error for API call failures."""
    def __init__(self, 
                 message: str, 
                 status_code: int = 500, 
                 error_details: Optional[dict] = None):
        super().__init__(message, code=status_code)
        self.status_code = status_code
        self.error_details = error_details or {}

    def __str__(self):
        return (f"API Error (Status {self.status_code}): {super().__str__()}\n"
                f"Details: {self.error_details}")


class ValidationError(PrometheusSwarmBaseError):
    """Error for input validation failures."""
    def __init__(self, field: str, value: Any, reason: str):
        message = f"Validation failed for {field}: {value}. Reason: {reason}"
        super().__init__(message, code=400)
        self.field = field
        self.value = value


class AuthenticationError(PrometheusSwarmBaseError):
    """Error for authentication and authorization failures."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, code=401)


class RateLimitError(PrometheusSwarmBaseError):
    """Error for rate limit violations."""
    def __init__(self, reset_time: Optional[int] = None):
        message = "Rate limit exceeded"
        super().__init__(message, code=429)
        self.reset_time = reset_time


def validate_api_response(response: Any) -> None:
    """
    Validate API response and raise appropriate errors.
    
    Args:
        response: API response object
    
    Raises:
        ClientAPIError: If response indicates an error
    """
    if response is None:
        raise ClientAPIError("Empty API response", status_code=500)
    
    if hasattr(response, 'status_code'):
        if 400 <= response.status_code < 600:
            error_details = {
                'status_code': response.status_code,
                'reason': getattr(response, 'reason', 'Unknown Error')
            }
            raise ClientAPIError(
                f"API request failed: {response.status_code}",
                status_code=response.status_code,
                error_details=error_details
            )