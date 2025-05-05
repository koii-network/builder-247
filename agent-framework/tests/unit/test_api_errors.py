"""
Unit tests for API error handling module.
"""

import pytest
from prometheus_swarm.utils.api_errors import (
    APIError, 
    InvalidRequestError, 
    AuthenticationError, 
    ResourceNotFoundError, 
    RateLimitError, 
    ServerError,
    validate_request_parameters,
    handle_api_error
)


def test_api_error_base():
    """Test base APIError creation."""
    error = APIError("Test message", 400)
    assert str(error) == "Test message"
    assert error.status_code == 400


def test_invalid_request_error():
    """Test InvalidRequestError."""
    error = InvalidRequestError("Custom invalid request")
    assert str(error) == "Custom invalid request"
    assert error.status_code == 400


def test_authentication_error():
    """Test AuthenticationError."""
    error = AuthenticationError("Custom auth error")
    assert str(error) == "Custom auth error"
    assert error.status_code == 401


def test_resource_not_found_error():
    """Test ResourceNotFoundError."""
    error = ResourceNotFoundError("Custom not found")
    assert str(error) == "Custom not found"
    assert error.status_code == 404


def test_rate_limit_error():
    """Test RateLimitError."""
    error = RateLimitError("Custom rate limit")
    assert str(error) == "Custom rate limit"
    assert error.status_code == 429


def test_server_error():
    """Test ServerError."""
    error = ServerError("Custom server error")
    assert str(error) == "Custom server error"
    assert error.status_code == 500


def test_validate_request_parameters_success():
    """Test successful parameter validation."""
    params = {"name": "test", "value": 42}
    validate_request_parameters(params, ["name", "value"])


def test_validate_request_parameters_missing():
    """Test parameter validation with missing parameters."""
    params = {"name": "test"}
    with pytest.raises(InvalidRequestError, match="Missing required parameter: value"):
        validate_request_parameters(params, ["name", "value"])


def test_validate_request_parameters_none():
    """Test parameter validation with None values."""
    params = {"name": "test", "value": None}
    with pytest.raises(InvalidRequestError, match="Missing required parameter: value"):
        validate_request_parameters(params, ["name", "value"])


def test_handle_api_error_decorator():
    """Test the handle_api_error decorator."""
    @handle_api_error
    def successful_func():
        return "Success"
    
    @handle_api_error
    def invalid_request_func():
        raise InvalidRequestError()
    
    @handle_api_error
    def unexpected_error_func():
        raise ValueError("Unexpected error")
    
    # Test successful case
    assert successful_func() == "Success"
    
    # Test known error propagation
    with pytest.raises(InvalidRequestError):
        invalid_request_func()
    
    # Test unexpected error conversion
    with pytest.raises(ServerError):
        unexpected_error_func()