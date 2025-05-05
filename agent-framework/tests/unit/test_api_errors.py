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
    # Test base APIError
    error = APIError("Test error", status_code=500, details={"key": "value"})
    assert str(error) == "Test error"
    assert error.status_code == 500
    assert error.details == {"key": "value"}

def test_invalid_input_error():
    # Test InvalidInputError
    invalid_fields = {
        "username": "Field is required",
        "age": "Expected type int"
    }
    error = InvalidInputError("Validation failed", invalid_fields)
    assert error.status_code == 400
    assert error.details == {"invalid_fields": invalid_fields}

def test_authentication_error():
    # Test AuthenticationError
    error = AuthenticationError()
    assert str(error) == "Authentication failed"
    assert error.status_code == 401

def test_resource_not_found_error():
    # Test ResourceNotFoundError
    error = ResourceNotFoundError("user", "123")
    assert str(error) == "User with ID 123 not found"
    assert error.status_code == 404

def test_rate_limit_error():
    # Test RateLimitError
    error = RateLimitError(100, reset_time=1234567)
    assert error.status_code == 429
    assert error.details == {"rate_limit": 100, "reset_time": 1234567}

def test_validate_input_success():
    # Test successful input validation
    data = {"name": "John", "age": 30}
    required_fields = {"name": str, "age": int}
    optional_fields = {"email": str}
    
    try:
        validate_input(data, required_fields, optional_fields)
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")

def test_validate_input_missing_required_field():
    # Test validation with missing required field
    data = {"name": "John"}
    required_fields = {"name": str, "age": int}
    
    with pytest.raises(InvalidInputError) as exc_info:
        validate_input(data, required_fields)
    
    assert "age" in exc_info.value.details["invalid_fields"]

def test_validate_input_incorrect_type():
    # Test validation with incorrect field type
    data = {"name": "John", "age": "thirty"}
    required_fields = {"name": str, "age": int}
    
    with pytest.raises(InvalidInputError) as exc_info:
        validate_input(data, required_fields)
    
    assert "age" in exc_info.value.details["invalid_fields"]
    assert "Expected type int" in exc_info.value.details["invalid_fields"]["age"]

def test_validate_input_optional_field():
    # Test validation with optional field
    data = {"name": "John", "age": 30, "email": 12345}
    required_fields = {"name": str, "age": int}
    optional_fields = {"email": str}
    
    with pytest.raises(InvalidInputError) as exc_info:
        validate_input(data, required_fields, optional_fields)
    
    assert "email" in exc_info.value.details["invalid_fields"]
    assert "Expected type str" in exc_info.value.details["invalid_fields"]["email"]