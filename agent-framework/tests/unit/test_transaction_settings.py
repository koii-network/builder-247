"""
Unit tests for Transaction ID Time Window Configuration.
"""

import pytest
import time
from prometheus_swarm.utils.transaction_settings import (
    configure_transaction_id_time_window,
    TransactionIDTimeWindowError
)


def test_default_configuration():
    """Test default configuration settings."""
    config = configure_transaction_id_time_window()
    
    assert config['window_duration'] == 3600
    assert config['max_transactions'] is None
    assert config['allow_overlapping'] is False
    assert isinstance(config['created_at'], int)


def test_custom_configuration():
    """Test custom configuration settings."""
    config = configure_transaction_id_time_window(
        window_duration=7200,
        max_transactions=10,
        allow_overlapping=True
    )
    
    assert config['window_duration'] == 7200
    assert config['max_transactions'] == 10
    assert config['allow_overlapping'] is True
    assert isinstance(config['created_at'], int)


def test_invalid_window_duration():
    """Test invalid window duration raises error."""
    with pytest.raises(TransactionIDTimeWindowError, match="Window duration must be a positive integer."):
        configure_transaction_id_time_window(window_duration=0)
    
    with pytest.raises(TransactionIDTimeWindowError, match="Window duration must be a positive integer."):
        configure_transaction_id_time_window(window_duration=-100)


def test_invalid_max_transactions():
    """Test invalid max transactions raises error."""
    with pytest.raises(TransactionIDTimeWindowError, match="Max transactions must be a positive integer or None."):
        configure_transaction_id_time_window(max_transactions=0)
    
    with pytest.raises(TransactionIDTimeWindowError, match="Max transactions must be a positive integer or None."):
        configure_transaction_id_time_window(max_transactions=-10)


def test_created_at_timestamp():
    """Test created_at timestamp is current time."""
    current_time = int(time.time())
    config = configure_transaction_id_time_window()
    
    assert abs(config['created_at'] - current_time) < 2  # Allow 2 seconds difference