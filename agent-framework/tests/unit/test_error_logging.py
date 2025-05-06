"""Unit tests for error handling and logging utilities."""

import logging
import pytest
from prometheus_swarm.utils.errors import (
    BaseSwarmError, 
    ClientAPIError, 
    ConfigurationError, 
    handle_and_log_error
)
from prometheus_swarm.utils.logging import configure_logging, log_exception, performance_log

def test_base_swarm_error():
    """Test BaseSwarmError initialization and to_dict method."""
    error = BaseSwarmError(
        message="Test error", 
        error_code="TEST_ERROR",
        context={"test_key": "test_value"}
    )
    
    error_dict = error.to_dict()
    
    assert error_dict["error_code"] == "TEST_ERROR"
    assert error_dict["message"] == "Test error"
    assert error_dict["context"]["test_key"] == "test_value"
    assert "traceback" in error_dict

def test_client_api_error():
    """Test ClientAPIError with various initialization scenarios."""
    # String-based error
    error1 = ClientAPIError("Connection failed", status_code=404)
    assert error1.status_code == 404
    assert "Connection failed" in str(error1)

    # Exception-based error
    try:
        raise ValueError("Original error")
    except ValueError as ve:
        error2 = ClientAPIError(ve, status_code=500, service="test_service")
    
    assert error2.status_code == 500
    assert "Original error" in str(error2)
    assert error2.to_dict()["context"]["service"] == "test_service"

def test_configuration_error():
    """Test ConfigurationError with context."""
    error = ConfigurationError(
        message="Invalid configuration", 
        config_key="test_config",
        expected_value="expected_value"
    )
    
    error_dict = error.to_dict()
    assert error_dict["error_code"] == "CONFIGURATION_ERROR"
    assert error_dict["context"]["config_key"] == "test_config"
    assert error_dict["context"]["expected_value"] == "expected_value"

def test_error_handling_and_logging(caplog):
    """Test error handling and logging integration."""
    logger = configure_logging(log_level=logging.DEBUG)

    def raise_error():
        raise ValueError("Test error")

    try:
        raise_error()
    except Exception as e:
        error_dict = handle_and_log_error(e, logger=logger)
        
        assert "error_code" in error_dict
        # Check logging occurred
        assert any("Test error" in record.message for record in caplog.records)

def test_log_exception(caplog):
    """Test exception logging utility."""
    logger = configure_logging(log_level=logging.DEBUG)

    try:
        raise RuntimeError("Test runtime error")
    except Exception as e:
        log_exception(logger, e, {"additional_context": "value"})
    
    # Verify logging
    records = [record for record in caplog.records if record.levelno == logging.ERROR]
    assert len(records) > 0
    assert "Test runtime error" in records[0].message
    assert "additional_context" in records[0].message

@performance_log
def dummy_function(x: int) -> int:
    """A dummy function for performance logging test."""
    return x * 2

def test_performance_log(caplog):
    """Test performance logging decorator."""
    logger = configure_logging(log_level=logging.INFO)
    
    result = dummy_function(21)
    
    assert result == 42
    
    # Verify performance logging occurred
    performance_records = [
        record for record in caplog.records 
        if "function_performance" in record.message
    ]
    assert len(performance_records) > 0