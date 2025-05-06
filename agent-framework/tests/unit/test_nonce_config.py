"""
Unit tests for Nonce System Configuration.
"""

import os
import tempfile
import json
import pytest
from prometheus_swarm.config.nonce_config import NonceConfig

def test_default_nonce_config():
    """
    Test default configuration initialization.
    """
    config = NonceConfig()
    
    # Check default values
    assert config.nonce_salt == 'default_salt'
    assert config.max_nonce_age == 3600
    assert config.nonce_length == 32
    assert config.encryption_key is None
    assert config.debug_mode is False

def test_nonce_config_from_env():
    """
    Test configuration with environment variables.
    """
    # Set environment variables
    os.environ['NONCE_SALT'] = 'test_salt'
    os.environ['MAX_NONCE_AGE'] = '7200'
    os.environ['NONCE_LENGTH'] = '64'
    os.environ['NONCE_ENCRYPTION_KEY'] = 'test_key'
    os.environ['NONCE_DEBUG'] = 'true'
    
    try:
        config = NonceConfig()
        
        # Verify environment-based configuration
        assert config.nonce_salt == 'test_salt'
        assert config.max_nonce_age == 7200
        assert config.nonce_length == 64
        assert config.encryption_key == 'test_key'
        assert config.debug_mode is True
    
    finally:
        # Clean up environment variables
        del os.environ['NONCE_SALT']
        del os.environ['MAX_NONCE_AGE']
        del os.environ['NONCE_LENGTH']
        del os.environ['NONCE_ENCRYPTION_KEY']
        del os.environ['NONCE_DEBUG']

def test_config_save_and_load():
    """
    Test saving and loading configuration to/from a file.
    """
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_filepath = temp_file.name
    
    try:
        # Create and save config
        original_config = NonceConfig(
            nonce_salt='save_test_salt',
            max_nonce_age=5000,
            nonce_length=48,
            encryption_key='save_test_key',
            debug_mode=True
        )
        original_config.save_to_file(temp_filepath)
        
        # Load and verify config
        loaded_config = NonceConfig.load_from_file(temp_filepath)
        
        assert loaded_config.nonce_salt == 'save_test_salt'
        assert loaded_config.max_nonce_age == 5000
        assert loaded_config.nonce_length == 48
        assert loaded_config.encryption_key == 'save_test_key'
        assert loaded_config.debug_mode is True
    
    finally:
        # Clean up the temporary file
        os.unlink(temp_filepath)

def test_config_to_dict():
    """
    Test converting configuration to dictionary.
    """
    config = NonceConfig(
        nonce_salt='dict_test_salt',
        max_nonce_age=4000,
        nonce_length=40,
        encryption_key='dict_test_key',
        debug_mode=True
    )
    
    config_dict = config.to_dict()
    
    assert isinstance(config_dict, dict)
    assert config_dict['nonce_salt'] == 'dict_test_salt'
    assert config_dict['max_nonce_age'] == 4000
    assert config_dict['nonce_length'] == 40
    assert config_dict['encryption_key'] == 'dict_test_key'
    assert config_dict['debug_mode'] is True