"""
API Error Handling Module

This module provides custom exceptions and error handling utilities
for the Prometheus Swarm Agent Framework.
"""

from typing import Optional, Any, Dict


class APIError(Exception):
    """Base class for API-related exceptions."""
    
    def __init__(self, 
                 message: str = "An API error occurred", 
                 status_code: int = 500, 
                 details: Optional[Dict[str, Any]] = None):
        """
        Initialize an API error.

        Args:
            message (str): Error message describing the issue.
            status_code (int): HTTP status code for the error.
            details (dict, optional): Additional error details.
        """
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the error to a dictionary representation.

        Returns:
            dict: Error details suitable for JSON serialization.
        """
        error_dict = {
            "message": self.message,
            "status_code": self.status_code
        }
        if self.details:
            error_dict["details"] = self.details
        return error_dict


class InvalidInputError(APIError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, invalid_fields: Optional[Dict[str, str]] = None):
        """
        Initialize an invalid input error.

        Args:
            message (str): Description of the validation error.
            invalid_fields (dict, optional): Fields that failed validation.
        """
        super().__init__(
            message=message, 
            status_code=400,
            details={"invalid_fields": invalid_fields or {}}
        )


class AuthenticationError(APIError):
    """Raised when authentication or authorization fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        """
        Initialize an authentication error.

        Args:
            message (str): Authentication error description.
        """
        super().__init__(
            message=message, 
            status_code=401
        )


class ResourceNotFoundError(APIError):
    """Raised when a requested resource cannot be found."""
    
    def __init__(self, resource_type: str, resource_id: Optional[str] = None):
        """
        Initialize a resource not found error.

        Args:
            resource_type (str): Type of resource not found.
            resource_id (str, optional): Specific ID of missing resource.
        """
        details = {"resource_type": resource_type}
        if resource_id:
            details["resource_id"] = resource_id
        
        super().__init__(
            message=f"{resource_type} not found",
            status_code=404,
            details=details
        )


class RateLimitError(APIError):
    """Raised when API rate limits are exceeded."""
    
    def __init__(self, limit: int, reset_time: Optional[float] = None):
        """
        Initialize a rate limit error.

        Args:
            limit (int): Maximum number of allowed requests.
            reset_time (float, optional): Time when rate limit resets.
        """
        details = {"rate_limit": limit}
        if reset_time:
            details["reset_time"] = reset_time
        
        super().__init__(
            message="Rate limit exceeded",
            status_code=429,
            details=details
        )


def validate_input(data: Any, rules: Dict[str, Any]) -> None:
    """
    Validate input data against specified rules.

    Args:
        data (dict): Input data to validate.
        rules (dict): Validation rules.

    Raises:
        InvalidInputError: If validation fails.
    """
    invalid_fields = {}

    for field, validators in rules.items():
        # Check if field is missing and required
        if field not in data:
            if validators.get('required', False):
                invalid_fields[field] = "Required field missing"
            continue

        value = data[field]

        # Type validation first
        if 'type' in validators:
            # Check type compatibility
            if not isinstance(value, validators['type']):
                try:
                    # Attempt type conversion
                    value = validators['type'](value)
                except (ValueError, TypeError):
                    invalid_fields[field] = f"Must be of type {validators['type'].__name__}"
                    continue

        # Range validation for numeric types
        if 'min' in validators and isinstance(value, (int, float)):
            if value < validators['min']:
                invalid_fields[field] = f"Must be greater than or equal to {validators['min']}"

        if 'max' in validators and isinstance(value, (int, float)):
            if value > validators['max']:
                invalid_fields[field] = f"Must be less than or equal to {validators['max']}"

        # Custom validation
        if 'validator' in validators and not validators['validator'](value):
            invalid_fields[field] = "Failed custom validation"

    # Raise error if any validation failed
    if invalid_fields:
        raise InvalidInputError(
            "Input validation failed", 
            invalid_fields
        )