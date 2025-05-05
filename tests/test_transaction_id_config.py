import pytest
from datetime import timedelta
from src.transaction_id_config import TransactionIDTimeWindowConfig


def test_default_initialization():
    """Test initialization with no specific configurations."""
    config = TransactionIDTimeWindowConfig()
    assert config.max_time_window is None
    assert config.min_time_window is None
    assert config.default_time_window is None


def test_initialization_with_timedelta():
    """Test initialization with timedelta inputs."""
    max_window = timedelta(hours=1)
    min_window = timedelta(minutes=5)
    default_window = timedelta(minutes=30)

    config = TransactionIDTimeWindowConfig(
        max_time_window=max_window,
        min_time_window=min_window,
        default_time_window=default_window
    )

    assert config.max_time_window == max_window
    assert config.min_time_window == min_window
    assert config.default_time_window == default_window


def test_initialization_with_integers():
    """Test initialization with integer (seconds) inputs."""
    max_window = 3600  # 1 hour
    min_window = 300   # 5 minutes
    default_window = 1800  # 30 minutes

    config = TransactionIDTimeWindowConfig(
        max_time_window=max_window,
        min_time_window=min_window,
        default_time_window=default_window
    )

    assert config.max_time_window == timedelta(seconds=max_window)
    assert config.min_time_window == timedelta(seconds=min_window)
    assert config.default_time_window == timedelta(seconds=default_window)


def test_invalid_time_window_configuration():
    """Test that invalid time window configurations raise ValueError."""
    with pytest.raises(ValueError, match="Max time window must be greater than or equal to min time window"):
        TransactionIDTimeWindowConfig(
            max_time_window=timedelta(minutes=10),
            min_time_window=timedelta(minutes=30)
        )


def test_get_time_window_with_defaults():
    """Test get_time_window method with default configurations."""
    config = TransactionIDTimeWindowConfig(
        max_time_window=timedelta(hours=1),
        min_time_window=timedelta(minutes=5),
        default_time_window=timedelta(minutes=30)
    )

    # No specific window requested, should return default
    assert config.get_time_window() == timedelta(minutes=30)


def test_get_time_window_with_validation():
    """Test get_time_window method with validation."""
    config = TransactionIDTimeWindowConfig(
        max_time_window=timedelta(hours=1),
        min_time_window=timedelta(minutes=5),
        default_time_window=timedelta(minutes=30)
    )

    # Within bounds
    assert config.get_time_window(timedelta(minutes=15)) == timedelta(minutes=15)

    # Below min window
    assert config.get_time_window(timedelta(minutes=2)) == timedelta(minutes=5)

    # Above max window
    assert config.get_time_window(timedelta(hours=2)) == timedelta(hours=1)


def test_unsupported_type_raises_error():
    """Test that unsupported types raise TypeError."""
    config = TransactionIDTimeWindowConfig()

    with pytest.raises(TypeError, match="Unsupported type for time window"):
        config.get_time_window("not a valid type")  # type: ignore