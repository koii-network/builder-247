"""Unit tests for Nonce Error Handling."""

import logging
import pytest
from prometheus_swarm.utils.errors import NonceError, validate_nonce


def test_nonce_error_basic():
    """Test basic NonceError instantiation."""
    with pytest.raises(NonceError) as exc_info:
        raise NonceError("Test nonce error")
    
    assert str(exc_info.value) == "Test nonce error"


def test_nonce_error_with_context():
    """Test NonceError with additional context."""
    context = {"user_id": 123, "timestamp": "2023-01-01"}
    with pytest.raises(NonceError) as exc_info:
        raise NonceError("Detailed error", context)
    
    assert str(exc_info.value) == "Detailed error"
    assert exc_info.value.context == context


def test_validate_nonce_type():
    """Test nonce type validation."""
    # Should pass for integers
    validate_nonce(42)
    validate_nonce(0)

    # Should raise for invalid types
    with pytest.raises(NonceError) as exc_info:
        validate_nonce("not an int")
    
    assert "Invalid nonce type" in str(exc_info.value)


def test_validate_nonce_min_value():
    """Test nonce minimum value validation."""
    validate_nonce(100, min_value=50)

    with pytest.raises(NonceError) as exc_info:
        validate_nonce(10, min_value=50)
    
    assert "Nonce value too small" in str(exc_info.value)


def test_validate_nonce_none():
    """Test behavior with None nonce."""
    with pytest.raises(NonceError) as exc_info:
        validate_nonce(None)
    
    assert "Nonce cannot be None" in str(exc_info.value)


def test_nonce_error_logging(caplog):
    """Test logging behavior of NonceError."""
    caplog.set_level(logging.DEBUG)

    with pytest.raises(NonceError):
        raise NonceError("Logging test", {"test": True}, log_level=logging.WARNING)
    
    assert "Logging test" in caplog.text
    assert "Context: {'test': True}" in caplog.text