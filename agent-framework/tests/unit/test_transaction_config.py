"""
Unit tests for TransactionTimeWindowConfig
"""

import pytest
from datetime import datetime, timedelta
from prometheus_swarm.utils.transaction_config import TransactionTimeWindowConfig


def test_default_configuration():
    """Test default configuration initialization"""
    config = TransactionTimeWindowConfig()
    assert config.window_size == timedelta(hours=1)
    assert config.max_transactions is None


def test_window_size_configuration():
    """Test various window size configurations"""
    # Integer seconds
    config1 = TransactionTimeWindowConfig(window_size=3600)
    assert config1.window_size == timedelta(hours=1)

    # Timedelta
    config2 = TransactionTimeWindowConfig(window_size=timedelta(minutes=30))
    assert config2.window_size == timedelta(minutes=30)

    # Max transactions
    config3 = TransactionTimeWindowConfig(max_transactions=5)
    assert config3.max_transactions == 5


def test_invalid_configurations():
    """Test invalid configuration initializations"""
    # Negative window size (int)
    with pytest.raises(ValueError, match="Window size cannot be negative"):
        TransactionTimeWindowConfig(window_size=-3600)

    # Negative window size (timedelta)
    with pytest.raises(ValueError, match="Window size cannot be negative"):
        TransactionTimeWindowConfig(window_size=timedelta(seconds=-3600))

    # Negative max transactions
    with pytest.raises(ValueError, match="Maximum transactions cannot be negative"):
        TransactionTimeWindowConfig(max_transactions=-1)

    # Invalid window size type
    with pytest.raises(TypeError, match="window_size must be int, timedelta, or None"):
        TransactionTimeWindowConfig(window_size="invalid")


def test_is_within_window():
    """Test is_within_window method"""
    config = TransactionTimeWindowConfig(window_size=timedelta(hours=1))
    current_time = datetime(2023, 1, 1, 12, 0, 0)

    # Transaction within the window
    within_transaction = datetime(2023, 1, 1, 11, 0, 0)
    assert config.is_within_window(within_transaction, current_time) is True

    # Transaction outside the window
    outside_transaction = datetime(2023, 1, 1, 10, 59, 59)
    assert config.is_within_window(outside_transaction, current_time) is False


def test_validate_transaction_count():
    """Test validate_transaction_count method"""
    config = TransactionTimeWindowConfig(
        window_size=timedelta(hours=1), 
        max_transactions=3
    )
    current_time = datetime(2023, 1, 1, 12, 0, 0)

    # Transactions within window and count limit
    valid_transactions = [
        datetime(2023, 1, 1, 11, 0, 0),
        datetime(2023, 1, 1, 11, 15, 0),
        datetime(2023, 1, 1, 11, 30, 0)
    ]
    assert config.validate_transaction_count(valid_transactions, current_time) is True

    # Transactions exceeding count limit
    invalid_transactions = valid_transactions + [
        datetime(2023, 1, 1, 11, 45, 0)
    ]
    assert config.validate_transaction_count(invalid_transactions, current_time) is False

    # Unlimited transactions
    unlimited_config = TransactionTimeWindowConfig(window_size=timedelta(hours=1))
    many_transactions = [
        datetime(2023, 1, 1, 11, 0, 0) for _ in range(100)
    ]
    assert unlimited_config.validate_transaction_count(many_transactions, current_time) is True