"""Test suite for error handling and logging utilities."""

import logging
import pytest
from prometheus_swarm.utils.errors import (
    PrometheusBaseError, 
    ConfigurationError, 
    NetworkError, 
    AuthenticationError, 
    ErrorSeverity,
    handle_error
)
from prometheus_swarm.utils.logging import log_error, log_structured

def test_prometheus_base_error():
    """Test basic PrometheusBaseError creation and properties."""
    context = {"service": "test", "id": 123}
    error = PrometheusBaseError(
        "Test error", 
        context=context, 
        severity=ErrorSeverity.MEDIUM
    )
    
    assert str(error) is not None
    assert "Test error" in str(error)
    assert error.context == context
    assert error.severity == ErrorSeverity.MEDIUM

def test_configuration_error():
    """Test ConfigurationError creation."""
    config = {"host": "localhost", "port": 8080}
    error = ConfigurationError("Invalid configuration", config)
    
    assert error.severity == ErrorSeverity.HIGH
    assert error.context == config
    assert "Invalid configuration" in str(error)

def test_network_error():
    """Test NetworkError creation."""
    error = NetworkError("Connection failed", host="example.com", port=443)
    
    assert error.severity == ErrorSeverity.HIGH
    assert error.context.get("host") == "example.com"
    assert error.context.get("port") == 443

def test_authentication_error():
    """Test AuthenticationError creation."""
    error = AuthenticationError("Invalid credentials", username="testuser")
    
    assert error.severity == ErrorSeverity.CRITICAL
    assert error.context.get("username") == "testuser"

def test_error_handler(caplog):
    """Test the error handling decorator."""
    logger = logging.getLogger('test_logger')
    
    @handle_error(
        logger, 
        default_message="Custom error message", 
        default_severity=ErrorSeverity.LOW
    )
    def test_function(raise_error=False):
        if raise_error:
            raise ValueError("Test error")
        return "Success"
    
    # Test successful execution
    result = test_function()
    assert result == "Success"
    
    # Test error handling
    with pytest.raises(PrometheusBaseError) as excinfo:
        test_function(raise_error=True)
    
    error = excinfo.value
    assert str(error) == "Custom error message"
    assert error.severity == ErrorSeverity.LOW
    assert "test_function" in str(error)

def test_log_error(caplog):
    """Test log_error function with various error types."""
    logger = logging.getLogger('test_logger')
    
    # Test with simple exception
    try:
        raise ValueError("Simple test error")
    except Exception as e:
        log_error(e, logger=logger)
        assert "Simple test error" in caplog.text
    
    caplog.clear()
    
    # Test with PrometheusBaseError
    custom_error = PrometheusBaseError(
        "Custom error", 
        context={"source": "test"},
        severity=ErrorSeverity.HIGH
    )
    log_error(custom_error, logger=logger)
    
    assert "Custom error" in caplog.text
    assert "Error Severity: HIGH" in caplog.text
    assert "source: test" in caplog.text

def test_log_structured(caplog):
    """Test log_structured for JSON-like logging."""
    logger = logging.getLogger('test_logger')
    
    log_structured(
        "Performance log", 
        data={"duration": 0.5, "status": "completed"},
        logger=logger
    )
    
    # Verify log contents
    assert "Performance log" in caplog.text
    assert "duration" in caplog.text
    assert "status" in caplog.text