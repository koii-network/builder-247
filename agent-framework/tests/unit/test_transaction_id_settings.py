"""
Unit tests for Transaction ID Time Window Settings.
"""

import pytest
import time
from prometheus_swarm.tools.transaction_id_settings import TransactionIDTimeWindowSettings


def test_default_initialization():
    """Test default initialization of TransactionIDTimeWindowSettings."""
    settings = TransactionIDTimeWindowSettings()
    assert settings.get_time_window() == 3600  # Default 1 hour
    assert settings.default_time_window == 3600
    assert settings.max_time_window == 86400
    assert settings.min_time_window == 60


def test_custom_initialization():
    """Test custom initialization of time window settings."""
    settings = TransactionIDTimeWindowSettings(
        default_time_window=7200,  # 2 hours
        max_time_window=172800,    # 48 hours
        min_time_window=300        # 5 minutes
    )
    assert settings.get_time_window() == 7200
    assert settings.default_time_window == 7200
    assert settings.max_time_window == 172800
    assert settings.min_time_window == 300


def test_invalid_initialization():
    """Test invalid initialization raises ValueError."""
    with pytest.raises(ValueError):
        TransactionIDTimeWindowSettings(
            default_time_window=50000,  # Exceeds max
            max_time_window=40000,
            min_time_window=10
        )


def test_set_time_window():
    """Test setting time window within valid range."""
    settings = TransactionIDTimeWindowSettings()
    settings.set_time_window(1800)  # 30 minutes
    assert settings.get_time_window() == 1800


def test_set_time_window_invalid():
    """Test setting time window outside valid range raises ValueError."""
    settings = TransactionIDTimeWindowSettings()
    with pytest.raises(ValueError):
        settings.set_time_window(100000)  # Exceeds max
    
    with pytest.raises(ValueError):
        settings.set_time_window(10)  # Below min


def test_reset_to_default():
    """Test resetting time window to default."""
    settings = TransactionIDTimeWindowSettings()
    settings.set_time_window(1800)
    settings.reset_to_default()
    assert settings.get_time_window() == 3600


def test_is_transaction_id_valid():
    """Test transaction ID validation."""
    settings = TransactionIDTimeWindowSettings(default_time_window=60)  # 1 minute window
    
    # Valid transaction (just within time window)
    valid_timestamp = time.time() - 30  # 30 seconds ago
    assert settings.is_transaction_id_valid("transaction1", valid_timestamp)
    
    # Invalid transaction (outside time window)
    invalid_timestamp = time.time() - 120  # 2 minutes ago
    assert not settings.is_transaction_id_valid("transaction2", invalid_timestamp)
    
    # Empty transaction ID
    assert not settings.is_transaction_id_valid("")
    assert not settings.is_transaction_id_valid(None)


def test_is_transaction_id_valid_no_timestamp():
    """Test transaction ID validation without explicit timestamp."""
    settings = TransactionIDTimeWindowSettings(default_time_window=60)
    
    # This should pass as it uses current time
    assert settings.is_transaction_id_valid("transaction")