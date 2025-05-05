class APIError(Exception):
    """Base exception for API-related errors."""
    pass

class NetworkError(APIError):
    """Exception raised for network-related errors."""
    pass

class AuthenticationError(APIError):
    """Exception raised for authentication-related errors."""
    pass

class RateLimitError(APIError):
    """Exception raised when rate limit is exceeded."""
    pass

def handle_api_error(response):
    """
    Centralized error handling for API responses.
    
    Args:
        response: The HTTP response object
    
    Raises:
        AuthenticationError: For 401 unauthorized errors
        RateLimitError: For 429 rate limit errors
        APIError: For other server-side errors
    """
    if response.status_code == 401:
        raise AuthenticationError("Authentication failed")
    elif response.status_code == 429:
        raise RateLimitError("Rate limit exceeded")
    elif 400 <= response.status_code < 600:
        raise APIError(f"Server error: {response.status_code} - {response.text}")