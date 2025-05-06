import pytest
from prometheus_swarm.database.transaction_config import (
    TransactionIDRetentionConfig, 
    create_default_transaction_config
)

def test_default_transaction_config():
    """Test the default transaction configuration."""
    config = create_default_transaction_config()
    
    # Check default values
    assert config.max_retention_count == 1000
    assert config.max_retention_days is None
    assert config.enable_cleanup is True
    assert config.priority_preserve_types == []

def test_transaction_config_validation():
    """Test validation of transaction configuration."""
    # Valid configurations
    valid_configs = [
        TransactionIDRetentionConfig(),
        TransactionIDRetentionConfig(max_retention_count=500),
        TransactionIDRetentionConfig(max_retention_days=30),
        TransactionIDRetentionConfig(priority_preserve_types=['critical', 'high'])
    ]
    
    for config in valid_configs:
        assert config.validate() is True

def test_transaction_config_invalid_validation():
    """Test invalid transaction configurations."""
    # Invalid configurations
    invalid_configs = [
        TransactionIDRetentionConfig(max_retention_count=-1),
        TransactionIDRetentionConfig(max_retention_days=-5)
    ]
    
    for config in invalid_configs:
        assert config.validate() is False

def test_transaction_config_retention_limit():
    """Test retention limit getter."""
    # When cleanup is enabled
    config1 = TransactionIDRetentionConfig(max_retention_count=100)
    assert config1.get_retention_limit() == 100

    # When cleanup is disabled
    config2 = TransactionIDRetentionConfig(max_retention_count=100, enable_cleanup=False)
    assert config2.get_retention_limit() is None

def test_transaction_config_priority_preserve():
    """Test setting and checking priority preserve types."""
    config = TransactionIDRetentionConfig(priority_preserve_types=['critical', 'high'])
    
    assert 'critical' in config.priority_preserve_types
    assert 'high' in config.priority_preserve_types
    assert len(config.priority_preserve_types) == 2