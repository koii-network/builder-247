"""Tests for the custom error handling system."""

import pytest
from ..utils.errors import (
    BaseCustomError,
    ClientAPIError,
    ConfigurationError,
    ResourceNotFoundError,
    AuthenticationError,
    handle_error
)


def test_base_custom_error():
    """Test BaseCustomError creation and dictionary conversion."""
    context = {"user_id": 123}
    error = BaseCustomError(
        message="Test error",
        context=context,
        original_error=ValueError("Original")
    )

    assert str(error) == "Test error"
    error_dict = error.to_dict()
    assert error_dict["message"] == "Test error"
    assert error_dict["type"] == "BaseCustomError"
    assert error_dict["context"] == context
    assert "Original" in error_dict["original_error"]


def test_client_api_error():
    """Test ClientAPIError with different configurations."""
    error1 = ClientAPIError("API call failed", status_code=404)
    error2 = ClientAPIError(
        "Unauthorized",
        status_code=401,
        context={"endpoint": "/test"}
    )

    assert error1.status_code == 404
    assert "404" in str(error1)

    error_dict = error2.to_dict()
    assert error_dict["status_code"] == 401
    assert error_dict["context"] == {"endpoint": "/test"}


def test_error_conversion():
    """Test handle_error conversion of various exceptions."""
    # Test API error
    api_error = handle_error(
        ValueError("API request failed"),
        context={"url": "http://example.com"}
    )
    assert isinstance(api_error, ClientAPIError)

    # Test authentication error
    auth_error = handle_error(
        ValueError("Authentication failed"),
        context={"username": "test_user"}
    )
    assert isinstance(auth_error, AuthenticationError)

    # Test configuration error
    config_error = handle_error(
        ValueError("Configuration missing"),
        context={"config_key": "database"}
    )
    assert isinstance(config_error, ConfigurationError)


def test_error_logging():
    """Test logging function with error handling."""
    logged_errors = []

    def mock_log_func(error_dict):
        logged_errors.append(error_dict)

    # Test logging
    handle_error(
        ValueError("Test logging"),
        log_func=mock_log_func
    )

    assert len(logged_errors) == 1
    assert "message" in logged_errors[0]
    assert "type" in logged_errors[0]