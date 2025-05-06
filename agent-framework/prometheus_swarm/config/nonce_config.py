"""
Configuration module for the Nonce System.

This module provides configuration management for the Nonce System,
including environment variables, configuration loading, and default settings.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class NonceConfig:
    """
    Configuration class for Nonce System settings.
    
    Attributes:
        nonce_salt (str): Salt used for nonce generation
        max_nonce_age (int): Maximum age of a nonce in seconds
        nonce_length (int): Length of generated nonces
        encryption_key (Optional[str]): Optional encryption key for nonce
        debug_mode (bool): Enable debug logging
    """
    nonce_salt: str = os.getenv('NONCE_SALT', 'default_salt')
    max_nonce_age: int = int(os.getenv('MAX_NONCE_AGE', 3600))  # 1 hour default
    nonce_length: int = int(os.getenv('NONCE_LENGTH', 32))
    encryption_key: Optional[str] = os.getenv('NONCE_ENCRYPTION_KEY')
    debug_mode: bool = os.getenv('NONCE_DEBUG', 'false').lower() == 'true'

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the configuration
        """
        return asdict(self)

    def save_to_file(self, filepath: str) -> None:
        """
        Save configuration to a JSON file.
        
        Args:
            filepath (str): Path to save the configuration file
        """
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load_from_file(cls, filepath: str) -> 'NonceConfig':
        """
        Load configuration from a JSON file.
        
        Args:
            filepath (str): Path to the configuration file
        
        Returns:
            NonceConfig: Loaded configuration instance
        """
        with open(filepath, 'r') as f:
            config_dict = json.load(f)
        return cls(**config_dict)

# Create a default configuration instance
default_nonce_config = NonceConfig()