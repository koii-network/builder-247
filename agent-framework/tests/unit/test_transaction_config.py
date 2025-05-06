"""
Unit tests for the TransactionIDConfig utility.

This test suite validates the behavior of the TransactionIDConfig class
and ensures proper time window and transaction limit management.
"""

import time
import pytest
from prometheus_swarm.utils.transaction_config import TransactionIDConfig


def test_default_initialization():
    """Test default configuration initialization."""
    config = TransactionIDConfig()
    assert config.get_time_window() == 60.0
    assert config.get_max_transactions() is None


def test_custom_initialization():
    """Test custom configuration initialization."""
    config = TransactionIDConfig(time_window=30.0, max_transactions=5)
    assert config.get_time_window() == 30.0
    assert config.get_max_transactions() == 5


def test_invalid_time_window_initialization():
    """Test initialization with invalid time window raises ValueError."""
    with pytest.raises(ValueError, match="Time window must be a positive number"):
        TransactionIDConfig(time_window=-10)
    with pytest.raises(ValueError, match="Time window must be a positive number"):
        TransactionIDConfig(time_window=0)


def test_set_time_window():
    """Test setting time window dynamically."""
    config = TransactionIDConfig()
    config.set_time_window(45.0)
    assert config.get_time_window() == 45.0

    with pytest.raises(ValueError, match="Time window must be a positive number"):
        config.set_time_window(-10)


def test_set_max_transactions():
    """Test setting max transactions dynamically."""
    config = TransactionIDConfig()
    config.set_max_transactions(3)
    assert config.get_max_transactions() == 3

    with pytest.raises(ValueError, match="Max transactions must be a positive integer"):
        config.set_max_transactions(-1)


def test_transaction_allowed_within_window():
    """Test transactions are allowed within time window."""
    config = TransactionIDConfig(time_window=1.0, max_transactions=3)
    
    for _ in range(3):
        assert config.is_transaction_allowed() is True


def test_transaction_limit_exceeded():
    """Test transactions are blocked when max is exceeded."""
    config = TransactionIDConfig(time_window=1.0, max_transactions=2)
    
    assert config.is_transaction_allowed() is True
    assert config.is_transaction_allowed() is True
    assert config.is_transaction_allowed() is False


def test_transaction_window_expiry():
    """Test transactions outside time window are removed."""
    config = TransactionIDConfig(time_window=0.5, max_transactions=3)
    
    # Simulate transactions
    assert config.is_transaction_allowed() is True
    assert config.is_transaction_allowed() is True
    
    # Wait beyond time window
    time.sleep(0.6)
    
    # Should allow new transactions after window expiry
    assert config.is_transaction_allowed() is True