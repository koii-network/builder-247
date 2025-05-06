import pytest
from datetime import timedelta
from prometheus_swarm.database.transaction_id_config import (
    TransactionIdRetentionConfig, 
    create_transaction_id_retention_config
)

def test_default_transaction_id_config():
    """Test default configuration settings."""
    config = TransactionIdRetentionConfig()
    assert config.max_retention_period is None
    assert config.max_transaction_count is None
    assert config.enabled is True

def test_transaction_id_config_with_period():
    """Test configuration with retention period."""
    period = timedelta(days=30)
    config = TransactionIdRetentionConfig(max_retention_period=period)
    assert config.max_retention_period == period
    assert config.enabled is True

def test_transaction_id_config_with_count():
    """Test configuration with transaction count limit."""
    config = TransactionIdRetentionConfig(max_transaction_count=1000)
    assert config.max_transaction_count == 1000
    assert config.enabled is True

def test_transaction_id_config_disabled():
    """Test configuration when disabled."""
    config = TransactionIdRetentionConfig(enabled=False)
    assert config.enabled is False

def test_invalid_retention_period_type():
    """Test invalid retention period type raises TypeError."""
    with pytest.raises(TypeError):
        TransactionIdRetentionConfig(max_retention_period="30 days")

def test_invalid_transaction_count_type():
    """Test invalid transaction count type raises TypeError."""
    with pytest.raises(TypeError):
        TransactionIdRetentionConfig(max_transaction_count="1000")

def test_negative_transaction_count():
    """Test negative transaction count raises ValueError."""
    with pytest.raises(ValueError):
        TransactionIdRetentionConfig(max_transaction_count=-100)

def test_create_transaction_id_config_factory():
    """Test factory function for creating configuration."""
    config = create_transaction_id_retention_config(
        max_retention_period=30,
        max_transaction_count=1000,
        enabled=True
    )
    assert isinstance(config.max_retention_period, timedelta)
    assert config.max_retention_period == timedelta(days=30)
    assert config.max_transaction_count == 1000
    assert config.enabled is True

def test_create_transaction_id_config_default():
    """Test factory function with default parameters."""
    config = create_transaction_id_retention_config()
    assert config.max_retention_period is None
    assert config.max_transaction_count is None
    assert config.enabled is True