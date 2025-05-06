"""Unit tests for custom error types in Prometheus framework."""

import pytest
from prometheus_swarm.utils.errors import (
    PrometheusBaseError,
    ClientAPIError,
    ConfigurationError,
    ValidationError,
    handle_api_error
)


def test_prometheus_base_error():
    """Test PrometheusBaseError initialization."""
    message = "Base error test"
    error_code = 42
    error = PrometheusBaseError(message, error_code)
    
    assert str(error) == message
    assert error.error_code == error_code


def test_client_api_error():
    """Test ClientAPIError with different types of original errors."""
    class MockAPIError(Exception):
        def __init__(self, status_code, message):
            self.status_code = status_code
            self.message = message

    # Test with mock API error
    mock_error = MockAPIError(404, "Not Found")
    api_error = ClientAPIError(mock_error)
    
    assert str(api_error) == "Not Found"
    assert api_error.error_code == 404

    # Test with standard exception
    std_error = ValueError("Standard Error")
    std_api_error = ClientAPIError(std_error)
    
    assert str(std_api_error) == "Standard Error"
    assert std_api_error.error_code == 500


def test_configuration_error():
    """Test ConfigurationError with configuration key."""
    message = "Invalid configuration"
    config_key = "DATABASE_URL"
    error = ConfigurationError(message, config_key)
    
    assert str(error) == message
    assert error.config_key == config_key


def test_validation_error():
    """Test ValidationError with invalid data."""
    message = "Data validation failed"
    invalid_data = {"username": ""}
    error = ValidationError(message, invalid_data)
    
    assert str(error) == message
    assert error.invalid_data == invalid_data


def test_handle_api_error():
    """Test handle_api_error utility function."""
    # Test with a standard exception
    std_exception = TypeError("Type mismatch")
    handled_error = handle_api_error(std_exception)
    
    assert isinstance(handled_error, ClientAPIError)
    assert str(handled_error) == "Type mismatch"

    # Test with an already converted API error
    api_error = ClientAPIError(ValueError("Original error"))
    re_handled_error = handle_api_error(api_error)
    
    assert re_handled_error is api_error