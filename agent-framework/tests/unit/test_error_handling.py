"""
Test suite for error handling utilities in the Prometheus Swarm Agent Framework.

This module tests the error handling mechanisms, specifically the ClientAPIError.
"""

import pytest
from prometheus_swarm.utils.errors import ClientAPIError


class MockException(Exception):
    """Mock exception for testing error handling."""
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def test_client_api_error_with_status_code_and_message():
    """
    Test ClientAPIError initialization with a mock exception
    that has both status_code and message attributes.
    """
    original_error = MockException("Test Error", 400)
    client_error = ClientAPIError(original_error)
    
    assert client_error.status_code == 400
    assert str(client_error) == "Test Error"


def test_client_api_error_with_only_status_code():
    """
    Test ClientAPIError initialization with an exception
    that only has a status_code attribute.
    """
    class StatusCodeException(Exception):
        status_code = 403

    original_error = StatusCodeException("Generic error")
    client_error = ClientAPIError(original_error)
    
    assert client_error.status_code == 403
    assert str(client_error) == "Generic error"


def test_client_api_error_without_status_code():
    """
    Test ClientAPIError initialization with a basic exception
    that lacks status_code and message attributes.
    """
    original_error = ValueError("Basic error")
    client_error = ClientAPIError(original_error)
    
    assert client_error.status_code == 500  # Default status code
    assert str(client_error) == "Basic error"


def test_client_api_error_inheritance():
    """
    Verify that ClientAPIError is an Exception subclass.
    """
    assert issubclass(ClientAPIError, Exception)


def test_client_api_error_raises_with_custom_exceptions():
    """
    Ensure ClientAPIError can handle various custom exception types.
    """
    class CustomNetworkError(Exception):
        def __init__(self, msg, code):
            self.message = msg
            self.status_code = code
            super().__init__(msg)

    custom_error = CustomNetworkError("Network Timeout", 504)
    client_error = ClientAPIError(custom_error)
    
    assert client_error.status_code == 504
    assert str(client_error) == "Network Timeout"


def test_client_api_error_str_representation():
    """
    Test the string representation of ClientAPIError.
    """
    error = ClientAPIError(ValueError("Some random error"))
    assert "Some random error" in str(error)