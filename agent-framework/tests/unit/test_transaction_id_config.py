import pytest
from prometheus_swarm.configs.transaction_id_config import TransactionIDTimeWindowConfig

def test_default_configuration():
    """Test the default configuration settings."""
    config = TransactionIDTimeWindowConfig()
    
    assert config.window_duration == 3600
    assert config.max_transactions is None
    assert config.cleanup_interval == 300
    assert config.enabled is True
    assert config.additional_config == {}

def test_custom_configuration():
    """Test creating a configuration with custom settings."""
    config = TransactionIDTimeWindowConfig(
        window_duration=7200,
        max_transactions=100,
        cleanup_interval=600,
        enabled=False,
        additional_config={"logging": True}
    )
    
    assert config.window_duration == 7200
    assert config.max_transactions == 100
    assert config.cleanup_interval == 600
    assert config.enabled is False
    assert config.additional_config == {"logging": True}

def test_validate_configuration():
    """Test configuration validation."""
    # Valid configurations
    valid_configs = [
        TransactionIDTimeWindowConfig(),
        TransactionIDTimeWindowConfig(window_duration=1, max_transactions=1),
    ]
    
    for config in valid_configs:
        assert config.validate() is True

    # Invalid configurations
    invalid_configs = [
        TransactionIDTimeWindowConfig(window_duration=0),
        TransactionIDTimeWindowConfig(window_duration=-1),
        TransactionIDTimeWindowConfig(max_transactions=0),
        TransactionIDTimeWindowConfig(max_transactions=-1),
        TransactionIDTimeWindowConfig(cleanup_interval=0),
        TransactionIDTimeWindowConfig(cleanup_interval=-1)
    ]
    
    for config in invalid_configs:
        assert config.validate() is False

def test_get_config():
    """Test get_config method."""
    config = TransactionIDTimeWindowConfig(
        window_duration=7200,
        max_transactions=100,
        additional_config={"logging": True}
    )
    
    config_dict = config.get_config()
    
    assert config_dict == {
        "window_duration": 7200,
        "max_transactions": 100,
        "cleanup_interval": 300,
        "enabled": True,
        "logging": True
    }