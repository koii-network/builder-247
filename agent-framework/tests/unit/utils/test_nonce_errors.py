"""Test suite for NonceError classes."""

import logging
import pytest
from prometheus_swarm.utils.errors import (
    NonceError, 
    NonceReplayError, 
    NonceExpirationError
)

def test_nonce_error_basic():
    """Test basic NonceError initialization and message."""
    error = NonceError("Test nonce error", error_type="test")
    assert str(error) == "Nonce Error [test]: Test nonce error"
    assert error.error_type == "test"

def test_nonce_replay_error():
    """Test NonceReplayError specific error type."""
    error = NonceReplayError("Duplicate nonce detected")
    assert str(error) == "Nonce Error [replay_attack]: Duplicate nonce detected"
    assert error.error_type == "replay_attack"

def test_nonce_expiration_error():
    """Test NonceExpirationError specific error type."""
    error = NonceExpirationError("Nonce has expired")
    assert str(error) == "Nonce Error [expired_nonce]: Nonce has expired"
    assert error.error_type == "expired_nonce"

def test_nonce_error_logging(caplog):
    """Test that NonceError logs an error message."""
    caplog.set_level(logging.ERROR)
    
    NonceError("Logging test", error_type="log_test")
    
    assert len(caplog.records) == 1
    log_record = caplog.records[0]
    assert log_record.levelno == logging.ERROR
    assert "Nonce Error [log_test]" in log_record.message

def test_nonce_errors_raise_exception():
    """Verify that nonce errors can be raised and caught."""
    with pytest.raises(NonceError):
        raise NonceError("Test raise", error_type="test_raise")
    
    with pytest.raises(NonceReplayError):
        raise NonceReplayError("Replay test")
    
    with pytest.raises(NonceExpirationError):
        raise NonceExpirationError("Expiration test")