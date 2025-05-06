"""
Nonce System Configuration and Environment Setup

This module provides configuration management and environment setup 
for the Nonce System, including initialization, validation, and 
environment-specific settings.
"""

import os
import logging
from typing import Dict, Any, Optional, Union
from dotenv import load_dotenv

class NonceConfig:
    """
    Configuration management class for Nonce System.
    
    Handles environment variable loading, configuration validation, 
    and provides a centralized configuration access point.
    """
    
    def __init__(self, env_path: Optional[str] = None):
        """
        Initialize the NonceConfig with optional environment file path.
        
        Args:
            env_path (Optional[str]): Path to the .env file. 
                                      Defaults to .env in the current directory.
        """
        # Load environment variables 
        self.env_path = env_path or os.path.join(os.path.dirname(__file__), '..', '..', '.env')
        load_dotenv(self.env_path)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - NonceConfig - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Validate and store configuration
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load and validate configuration from environment variables.
        
        Returns:
            Dict[str, Any]: Validated configuration dictionary
        
        Raises:
            ValueError: If required configuration is missing or invalid
        """
        config = {
            'nonce_secret_key': self._get_env_var('NONCE_SECRET_KEY'),
            'nonce_expiration_minutes': self._get_env_var('NONCE_EXPIRATION_MINUTES', default=30, cast=int),
            'nonce_max_uses': self._get_env_var('NONCE_MAX_USES', default=1, cast=int),
            'debug_mode': self._get_env_var('NONCE_DEBUG_MODE', default=False, cast=bool)
        }
        
        # Additional validation
        if len(config['nonce_secret_key']) < 16:
            raise ValueError("Nonce secret key must be at least 16 characters long")
        
        return config
    
    def _get_env_var(
        self, 
        key: str, 
        default: Any = None, 
        required: bool = True, 
        cast: Optional[type] = None
    ) -> Any:
        """
        Retrieve and optionally validate an environment variable.
        
        Args:
            key (str): Environment variable name
            default (Any, optional): Default value if not set
            required (bool): Whether the variable is required
            cast (Optional[type]): Type to cast the value to
        
        Returns:
            Any: The environment variable value
        
        Raises:
            ValueError: If required variable is not set
        """
        value = os.getenv(key, default)
        
        if value is None and required:
            self.logger.error(f"Required environment variable {key} is not set")
            raise ValueError(f"Required environment variable {key} is not set")
        
        # Cast the value if a type is provided
        if cast is not None and value is not None:
            try:
                value = cast(value)
            except ValueError:
                self.logger.error(f"Could not cast {key} to {cast.__name__}")
                raise
        
        return value
    
    def get_config(self, key: Optional[str] = None) -> Union[Dict[str, Any], Any]:
        """
        Retrieve the entire configuration or a specific configuration value.
        
        Args:
            key (Optional[str]): Specific configuration key to retrieve
        
        Returns:
            Union[Dict[str, Any], Any]: Full configuration or specific value
        """
        if key is None:
            return self._config
        
        return self._config.get(key)
    
    def is_debug_mode(self) -> bool:
        """
        Check if debug mode is enabled.
        
        Returns:
            bool: True if debug mode is on, False otherwise
        """
        return self._config['debug_mode']

# Create a singleton instance for easy import and use
nonce_config = NonceConfig()