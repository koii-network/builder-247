import os
import hashlib
import secrets
import json
from typing import Dict, Optional

class NonceConfigManager:
    """
    Manages nonce configuration for secure token generation and validation.
    
    Provides methods to:
    - Generate secure nonces
    - Validate nonces
    - Persist and load nonce configurations
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize NonceConfigManager with optional config file path.
        
        :param config_path: Path to nonce configuration file
        """
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), 'nonce_config.json')
        self.nonce_config: Dict[str, str] = self._load_config()
    
    def _load_config(self) -> Dict[str, str]:
        """
        Load nonce configuration from file.
        
        :return: Dictionary of nonce configurations
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            return {}
        except (IOError, json.JSONDecodeError):
            return {}
    
    def _save_config(self):
        """
        Save current nonce configuration to file.
        """
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.nonce_config, f, indent=2)
        except IOError as e:
            raise RuntimeError(f"Failed to save nonce configuration: {e}")
    
    def generate_nonce(self, identifier: str, length: int = 32) -> str:
        """
        Generate a secure nonce for a given identifier.
        
        :param identifier: Unique identifier for the nonce
        :param length: Length of the nonce (default: 32 bytes)
        :return: Generated nonce
        """
        if not identifier:
            raise ValueError("Identifier cannot be empty")
        
        # Generate a cryptographically secure random nonce
        nonce = secrets.token_hex(length // 2)
        
        # Store the nonce with a timestamp hash
        self.nonce_config[identifier] = hashlib.sha256(nonce.encode()).hexdigest()
        self._save_config()
        
        return nonce
    
    def validate_nonce(self, identifier: str, nonce: str) -> bool:
        """
        Validate a nonce for a given identifier.
        
        :param identifier: Unique identifier for the nonce
        :param nonce: Nonce to validate
        :return: True if nonce is valid, False otherwise
        """
        if not identifier or not nonce:
            return False
        
        stored_hash = self.nonce_config.get(identifier)
        if not stored_hash:
            return False
        
        # Validate by comparing hash of input nonce
        input_hash = hashlib.sha256(nonce.encode()).hexdigest()
        return input_hash == stored_hash
    
    def clear_nonce(self, identifier: str):
        """
        Clear a nonce for a given identifier.
        
        :param identifier: Unique identifier for the nonce
        """
        if identifier in self.nonce_config:
            del self.nonce_config[identifier]
            self._save_config()