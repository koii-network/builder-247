"""Unit tests for comprehensive error handling utilities."""

import pytest
import time
from prometheus_swarm.utils.error_handling import (
    BaseCustomError, 
    ValidationError, 
    ConfigurationError, 
    retry, 
    handle_errors,
    handle_context_errors
)

def test_base_custom_error():
    context = {'key': 'value'}
    original_error = ValueError("Original error")
    error = BaseCustomError(
        message="Test error", 
        context=context, 
        original_error=original_error
    )
    
    assert str(error) == "BaseCustomError: Test error\nContext: {'key': 'value', 'error_type': 'BaseCustomError'}"
    assert error.context['error_type'] == 'BaseCustomError'
    assert error.original_error == original_error

def test_validation_error():
    error = ValidationError("Invalid input", {'field': 'email'})
    
    assert isinstance(error, BaseCustomError)
    assert error.context['field'] == 'email'
    assert error.context['error_type'] == 'ValidationError'

def test_retry_decorator():
    @retry(max_attempts=3, exceptions=ValueError)
    def flaky_function(fail_count=[0]):
        fail_count[0] += 1
        if fail_count[0] < 3:
            raise ValueError("Simulated failure")
        return "Success"
    
    result = flaky_function()
    assert result == "Success"

def test_retry_decorator_max_attempts():
    @retry(max_attempts=2, exceptions=ValueError)
    def always_fail():
        raise ValueError("Always failing")
    
    with pytest.raises(ValueError):
        always_fail()

def test_handle_errors_raise():
    @handle_errors()
    def error_raising_function():
        raise RuntimeError("Test error")
    
    with pytest.raises(BaseCustomError) as excinfo:
        error_raising_function()
    
    assert "Test error" in str(excinfo.value)
    assert excinfo.value.context['function'] == 'error_raising_function'

def test_handle_errors_suppress():
    @handle_errors(raise_on_error=False, fallback_return="Fallback")
    def error_raising_function():
        raise RuntimeError("Test error")
    
    result = error_raising_function()
    assert result == "Fallback"

def test_handle_context_errors():
    def context_extractor(*args, **kwargs):
        return {'user_id': args[0]}

    @handle_context_errors(context_extractor)
    def process_user(user_id):
        if user_id <= 0:
            raise ValueError("Invalid user ID")
        return f"Processed user {user_id}"
    
    # Successful case
    result = process_user(123)
    assert result == "Processed user 123"

    # Error case
    with pytest.raises(BaseCustomError) as excinfo:
        process_user(0)
    
    error = excinfo.value
    assert "Invalid user ID" in str(error)
    assert error.context['user_id'] == 0