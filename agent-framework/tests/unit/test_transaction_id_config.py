import pytest
from prometheus_swarm.transaction.config import TransactionIDTimeWindowConfig


def test_default_configuration():
    """Test default configuration values."""
    config = TransactionIDTimeWindowConfig()
    
    assert config.window_size_seconds == 3600
    assert config.max_unique_ids == 1000
    assert config.cleanup_interval_seconds == 300


def test_custom_configuration():
    """Test custom configuration with valid values."""
    config = TransactionIDTimeWindowConfig(
        window_size_seconds=7200,
        max_unique_ids=5000,
        cleanup_interval_seconds=600
    )
    
    assert config.window_size_seconds == 7200
    assert config.max_unique_ids == 5000
    assert config.cleanup_interval_seconds == 600


def test_get_configuration():
    """Test get_configuration method."""
    config = TransactionIDTimeWindowConfig(
        window_size_seconds=7200,
        max_unique_ids=5000,
        cleanup_interval_seconds=600
    )
    
    config_dict = config.get_configuration()
    
    assert config_dict == {
        "window_size_seconds": 7200,
        "max_unique_ids": 5000,
        "cleanup_interval_seconds": 600
    }


def test_invalid_window_size():
    """Test invalid window size."""
    with pytest.raises(ValueError):
        TransactionIDTimeWindowConfig(window_size_seconds=0)
    
    with pytest.raises(ValueError):
        TransactionIDTimeWindowConfig(window_size_seconds=100000)


def test_invalid_max_unique_ids():
    """Test invalid max unique IDs."""
    with pytest.raises(ValueError):
        TransactionIDTimeWindowConfig(max_unique_ids=0)
    
    with pytest.raises(ValueError):
        TransactionIDTimeWindowConfig(max_unique_ids=20000)


def test_invalid_cleanup_interval():
    """Test invalid cleanup interval."""
    with pytest.raises(ValueError):
        TransactionIDTimeWindowConfig(cleanup_interval_seconds=0)
    
    with pytest.raises(ValueError):
        TransactionIDTimeWindowConfig(cleanup_interval_seconds=5000)


def test_cleanup_interval_exceeds_window_size():
    """Test cleanup interval larger than window size."""
    with pytest.raises(ValueError):
        TransactionIDTimeWindowConfig(
            window_size_seconds=3600,
            cleanup_interval_seconds=7200
        )