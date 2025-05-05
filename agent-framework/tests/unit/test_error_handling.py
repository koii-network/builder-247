"""Unit tests for error handling utilities."""

import pytest
from prometheus_swarm.utils.error_handling import (
    BasePrometheusError, ConfigurationError, AuthenticationError,
    ResourceNotFoundError, NetworkError, handle_and_log_errors, retry_on_error
)
import time

def test_base_prometheus_error():
    """Test BasePrometheusError creation."""
    context = {'user': 'test_user'}
    error = BasePrometheusError("Test error", context)
    
    error_str = str(error)
    assert "Test error" in error_str
    assert "user: test_user" in error_str

def test_specific_error_types():
    """Test specific error types."""
    errors = [
        (ConfigurationError, "Config issue"),
        (AuthenticationError, "Auth failed"),
        (ResourceNotFoundError, "Resource missing"),
        (NetworkError, "Network problem")
    ]
    
    for error_type, message in errors:
        error = error_type(message)
        assert isinstance(error, BasePrometheusError)
        assert message in str(error)
        assert len(str(error)) == len(message)

def test_handle_and_log_errors():
    """Test error handling decorator."""
    @handle_and_log_errors()
    def risky_function(should_fail=False):
        if should_fail:
            raise ValueError("Forced failure")
        return "Success"
    
    # Test successful execution
    assert risky_function() == "Success"
    
    # Test error handling
    with pytest.raises(BasePrometheusError) as excinfo:
        risky_function(should_fail=True)
    
    error_str = str(excinfo.value)
    assert "ValueError: Forced failure" in error_str
    assert "function: risky_function" in error_str
    assert "module: test_error_handling" in error_str

def test_retry_on_error():
    """Test retry decorator."""
    attempts = 0
    
    @retry_on_error(max_attempts=3, allowed_exceptions=(ValueError,))
    def unreliable_function():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ValueError("Not ready yet")
        return "Success"
    
    result = unreliable_function()
    assert result == "Success"
    assert attempts == 3

def test_retry_max_attempts_exceeded():
    """Test retry decorator with max attempts exceeded."""
    @retry_on_error(max_attempts=2, allowed_exceptions=(ValueError,))
    def always_failing_function():
        raise ValueError("Always fails")
    
    with pytest.raises(RuntimeError, match="Function always_failing_function failed after 2 attempts"):
        always_failing_function()