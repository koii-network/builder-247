"""Unit tests for Transaction ID Retention Configuration."""

import os
import pytest
from prometheus_swarm.database.config import TransactionIDRetentionConfig

def test_transaction_id_retention_config_default():
    """Test default configuration initialization."""
    config = TransactionIDRetentionConfig()
    
    assert config.max_retention_days == 30
    assert config.max_retention_count == 1000
    assert config.enable_pruning is True

def test_transaction_id_retention_config_custom():
    """Test custom configuration initialization."""
    config = TransactionIDRetentionConfig(
        max_retention_days=60, 
        max_retention_count=2000, 
        enable_pruning=False
    )
    
    assert config.max_retention_days == 60
    assert config.max_retention_count == 2000
    assert config.enable_pruning is False

def test_transaction_id_retention_config_validation():
    """Test configuration validation."""
    # Valid configurations
    valid_configs = [
        TransactionIDRetentionConfig(),
        TransactionIDRetentionConfig(max_retention_days=None, max_retention_count=None),
        TransactionIDRetentionConfig(max_retention_days=90, max_retention_count=500)
    ]

    # Invalid configurations
    invalid_configs = [
        TransactionIDRetentionConfig(max_retention_days=-1),
        TransactionIDRetentionConfig(max_retention_count=-1)
    ]

    # Validate valid configs
    for config in valid_configs:
        assert config.validate() is True

    # Validate invalid configs
    for config in invalid_configs:
        assert config.validate() is False

def test_transaction_id_retention_get_limits():
    """Test get_retention_limits method."""
    config = TransactionIDRetentionConfig(
        max_retention_days=45, 
        max_retention_count=1500, 
        enable_pruning=True
    )
    
    limits = config.get_retention_limits()
    
    assert limits == {
        "max_retention_days": 45,
        "max_retention_count": 1500,
        "pruning_enabled": True
    }

def test_transaction_id_retention_env_variables():
    """Test configuration parsing from environment variables."""
    # Store original environment variables
    orig_days = os.getenv('TRANSACTION_ID_MAX_RETENTION_DAYS')
    orig_count = os.getenv('TRANSACTION_ID_MAX_RETENTION_COUNT')
    orig_pruning = os.getenv('TRANSACTION_ID_ENABLE_PRUNING')

    try:
        # Set environment variables
        os.environ['TRANSACTION_ID_MAX_RETENTION_DAYS'] = '90'
        os.environ['TRANSACTION_ID_MAX_RETENTION_COUNT'] = '5000'
        os.environ['TRANSACTION_ID_ENABLE_PRUNING'] = 'false'

        # Create config with environment variables
        config = TransactionIDRetentionConfig()

        # Verify environment variable parsing
        assert config.max_retention_days == 90
        assert config.max_retention_count == 5000
        assert config.enable_pruning is False

        # Verify parameter override of environment variables
        config_override = TransactionIDRetentionConfig(
            max_retention_days=60, 
            max_retention_count=2000, 
            enable_pruning=True
        )
        assert config_override.max_retention_days == 60
        assert config_override.max_retention_count == 2000
        assert config_override.enable_pruning is True

    finally:
        # Restore original environment variables
        if orig_days:
            os.environ['TRANSACTION_ID_MAX_RETENTION_DAYS'] = orig_days
        else:
            os.environ.pop('TRANSACTION_ID_MAX_RETENTION_DAYS', None)

        if orig_count:
            os.environ['TRANSACTION_ID_MAX_RETENTION_COUNT'] = orig_count
        else:
            os.environ.pop('TRANSACTION_ID_MAX_RETENTION_COUNT', None)

        if orig_pruning:
            os.environ['TRANSACTION_ID_ENABLE_PRUNING'] = orig_pruning
        else:
            os.environ.pop('TRANSACTION_ID_ENABLE_PRUNING', None)