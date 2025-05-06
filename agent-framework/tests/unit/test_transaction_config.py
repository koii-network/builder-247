import pytest
from prometheus_swarm.database.transaction_config import TransactionIDRetentionConfig

def test_default_config():
    """Test default configuration initialization."""
    config = TransactionIDRetentionConfig()
    cfg = config.get_config()
    
    assert cfg['max_retention_time'] == 86400
    assert cfg['max_stored_ids'] == 1000
    assert cfg['retention_strategy'] == 'oldest'

def test_custom_config():
    """Test custom configuration initialization."""
    config = TransactionIDRetentionConfig(
        max_retention_time=3600,  # 1 hour
        max_stored_ids=500,
        retention_strategy='newest'
    )
    cfg = config.get_config()
    
    assert cfg['max_retention_time'] == 3600
    assert cfg['max_stored_ids'] == 500
    assert cfg['retention_strategy'] == 'newest'

def test_config_update():
    """Test updating configuration."""
    config = TransactionIDRetentionConfig()
    
    # Update config partially
    config.update_config(
        max_retention_time=7200,  # 2 hours
        retention_strategy='newest'
    )
    
    cfg = config.get_config()
    assert cfg['max_retention_time'] == 7200
    assert cfg['max_stored_ids'] == 1000  # Unchanged
    assert cfg['retention_strategy'] == 'newest'

def test_config_boundary_values():
    """Test boundary and invalid configuration values."""
    config = TransactionIDRetentionConfig()
    
    # Test negative values are converted to 0 or 1
    config.update_config(
        max_retention_time=-100,
        max_stored_ids=-50
    )
    
    cfg = config.get_config()
    assert cfg['max_retention_time'] == 0
    assert cfg['max_stored_ids'] == 1

def test_invalid_retention_strategy():
    """Test that an invalid retention strategy raises an error."""
    config = TransactionIDRetentionConfig()
    
    with pytest.raises(ValueError, match="Retention strategy must be 'oldest' or 'newest'"):
        config.update_config(retention_strategy='invalid_strategy')

def test_none_values_in_update():
    """Test that None values do not modify existing configuration."""
    config = TransactionIDRetentionConfig(
        max_retention_time=3600,
        max_stored_ids=500,
        retention_strategy='newest'
    )
    
    config.update_config(
        max_retention_time=None,
        max_stored_ids=None,
        retention_strategy=None
    )
    
    cfg = config.get_config()
    assert cfg['max_retention_time'] == 3600
    assert cfg['max_stored_ids'] == 500
    assert cfg['retention_strategy'] == 'newest'