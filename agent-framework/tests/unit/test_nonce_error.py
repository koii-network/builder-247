import pytest
import logging
import time
from prometheus_swarm.utils.nonce_error import (
    NonceError, 
    validate_nonce, 
    handle_nonce_error
)

# Mock logger for testing
class MockLogger:
    def __init__(self):
        self.warnings = []
        self.errors = []
    
    def warning(self, msg):
        self.warnings.append(msg)
    
    def error(self, msg):
        self.errors.append(msg)

def test_nonce_validation():
    """Test nonce validation function."""
    assert validate_nonce(None) == False
    assert validate_nonce("") == False
    assert validate_nonce("valid_nonce") == True
    assert validate_nonce("a" * 64) == True
    assert validate_nonce("a" * 65) == False

def test_nonce_error_initialization():
    """Test NonceError initialization."""
    error = NonceError("Test message", "test_nonce")
    assert str(error) == "Test message"
    assert error.nonce == "test_nonce"

def test_handle_nonce_error_successful_call():
    """Test successful function call with nonce decorator."""
    mock_logger = MockLogger()

    @handle_nonce_error(max_retries=3, logger=mock_logger)
    def valid_function(nonce):
        if not validate_nonce(nonce):
            raise NonceError("Invalid nonce")
        return "Success"

    result = valid_function("good_nonce")
    assert result == "Success"
    assert len(mock_logger.warnings) == 0
    assert len(mock_logger.errors) == 0

def test_handle_nonce_error_retry():
    """Test nonce error handling with retries."""
    mock_logger = MockLogger()
    call_count = 0

    @handle_nonce_error(max_retries=3, retry_delay=0.1, logger=mock_logger)
    def flaky_function(nonce):
        nonlocal call_count
        call_count += 1
        if call_count <= 2:
            raise NonceError("Simulated nonce failure")
        return "Success"

    result = flaky_function("retry_nonce")
    assert result == "Success"
    assert call_count == 3
    assert len(mock_logger.warnings) == 2
    assert len(mock_logger.errors) == 0

def test_handle_nonce_error_max_retries():
    """Test nonce error handling with maximum retries exceeded."""
    mock_logger = MockLogger()

    @handle_nonce_error(max_retries=2, retry_delay=0.1, logger=mock_logger)
    def always_failing_function(nonce):
        raise NonceError("Always fails")

    with pytest.raises(NonceError):
        always_failing_function("bad_nonce")
    
    assert len(mock_logger.warnings) == 2
    assert len(mock_logger.errors) == 1