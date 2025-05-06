import os
import json
import tempfile
import pytest
from src.nonce_config import NonceConfig

@pytest.fixture
def temp_config_file():
    """Create a temporary configuration file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        json.dump({
            "max_attempts": 3,
            "timeout": 60,
            "retry_strategy": "exponential"
        }, temp_file)
        temp_file.close()
        yield temp_file.name
    os.unlink(temp_file.name)

def test_nonce_config_default_initialization():
    """Test default initialization of NonceConfig."""
    config = NonceConfig()
    assert isinstance(config, NonceConfig)

def test_nonce_config_with_custom_file(temp_config_file):
    """Test NonceConfig with a custom configuration file."""
    config = NonceConfig(config_path=temp_config_file)
    
    # Check JSON config values
    assert config.get('max_attempts') == 3
    assert config.get('timeout') == 60
    assert config.get('retry_strategy') == 'exponential'

def test_nonce_config_environment_override(temp_config_file, monkeypatch):
    """Test that environment variables override JSON configuration."""
    # Set environment variable
    monkeypatch.setenv('MAX_ATTEMPTS', '5')
    
    config = NonceConfig(config_path=temp_config_file)
    
    # Verify environment variable takes precedence
    assert config.get('max_attempts') == '5'
    assert config.get('timeout') == 60

def test_nonce_config_default_value(temp_config_file):
    """Test retrieving a value with a default."""
    config = NonceConfig(config_path=temp_config_file)
    
    # Check default value for non-existent key
    assert config.get('non_existent_key', 'default_value') == 'default_value'

def test_nonce_config_set_and_save(temp_config_file):
    """Test setting and saving configuration."""
    config = NonceConfig(config_path=temp_config_file)
    
    # Set a new configuration value
    config.set('new_setting', 'test_value')
    config.save()
    
    # Reload and verify
    reloaded_config = NonceConfig(config_path=temp_config_file)
    assert reloaded_config.get('new_setting') == 'test_value'

def test_nonce_config_invalid_file():
    """Test handling of invalid configuration file."""
    with pytest.warns(UserWarning):
        # Attempt to load from a non-existent file
        config = NonceConfig(config_path='/path/to/nonexistent/config.json')
        
    # Verify no errors are raised