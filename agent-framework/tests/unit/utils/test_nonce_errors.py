"""Tests for nonce error handling and recovery."""

import logging
import pytest
from prometheus_swarm.utils.errors import NonceError, nonce_error_handler


def test_nonce_error_initialization():
    """Test NonceError can be created with message and optional nonce."""
    error = NonceError("Invalid nonce", "abc123")
    assert str(error) == "Invalid nonce"
    assert error.current_nonce == "abc123"


def test_nonce_error_without_nonce():
    """Test NonceError can be created without specifying a nonce."""
    error = NonceError("Nonce reused")
    assert str(error) == "Nonce reused"
    assert error.current_nonce is None


def test_nonce_error_handler_success():
    """Test nonce error handler successfully recovers from nonce errors."""
    mock_attempts = [0]

    @nonce_error_handler
    def mock_function():
        mock_attempts[0] += 1
        if mock_attempts[0] < 3:
            raise NonceError("Simulated nonce error")
        return "Success"

    result = mock_function()
    assert result == "Success"
    assert mock_attempts[0] == 3


def test_nonce_error_handler_max_retries():
    """Test nonce error handler raises error after max retries."""
    @nonce_error_handler(max_retries=2)
    def mock_function():
        raise NonceError("Persistent nonce error")

    with pytest.raises(RuntimeError, match="Max nonce error retries exceeded"):
        mock_function()


def test_nonce_error_handler_with_logger(caplog):
    """Test nonce error handler works with a logger."""
    caplog.set_level(logging.WARNING)

    @nonce_error_handler(logger=logging.getLogger())
    def mock_function():
        raise NonceError("Logged nonce error")

    with pytest.raises(RuntimeError):
        mock_function()

    assert "Nonce error encountered: Logged nonce error" in caplog.text