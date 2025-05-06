import os
import secrets
from typing import Dict, Any, Optional
from dataclasses import dataclass, fields
from dotenv import load_dotenv

# Automatically load environment variables from .env file
load_dotenv()

@dataclass
class NonceConfiguration:
    """
    Configuration class for managing Nonce System settings.
    
    Provides a structured way to load and validate configuration settings
    with support for environment variables and default values.
    """
    # Nonce-related configurations
    NONCE_SECRET_KEY: str = os.getenv('NONCE_SECRET_KEY', '')
    NONCE_EXPIRATION_SECONDS: int = int(os.getenv('NONCE_EXPIRATION_SECONDS', 300))
    NONCE_MAX_ATTEMPTS: int = int(os.getenv('NONCE_MAX_ATTEMPTS', 5))
    
    # Cryptographic settings
    NONCE_ALGORITHM: str = os.getenv('NONCE_ALGORITHM', 'SHA256')
    
    # Logging and debugging
    NONCE_DEBUG_MODE: bool = os.getenv('NONCE_DEBUG_MODE', 'false').lower() == 'true'

    def __post_init__(self):
        """
        Post-initialization method to generate a default secret key if not provided.
        """
        if not self.NONCE_SECRET_KEY:
            self.NONCE_SECRET_KEY = secrets.token_hex(32)

    def validate(self) -> bool:
        """
        Validate the current configuration settings.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        if self.NONCE_EXPIRATION_SECONDS <= 0:
            print("Error: NONCE_EXPIRATION_SECONDS must be positive")
            return False
        
        if self.NONCE_MAX_ATTEMPTS <= 0:
            print("Error: NONCE_MAX_ATTEMPTS must be positive")
            return False
        
        return True

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of configuration
        """
        return {field.name: getattr(self, field.name) for field in fields(self)}

    @classmethod
    def from_env(cls) -> 'NonceConfiguration':
        """
        Create a configuration instance from environment variables.
        
        Returns:
            NonceConfiguration: Configured instance
        """
        config = cls()
        if not config.validate():
            raise ValueError("Invalid Nonce Configuration")
        return config

def get_nonce_config() -> NonceConfiguration:
    """
    Retrieve the global Nonce Configuration.
    
    Returns:
        NonceConfiguration: Configured Nonce settings
    """
    return NonceConfiguration.from_env()