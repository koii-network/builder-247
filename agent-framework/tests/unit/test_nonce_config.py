import os
import pytest
from prometheus_swarm.utils.nonce_config import NonceConfiguration, get_nonce_config

@pytest.fixture
def clean_env():
    """Fixture to clean environment variables before each test."""
    original_env = {key: os.getenv(key) for key in [
        'NONCE_SECRET_KEY', 'NONCE_EXPIRATION_SECONDS', 
        'NONCE_MAX_ATTEMPTS', 'NONCE_ALGORITHM', 
        'NONCE_DEBUG_MODE'
    ]}
    yield
    for key, value in original_env.items():
        if value is None:
            os.unsetenv(key)
        else:
            os.environ[key] = value

def test_default_configuration():
    """Test default configuration values."""
    config = NonceConfiguration()
    
    assert config.NONCE_SECRET_KEY == ''
    assert config.NONCE_EXPIRATION_SECONDS == 300
    assert config.NONCE_MAX_ATTEMPTS == 5
    assert config.NONCE_ALGORITHM == 'SHA256'
    assert config.NONCE_DEBUG_MODE is False

def test_configuration_from_env(clean_env):
    """Test configuration loaded from environment variables."""
    os.environ['NONCE_SECRET_KEY'] = 'test_secret'
    os.environ['NONCE_EXPIRATION_SECONDS'] = '600'
    os.environ['NONCE_MAX_ATTEMPTS'] = '10'
    os.environ['NONCE_ALGORITHM'] = 'SHA512'
    os.environ['NONCE_DEBUG_MODE'] = 'true'

    config = NonceConfiguration.from_env()
    
    assert config.NONCE_SECRET_KEY == 'test_secret'
    assert config.NONCE_EXPIRATION_SECONDS == 600
    assert config.NONCE_MAX_ATTEMPTS == 10
    assert config.NONCE_ALGORITHM == 'SHA512'
    assert config.NONCE_DEBUG_MODE is True

def test_configuration_validation():
    """Test configuration validation."""
    # Valid configuration
    config_valid = NonceConfiguration()
    config_valid.NONCE_SECRET_KEY = 'valid_secret'
    assert config_valid.validate() is True

    # Invalid configurations
    config_no_secret = NonceConfiguration()
    config_no_secret.NONCE_SECRET_KEY = ''
    assert config_no_secret.validate() is False

    config_invalid_expiration = NonceConfiguration()
    config_invalid_expiration.NONCE_SECRET_KEY = 'valid_secret'
    config_invalid_expiration.NONCE_EXPIRATION_SECONDS = -100
    assert config_invalid_expiration.validate() is False

    config_invalid_attempts = NonceConfiguration()
    config_invalid_attempts.NONCE_SECRET_KEY = 'valid_secret'
    config_invalid_attempts.NONCE_MAX_ATTEMPTS = -5
    assert config_invalid_attempts.validate() is False

def test_to_dict():
    """Test conversion of configuration to dictionary."""
    config = NonceConfiguration()
    config.NONCE_SECRET_KEY = 'test_secret'
    
    config_dict = config.to_dict()
    
    assert isinstance(config_dict, dict)
    assert config_dict['NONCE_SECRET_KEY'] == 'test_secret'
    assert 'NONCE_EXPIRATION_SECONDS' in config_dict
    assert 'NONCE_ALGORITHM' in config_dict

def test_get_nonce_config():
    """Test global configuration retrieval."""
    config = get_nonce_config()
    assert isinstance(config, NonceConfiguration)
    assert config.validate() is True