"""Unit tests for comprehensive error handling utilities."""

import pytest
from prometheus_swarm.utils.errors import (
    PrometheusBaseError,
    ClientAPIError,
    ConfigurationError,
    handle_and_log_error,
    safe_execute
)


def test_prometheus_base_error():
    """Test the base error class with all initialization parameters."""
    # Test with minimal parameters
    error1 = PrometheusBaseError("Test error")
    assert str(error1)
    assert error1.error_code == "UNKNOWN_ERROR"

    # Test with full parameters
    context = {"key": "value"}
    original_error = ValueError("Original error")
    error2 = PrometheusBaseError(
        message="Detailed error",
        error_code="TEST_ERROR",
        context=context,
        original_error=original_error
    )
    assert "TEST_ERROR" in str(error2)
    assert "Detailed error" in str(error2)
    assert "{'key': 'value'}" in str(error2)


def test_client_api_error():
    """Test the client API error class."""
    error = ClientAPIError(
        "API call failed",
        status_code=404,
        error_code="NOT_FOUND",
        context={"endpoint": "/test"}
    )
    assert error.status_code == 404
    assert "NOT_FOUND" in str(error)
    assert "API call failed" in str(error)


def test_configuration_error():
    """Test the configuration error class."""
    error = ConfigurationError(
        "Invalid configuration",
        context={"setting": "timeout"}
    )
    assert "CONFIG_ERROR" in str(error)
    assert "Invalid configuration" in str(error)


def test_handle_and_log_error():
    """Test the error handling decorator."""
    # Mock logging function
    logged_errors = []

    def mock_logger(error):
        logged_errors.append(error)

    @handle_and_log_error(logger_func=mock_logger, error_type=ClientAPIError)
    def test_function(raise_error=False):
        if raise_error:
            raise ValueError("Test error")
        return "Success"

    # Test successful execution
    result = test_function()
    assert result == "Success"
    assert len(logged_errors) == 0

    # Test error handling
    with pytest.raises(ClientAPIError) as exc_info:
        test_function(raise_error=True)

    # Verify custom error details
    error = exc_info.value
    assert isinstance(error, ClientAPIError)
    assert "test_function" in str(error)
    assert "Test error" in str(error)


def test_safe_execute():
    """Test safe execution of functions."""
    # Successful function
    result = safe_execute(lambda: 42)
    assert result == 42

    # Error handling with default return
    result = safe_execute(lambda: 1/0, default_return=-1)
    assert result == -1

    # Error handling with custom error handler
    errors = []
    def error_handler(error):
        errors.append(error)

    result = safe_execute(
        lambda: 1/0,
        default_return=None,
        error_handler=error_handler
    )
    assert result is None
    assert len(errors) == 1
    assert isinstance(errors[0], ZeroDivisionError)