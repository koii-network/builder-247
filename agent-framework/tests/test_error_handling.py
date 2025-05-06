"""Tests for enhanced error handling and logging utilities."""

import pytest
from prometheus_swarm.utils.errors import (
    BasePrometheusError,
    ClientAPIError,
    ConfigurationError,
    ResourceAccessError,
    handle_error
)

def test_base_prometheus_error():
    """Test the BasePrometheusError with context."""
    error = BasePrometheusError("Test error", {"key": "value"})
    
    assert str(error) == "Test error"
    assert error.context == {"key": "value"}

def test_client_api_error():
    """Test ClientAPIError with various initialization scenarios."""
    # With original error
    original_error = ValueError("Connection failed")
    api_error = ClientAPIError(
        original_error=original_error, 
        status_code=404, 
        api_response={"detail": "Not found"}
    )
    
    assert str(api_error) == "Connection failed"
    assert api_error.status_code == 404
    assert api_error.api_response == {"detail": "Not found"}

def test_configuration_error():
    """Test ConfigurationError with missing keys."""
    error = ConfigurationError(
        "Missing configuration", 
        missing_keys=["API_KEY", "SECRET"]
    )
    
    assert str(error) == "Missing configuration"
    assert error.context == {"missing_keys": ["API_KEY", "SECRET"]}

def test_resource_access_error():
    """Test ResourceAccessError with detailed information."""
    error = ResourceAccessError(
        "Could not access resource", 
        resource="external_api", 
        error_type="network_timeout"
    )
    
    assert str(error) == "Could not access resource"
    assert error.context == {
        "resource": "external_api", 
        "error_type": "network_timeout"
    }

def test_handle_error_with_mocked_logging():
    """Test handle_error function with a mock logging function."""
    # Mock logging function to track calls
    log_calls = []
    def mock_log_func(error):
        log_calls.append(str(error))

    # Test with various error types
    client_error = ClientAPIError(
        message="API Error", 
        status_code=500, 
        api_response={"error": "Internal Server Error"}
    )
    
    result = handle_error(client_error, log_func=mock_log_func)
    
    assert result["success"] is False
    assert result["error"] == "API Error"
    assert result["status_code"] == 500
    assert len(log_calls) == 1  # Verify log function was called

def test_nested_exception_handling():
    """Demonstrate nested exception handling."""
    def inner_function():
        try:
            raise ValueError("Inner error")
        except ValueError as e:
            raise ResourceAccessError("Resource access failed", error_type="validation") from e

    def outer_function():
        try:
            inner_function()
        except ResourceAccessError as e:
            return handle_error(e)

    result = outer_function()
    
    assert result["success"] is False
    assert "Resource access failed" in result["error"]
    assert result["context"]["error_type"] == "validation"