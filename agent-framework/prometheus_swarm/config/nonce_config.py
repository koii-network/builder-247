import os
from typing import Dict, Any, Optional

class NonceSystemConfig:
    """
    Configuration management for Nonce System.
    Handles loading and validating configuration parameters.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Nonce System configuration.
        
        :param config_path: Optional path to a configuration file
        """
        self._config: Dict[str, Any] = {}
        self._load_default_config()
        
        if config_path:
            self.load_config_file(config_path)

    def _load_default_config(self):
        """
        Load default configuration parameters.
        """
        self._config = {
            'nonce_length': 32,  # Default nonce length in bytes
            'nonce_encoding': 'hex',  # Default encoding method
            'nonce_ttl': 3600,  # Default time-to-live in seconds (1 hour)
            'allow_reuse': False,  # Default to preventing nonce reuse
        }

    def load_config_file(self, config_path: str):
        """
        Load configuration from a file.
        
        :param config_path: Path to the configuration file
        :raises FileNotFoundError: If the configuration file does not exist
        :raises ValueError: If the configuration file is invalid
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        # For now, we'll support JSON and environment-based configurations
        try:
            import json
            with open(config_path, 'r') as config_file:
                file_config = json.load(config_file)
                self._config.update(file_config)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON configuration file: {config_path}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a configuration value.
        
        :param key: Configuration key
        :param default: Default value if key is not found
        :return: Configuration value
        """
        return self._config.get(key, default)

    def validate_config(self) -> bool:
        """
        Validate the current configuration.
        
        :return: True if configuration is valid, False otherwise
        """
        # Validate nonce length
        if not isinstance(self._config.get('nonce_length', 0), int) or \
           self._config.get('nonce_length', 0) < 16:
            return False
        
        # Validate nonce encoding
        if self._config.get('nonce_encoding') not in ['hex', 'base64', 'base32']:
            return False
        
        # Validate nonce TTL
        if not isinstance(self._config.get('nonce_ttl', 0), int) or \
           self._config.get('nonce_ttl', 0) <= 0:
            return False
        
        return True

    def update(self, key: str, value: Any):
        """
        Update a specific configuration parameter.
        
        :param key: Configuration key
        :param value: New value for the configuration
        """
        self._config[key] = value