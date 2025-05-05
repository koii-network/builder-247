"""
Unit tests for API Error Handling Module
"""

import pytest
from prometheus_swarm.utils.api_errors import (
    APIError, 
    InvalidInputError, 
    AuthenticationError, 
    ResourceNotFoundError, 
    RateLimitError,
    validate_input
)


def test_base_api_error():
    """Test basic APIError functionality."""
    error = APIError("Test error", 500, {"test": "detail"})
    
    assert str(error) == "Test error"
    assert error.status_code == 500
    assert error.details == {"test": "detail"}
    
    error_dict = error.to_dict()
    assert error_dict == {
        "message": "Test error",
        "status_code": 500,
        "details": {"test": "detail"}
    }


def test_invalid_input_error():
    """Test InvalidInputError with invalid fields."""
    error = InvalidInputError(
        "Validation failed", 
        {"name": "Required field", "age": "Must be a positive integer"}
    )
    
    assert error.status_code == 400
    assert error.details == {
        "invalid_fields": {
            "name": "Required field", 
            "age": "Must be a positive integer"
        }
    }


def test_authentication_error():
    """Test AuthenticationError."""
    error = AuthenticationError("Invalid credentials")
    
    assert error.message == "Invalid credentials"
    assert error.status_code == 401


def test_resource_not_found_error():
    """Test ResourceNotFoundError."""
    error = ResourceNotFoundError("User", "123")
    
    assert error.message == "User not found"
    assert error.status_code == 404
    assert error.details == {
        "resource_type": "User", 
        "resource_id": "123"
    }


def test_rate_limit_error():
    """Test RateLimitError."""
    error = RateLimitError(100, 1623456789.0)
    
    assert error.message == "Rate limit exceeded"
    assert error.status_code == 429
    assert error.details == {
        "rate_limit": 100,
        "reset_time": 1623456789.0
    }


def test_input_validation_success():
    """Test successful input validation."""
    rules = {
        'age': {
            'type': int,
            'min': 18,
            'max': 100,
            'required': True
        },
        'name': {
            'type': str,
            'validator': lambda x: len(x) > 2
        }
    }
    
    data = {'age': 25, 'name': 'John'}
    
    try:
        validate_input(data, rules)
    except InvalidInputError:
        pytest.fail("Valid input raised an error")


def test_input_validation_type_error():
    """Test input validation type error."""
    rules = {
        'age': {
            'type': int,
            'min': 18,
            'max': 100,
            'required': True
        }
    }
    
    data = {'age': '25'}  # Wrong type
    
    with pytest.raises(InvalidInputError) as excinfo:
        validate_input(data, rules)
    
    assert 'Must be of type int' in str(excinfo.value)


def test_input_validation_range_error():
    """Test input validation range error."""
    rules = {
        'age': {
            'type': int,
            'min': 18,
            'max': 100,
            'required': True
        }
    }
    
    data = {'age': 17}  # Below minimum
    
    with pytest.raises(InvalidInputError) as excinfo:
        validate_input(data, rules)
    
    assert 'Must be greater than or equal to 18' in str(excinfo.value)


def test_input_validation_missing_required():
    """Test validation of missing required field."""
    rules = {
        'age': {
            'type': int,
            'required': True
        }
    }
    
    data = {}
    
    with pytest.raises(InvalidInputError) as excinfo:
        validate_input(data, rules)
    
    assert 'Required field missing' in str(excinfo.value)