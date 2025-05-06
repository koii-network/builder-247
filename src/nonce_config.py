import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class NonceConfig:
    """
    Configuration management class for Nonce System.
    Handles loading configurations from environment variables and JSON files.
    
    Supports multiple configuration sources with priority:
    1. Environment variables
    2. JSON configuration file
    3. Default values
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize NonceConfig with optional configuration file path.
        
        Args:
            config_path (str, optional): Path to JSON configuration file. 
                                         Defaults to 'config/nonce_config.json'
        """
        # Load environment variables
        load_dotenv()
        
        # Default configuration path if not provided
        self._config_path = config_path or 'config/nonce_config.json'
        
        # Configuration dictionary
        self._config: Dict[str, Any] = {}
        
        # Load configurations
        self._load_config()
    
    def _load_config(self):
        """
        Load configuration from multiple sources.
        Prioritizes environment variables over JSON config.
        """
        # Load from JSON file if it exists
        try:
            if os.path.exists(self._config_path):
                with open(self._config_path, 'r') as f:
                    self._config.update(json.load(f))
        except (IOError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load config file: {e}")
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Retrieve configuration value.
        
        Checks in order:
        1. Environment variable
        2. JSON configuration
        3. Provided default value
        
        Args:
            key (str): Configuration key
            default (Any, optional): Default value if key not found
        
        Returns:
            Configuration value or default
        """
        # Check environment variable first
        env_value = os.getenv(key.upper())
        if env_value is not None:
            return env_value
        
        # Check JSON configuration
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        Set a configuration value.
        
        Args:
            key (str): Configuration key
            value (Any): Configuration value
        """
        self._config[key] = value
    
    def save(self):
        """
        Save current configuration to JSON file.
        Creates directory if it doesn't exist.
        """
        os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
        with open(self._config_path, 'w') as f:
            json.dump(self._config, f, indent=4)