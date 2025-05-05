from typing import Any, Dict, Optional
import logging

class APIError(Exception):
    """Base class for API-related errors."""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        """
        Initialize an API error with detailed information.

        Args:
            message (str): Human-readable error message
            status_code (int, optional): HTTP status code. Defaults to 500.
            details (dict, optional): Additional error details. Defaults to None.
        """
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
        logging.error(f"API Error: {message} (Status: {status_code})")

class InvalidInputError(APIError):
    """Raised when input validation fails."""
    def __init__(self, message: str, invalid_fields: Optional[Dict[str, str]] = None):
        """
        Initialize an invalid input error.

        Args:
            message (str): Description of the validation error
            invalid_fields (dict, optional): Specific fields that failed validation
        """
        details = {"invalid_fields": invalid_fields} if invalid_fields else {}
        super().__init__(message, status_code=400, details=details)

class AuthenticationError(APIError):
    """Raised when authentication or authorization fails."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)

class ResourceNotFoundError(APIError):
    """Raised when a requested resource cannot be found."""
    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type.capitalize()} with ID {resource_id} not found"
        super().__init__(message, status_code=404)

class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""
    def __init__(self, limit: int, reset_time: Optional[int] = None):
        details = {"rate_limit": limit, "reset_time": reset_time}
        super().__init__("Rate limit exceeded", status_code=429, details=details)

def validate_input(data: Dict[str, Any], required_fields: Dict[str, type], optional_fields: Optional[Dict[str, type]] = None):
    """
    Validate input data against required and optional fields.

    Args:
        data (dict): Input data to validate
        required_fields (dict): Dictionary of required fields and their expected types
        optional_fields (dict, optional): Dictionary of optional fields and their expected types

    Raises:
        InvalidInputError: If validation fails
    """
    invalid_fields = {}

    # Check required fields
    for field, field_type in required_fields.items():
        if field not in data:
            invalid_fields[field] = "Field is required"
        elif not isinstance(data[field], field_type):
            invalid_fields[field] = f"Expected type {field_type.__name__}"

    # Check optional fields if provided
    if optional_fields:
        for field, field_type in optional_fields.items():
            if field in data and not isinstance(data[field], field_type):
                invalid_fields[field] = f"Expected type {field_type.__name__}"

    if invalid_fields:
        raise InvalidInputError("Input validation failed", invalid_fields)