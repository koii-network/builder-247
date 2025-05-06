import os
import json
import tempfile
import pytest
from prometheus_swarm.config.nonce_config import NonceSystemConfig

def test_default_config():
    """Test default configuration initialization."""
    config = NonceSystemConfig()
    
    assert config.get('nonce_length') == 32
    assert config.get('nonce_encoding') == 'hex'
    assert config.get('nonce_ttl') == 3600
    assert config.get('allow_reuse') is False

def test_config_update():
    """Test configuration parameter update."""
    config = NonceSystemConfig()
    config.update('nonce_length', 64)
    
    assert config.get('nonce_length') == 64

def test_config_file_loading():
    """Test loading configuration from a file."""
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_config:
        json.dump({
            'nonce_length': 48,
            'nonce_encoding': 'base64',
            'nonce_ttl': 7200
        }, temp_config)
        temp_config_path = temp_config.name

    try:
        config = NonceSystemConfig(temp_config_path)
        
        assert config.get('nonce_length') == 48
        assert config.get('nonce_encoding') == 'base64'
        assert config.get('nonce_ttl') == 7200
    finally:
        # Clean up the temporary file
        os.unlink(temp_config_path)

def test_config_validation():
    """Test configuration validation."""
    config = NonceSystemConfig()
    
    # Valid default configuration
    assert config.validate_config() is True
    
    # Invalid nonce length
    config.update('nonce_length', 8)
    assert config.validate_config() is False
    
    # Reset configuration
    config = NonceSystemConfig()
    
    # Invalid nonce encoding
    config.update('nonce_encoding', 'invalid')
    assert config.validate_config() is False
    
    # Reset configuration
    config = NonceSystemConfig()
    
    # Invalid nonce TTL
    config.update('nonce_ttl', -100)
    assert config.validate_config() is False

def test_nonexistent_config_file():
    """Test handling of nonexistent configuration file."""
    with pytest.raises(FileNotFoundError):
        NonceSystemConfig('/path/to/nonexistent/config.json')

def test_invalid_config_file():
    """Test handling of invalid configuration file."""
    # Create a temporary invalid config file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_config:
        temp_config.write('This is not a valid JSON')
        temp_config_path = temp_config.name

    try:
        with pytest.raises(ValueError):
            NonceSystemConfig(temp_config_path)
    finally:
        # Clean up the temporary file
        os.unlink(temp_config_path)