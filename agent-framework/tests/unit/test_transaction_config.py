"""
Unit tests for Transaction ID Time Window Configuration.
"""

import pytest
from datetime import timedelta
from prometheus_swarm.database.transaction_config import TransactionIDTimeWindowConfig


def test_transaction_config_default_initialization():
    """Test default initialization of TransactionIDTimeWindowConfig."""
    config = TransactionIDTimeWindowConfig()
    assert config.max_window_duration == timedelta(hours=24)
    assert config.min_window_duration == timedelta(minutes=5)
    assert config.default_window_duration == timedelta(hours=1)


def test_transaction_config_custom_initialization():
    """Test custom initialization of TransactionIDTimeWindowConfig."""
    config = TransactionIDTimeWindowConfig(
        max_window_duration=timedelta(hours=48),
        min_window_duration=timedelta(minutes=10),
        default_window_duration=timedelta(hours=2)
    )
    assert config.max_window_duration == timedelta(hours=48)
    assert config.min_window_duration == timedelta(minutes=10)
    assert config.default_window_duration == timedelta(hours=2)


def test_transaction_config_integer_initialization():
    """Test initialization with integer seconds."""
    config = TransactionIDTimeWindowConfig(
        max_window_duration=48 * 3600,  # 48 hours in seconds
        min_window_duration=600,  # 10 minutes in seconds
        default_window_duration=7200  # 2 hours in seconds
    )
    assert config.max_window_duration == timedelta(hours=48)
    assert config.min_window_duration == timedelta(minutes=10)
    assert config.default_window_duration == timedelta(hours=2)


def test_transaction_config_invalid_configurations():
    """Test invalid time window configurations."""
    with pytest.raises(ValueError, match="Minimum window duration cannot exceed maximum window duration"):
        TransactionIDTimeWindowConfig(
            max_window_duration=timedelta(hours=1),
            min_window_duration=timedelta(hours=2)
        )

    with pytest.raises(ValueError, match="Default window duration cannot be less than minimum window duration"):
        TransactionIDTimeWindowConfig(
            min_window_duration=timedelta(hours=2),
            default_window_duration=timedelta(hours=1)
        )

    with pytest.raises(ValueError, match="Default window duration cannot exceed maximum window duration"):
        TransactionIDTimeWindowConfig(
            max_window_duration=timedelta(hours=1),
            default_window_duration=timedelta(hours=2)
        )


def test_validate_window_duration():
    """Test window duration validation."""
    config = TransactionIDTimeWindowConfig()

    # Valid window durations
    assert config.validate_window_duration(timedelta(minutes=10)) == timedelta(minutes=10)
    assert config.validate_window_duration(600) == timedelta(minutes=10)  # 10 minutes in seconds

    # Invalid window durations
    with pytest.raises(ValueError, match="Window duration must be at least"):
        config.validate_window_duration(timedelta(minutes=1))

    with pytest.raises(ValueError, match="Window duration cannot exceed"):
        config.validate_window_duration(timedelta(days=2))


def test_get_default_window_duration():
    """Test getting default window duration."""
    config = TransactionIDTimeWindowConfig()
    assert config.get_default_window_duration() == timedelta(hours=1)

    custom_config = TransactionIDTimeWindowConfig(default_window_duration=timedelta(hours=4))
    assert custom_config.get_default_window_duration() == timedelta(hours=4)