"""
Unit tests for TransactionIDSettings.
"""
import pytest
import time
from prometheus_swarm.utils.transaction_settings import TransactionIDSettings


def test_default_initialization():
    """Test default settings initialization."""
    settings = TransactionIDSettings()
    assert settings.time_window == 3600
    assert settings.max_stored_transactions == 1000


def test_custom_initialization():
    """Test custom settings initialization."""
    settings = TransactionIDSettings(time_window=1800, max_stored_transactions=500)
    assert settings.time_window == 1800
    assert settings.max_stored_transactions == 500


def test_invalid_time_window():
    """Test that negative time window raises ValueError."""
    with pytest.raises(ValueError, match="Time window must be non-negative"):
        TransactionIDSettings(time_window=-100)


def test_invalid_max_transactions():
    """Test that non-positive max transactions raises ValueError."""
    with pytest.raises(ValueError, match="Maximum stored transactions must be positive"):
        TransactionIDSettings(max_stored_transactions=0)


def test_add_transaction():
    """Test adding unique transactions."""
    settings = TransactionIDSettings(time_window=5, max_stored_transactions=3)
    
    assert settings.add_transaction("tx1") is True
    assert settings.add_transaction("tx2") is True
    assert settings.add_transaction("tx1") is False  # Duplicate transaction


def test_transaction_validation():
    """Test transaction validation within time window."""
    settings = TransactionIDSettings(time_window=2, max_stored_transactions=10)
    
    settings.add_transaction("tx1")
    assert settings.is_transaction_valid("tx1") is True
    
    time.sleep(3)  # Wait beyond time window
    assert settings.is_transaction_valid("tx1") is False


def test_max_transactions_limit():
    """Test max transactions limit."""
    settings = TransactionIDSettings(time_window=10, max_stored_transactions=2)
    
    assert settings.add_transaction("tx1") is True
    assert settings.add_transaction("tx2") is True
    assert settings.add_transaction("tx3") is False  # Exceeds limit


def test_automatic_cleanup():
    """Test automatic cleanup of expired transactions."""
    settings = TransactionIDSettings(time_window=1, max_stored_transactions=10)
    
    settings.add_transaction("tx1")
    time.sleep(2)  # Wait beyond time window
    
    # Adding a new transaction should trigger cleanup
    settings.add_transaction("tx2")
    
    assert settings.is_transaction_valid("tx1") is False
    assert settings.is_transaction_valid("tx2") is True