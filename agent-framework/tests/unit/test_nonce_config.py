"""
Unit tests for NonceConfig configuration management.
"""

import os
import pytest
from prometheus_swarm.config.nonce import NonceConfig

class TestNonceConfig:
    @pytest.fixture
    def mock_env(self, monkeypatch):
        """
        Create a fixture to mock environment variables for testing.
        """
        monkeypatch.setenv('NONCE_SECRET_KEY', 'test_secret_key_12345678')
        monkeypatch.setenv('NONCE_EXPIRATION_MINUTES', '45')
        monkeypatch.setenv('NONCE_MAX_USES', '3')
        monkeypatch.setenv('NONCE_DEBUG_MODE', 'True')
    
    def test_config_initialization(self, mock_env):
        """
        Test that the NonceConfig can be initialized with correct environment variables.
        """
        config = NonceConfig()
        
        assert config.get_config('nonce_secret_key') == 'test_secret_key_12345678'
        assert config.get_config('nonce_expiration_minutes') == 45
        assert config.get_config('nonce_max_uses') == 3
        assert config.get_config('debug_mode') is True
    
    def test_config_get_specific_key(self, mock_env):
        """
        Test retrieving a specific configuration value.
        """
        config = NonceConfig()
        
        assert config.get_config('nonce_secret_key') == 'test_secret_key_12345678'
        assert config.get_config('nonce_expiration_minutes') == 45
    
    def test_debug_mode(self, mock_env):
        """
        Test debug mode detection.
        """
        config = NonceConfig()
        
        assert config.is_debug_mode() is True
    
    def test_short_secret_key_raises_error(self, monkeypatch):
        """
        Test that a short secret key raises a ValueError.
        """
        monkeypatch.setenv('NONCE_SECRET_KEY', 'short')
        
        with pytest.raises(ValueError, match="Nonce secret key must be at least 16 characters long"):
            NonceConfig()
    
    def test_missing_required_env_var(self, monkeypatch):
        """
        Test that missing required environment variables raise an error.
        """
        # Remove the required secret key
        monkeypatch.delenv('NONCE_SECRET_KEY', raising=False)
        
        with pytest.raises(ValueError, match="Required environment variable NONCE_SECRET_KEY is not set"):
            NonceConfig()
    
    def test_optional_env_vars_with_defaults(self, monkeypatch):
        """
        Test that optional environment variables use default values.
        """
        # Only set the required secret key
        monkeypatch.setenv('NONCE_SECRET_KEY', 'test_secret_key_12345678')
        
        config = NonceConfig()
        
        assert config.get_config('nonce_expiration_minutes') == 30  # Default value
        assert config.get_config('nonce_max_uses') == 1  # Default value
        assert config.get_config('debug_mode') is False  # Default value