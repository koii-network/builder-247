"""
Unit tests for Transaction ID Time Window Configuration.
"""

import pytest
from datetime import timedelta
from prometheus_swarm.config.transaction_id import TransactionIDConfig

def test_default_time_window():
    """Test default time window configuration."""
    config = TransactionIDConfig()
    assert config.get_time_window() == timedelta(minutes=60)

def test_custom_time_window():
    """Test setting a custom time window."""
    config = TransactionIDConfig()
    config.set_time_window(30)
    assert config.get_time_window() == timedelta(minutes=30)

def test_invalid_time_window():
    """Test setting an invalid time window raises ValueError."""
    config = TransactionIDConfig()
    
    with pytest.raises(ValueError, match="Time window must be a positive number"):
        config.set_time_window(0)
    
    with pytest.raises(ValueError, match="Time window must be a positive number"):
        config.set_time_window(-10)

def test_reset_time_window():
    """Test resetting time window to default."""
    config = TransactionIDConfig()
    config.set_time_window(45)
    
    assert config.get_time_window() == timedelta(minutes=45)
    
    config.reset_time_window()
    assert config.get_time_window() == timedelta(minutes=60)

def test_float_time_window():
    """Test setting time window with float value."""
    config = TransactionIDConfig()
    config.set_time_window(30.5)
    assert config.get_time_window() == timedelta(minutes=30.5)