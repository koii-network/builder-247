import pytest
from prometheus_swarm.config.transaction_id_config import (
    TransactionIdRetentionConfig, 
    create_transaction_id_config
)

def test_default_transaction_id_config():
    """Test default configuration initialization."""
    config = create_transaction_id_config()
    
    assert config.max_retention_days == 30
    assert config.max_transaction_count is None
    assert config.enabled is True

def test_custom_transaction_id_config():
    """Test custom configuration initialization."""
    config = create_transaction_id_config(
        max_retention_days=60,
        max_transaction_count=1000,
        enabled=False
    )
    
    assert config.max_retention_days == 60
    assert config.max_transaction_count == 1000
    assert config.enabled is False

def test_invalid_retention_days():
    """Test invalid maximum retention days."""
    with pytest.raises(ValueError, match="max_retention_days must be a positive integer"):
        TransactionIdRetentionConfig(max_retention_days=0)
    
    with pytest.raises(ValueError, match="max_retention_days must be a positive integer"):
        TransactionIdRetentionConfig(max_retention_days=-10)

def test_invalid_transaction_count():
    """Test invalid maximum transaction count."""
    with pytest.raises(ValueError, match="max_transaction_count must be a positive integer or None"):
        TransactionIdRetentionConfig(max_transaction_count=0)
    
    with pytest.raises(ValueError, match="max_transaction_count must be a positive integer or None"):
        TransactionIdRetentionConfig(max_transaction_count=-100)

def test_config_preservation():
    """Test configuration parameter preservation."""
    config = TransactionIdRetentionConfig(
        max_retention_days=45,
        max_transaction_count=500,
        enabled=False
    )
    
    assert config.max_retention_days == 45
    assert config.max_transaction_count == 500
    assert config.enabled is False