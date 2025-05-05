import pytest
from datetime import timedelta
from prometheus_swarm.utils.transaction_id_config import TransactionIDTimeWindowConfig


def test_default_config_creation():
    """Test creating a default TransactionIDTimeWindowConfig."""
    config = TransactionIDTimeWindowConfig()
    assert config.max_window_duration == timedelta(hours=24)
    assert config.min_window_duration == timedelta(minutes=1)
    assert config.default_window_duration == timedelta(hours=1)
    assert config.max_future_offset == timedelta(minutes=5)
    assert config.max_past_offset == timedelta(hours=24)


def test_validate_window_duration_success():
    """Test valid window duration validations."""
    config = TransactionIDTimeWindowConfig()
    
    # Test with timedelta
    assert config.validate_window_duration(timedelta(hours=1)) == timedelta(hours=1)
    
    # Test with int (seconds)
    assert config.validate_window_duration(3600) == timedelta(hours=1)


def test_validate_window_duration_exceeds_max():
    """Test validation fails when window duration exceeds maximum."""
    config = TransactionIDTimeWindowConfig()
    
    with pytest.raises(ValueError, match="Window duration exceeds maximum"):
        config.validate_window_duration(timedelta(days=2))


def test_validate_window_duration_below_min():
    """Test validation fails when window duration is below minimum."""
    config = TransactionIDTimeWindowConfig()
    
    with pytest.raises(ValueError, match="Window duration is less than minimum"):
        config.validate_window_duration(timedelta(seconds=30))


def test_get_window_duration():
    """Test getting window duration with and without custom input."""
    config = TransactionIDTimeWindowConfig()
    
    # Test default window duration
    assert config.get_window_duration() == timedelta(hours=1)
    
    # Test custom window duration
    assert config.get_window_duration(timedelta(hours=2)) == timedelta(hours=2)
    assert config.get_window_duration(7200) == timedelta(hours=2)


def test_custom_config():
    """Test creating a configuration with custom parameters."""
    config = TransactionIDTimeWindowConfig(
        max_window_duration=timedelta(hours=12),
        min_window_duration=timedelta(minutes=5),
        default_window_duration=timedelta(hours=2),
        max_future_offset=timedelta(minutes=10),
        max_past_offset=timedelta(hours=12)
    )
    
    assert config.max_window_duration == timedelta(hours=12)
    assert config.min_window_duration == timedelta(minutes=5)
    assert config.default_window_duration == timedelta(hours=2)
    assert config.max_future_offset == timedelta(minutes=10)
    assert config.max_past_offset == timedelta(hours=12)