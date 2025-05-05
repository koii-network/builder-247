"""Unit tests for API error handling."""

import pytest
from prometheus_swarm.utils.errors import (
    PrometheusSwarmBaseError,
    ClientAPIError,
    ValidationError,
    AuthenticationError,
    RateLimitError,
    validate_api_response
)


def test_base_error():
    """Test base error initialization."""
    error = PrometheusSwarmBaseError("Test error", 500)
    assert str(error) == "Test error"
    assert error.code == 500


def test_client_api_error():
    """Test ClientAPIError with details."""
    error_details = {"field": "token", "reason": "invalid"}
    error = ClientAPIError(
        "Authentication failed", 
        status_code=401, 
        error_details=error_details
    )
    
    assert error.status_code == 401
    assert "Authentication failed" in str(error)
    assert error.error_details == error_details


def test_validation_error():
    """Test ValidationError for input validation."""
    error = ValidationError("email", "invalid_email", "Invalid format")
    
    assert "email" in str(error)
    assert "invalid_email" in str(error)
    assert error.code == 400


def test_authentication_error():
    """Test AuthenticationError."""
    error = AuthenticationError("Invalid credentials")
    
    assert str(error) == "Invalid credentials"
    assert error.code == 401


def test_rate_limit_error():
    """Test RateLimitError."""
    error = RateLimitError(reset_time=1234567890)
    
    assert str(error) == "Rate limit exceeded"
    assert error.code == 429
    assert error.reset_time == 1234567890


def test_validate_api_response_null():
    """Test validate_api_response with None."""
    with pytest.raises(ClientAPIError, match="Empty API response"):
        validate_api_response(None)


class MockResponse:
    def __init__(self, status_code, reason=None):
        self.status_code = status_code
        self.reason = reason


def test_validate_api_response_error_status():
    """Test validate_api_response with error status codes."""
    error_responses = [
        MockResponse(400, "Bad Request"),
        MockResponse(401, "Unauthorized"),
        MockResponse(403, "Forbidden"),
        MockResponse(404, "Not Found"),
        MockResponse(500, "Internal Server Error")
    ]
    
    for response in error_responses:
        with pytest.raises(ClientAPIError) as exc_info:
            validate_api_response(response)
        
        assert exc_info.value.status_code == response.status_code
        assert response.reason in str(exc_info.value)