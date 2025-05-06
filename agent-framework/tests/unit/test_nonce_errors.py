"""Unit tests for NonceError in prometheus_swarm.utils.errors."""

import logging
import pytest
from prometheus_swarm.utils.errors import NonceError


def test_nonce_error_basic_creation():
    """Test basic NonceError creation with minimal parameters."""
    error = NonceError("Test message")
    assert str(error) == "[NONCE_ERROR] Test message"
    assert error.error_type == "NONCE_ERROR"
    assert error.context == {}


def test_nonce_error_with_context():
    """Test NonceError creation with context."""
    context = {"key1": "value1", "key2": 42}
    error = NonceError("Detailed error", context=context, error_type="CUSTOM_NONCE_ERROR")
    
    expected_str = ("[CUSTOM_NONCE_ERROR] Detailed error || "
                    "Context: key1: value1 | key2: 42")
    assert str(error) == expected_str
    assert error.error_type == "CUSTOM_NONCE_ERROR"
    assert error.context == context


def test_raise_for_invalid_nonce_type():
    """Test raising an error for incorrect nonce type."""
    with pytest.raises(NonceError) as excinfo:
        NonceError.raise_for_invalid_nonce("not_an_int", expected_type=int)
    
    error = excinfo.value
    assert "Invalid nonce type" in str(error)
    assert error.error_type == "NONCE_TYPE_ERROR"


def test_raise_for_invalid_nonce_min_value():
    """Test raising an error for nonce value below minimum."""
    with pytest.raises(NonceError) as excinfo:
        NonceError.raise_for_invalid_nonce(5, min_value=10)
    
    error = excinfo.value
    assert "Nonce value too low" in str(error)
    assert error.error_type == "NONCE_VALUE_TOO_LOW"


def test_raise_for_invalid_nonce_max_value():
    """Test raising an error for nonce value above maximum."""
    with pytest.raises(NonceError) as excinfo:
        NonceError.raise_for_invalid_nonce(15, max_value=10)
    
    error = excinfo.value
    assert "Nonce value too high" in str(error)
    assert error.error_type == "NONCE_VALUE_TOO_HIGH"


def test_nonce_error_log_method():
    """Test log method works with a mock logger."""
    # Create a mock logger
    mock_logger = logging.getLogger('test_logger')
    mock_logger.setLevel(logging.ERROR)
    
    # Create a handler that captures log records
    log_capture_handler = logging.Handler()
    log_records = []
    
    def capture_log_record(record):
        log_records.append(record)
    
    log_capture_handler.emit = capture_log_record
    mock_logger.addHandler(log_capture_handler)
    
    # Create and log an error
    error = NonceError("Test logging", error_type="LOG_TEST")
    error.log_error(mock_logger)
    
    # Verify the log record
    assert len(log_records) == 1
    assert "Test logging" in log_records[0].getMessage()