import secrets
import time
from typing import Dict, Any
from threading import Lock

class NonceSecurityManager:
    """
    A thread-safe nonce management utility for preventing replay attacks and ensuring request uniqueness.
    
    Features:
    - Generate cryptographically secure random nonces
    - Track and validate nonce usage
    - Automatically expire old nonces
    """
    
    def __init__(self, nonce_expiry_seconds: int = 300):
        """
        Initialize the NonceSecurityManager.
        
        :param nonce_expiry_seconds: Time in seconds after which a nonce becomes invalid. Defaults to 5 minutes.
        """
        self._nonces: Dict[str, float] = {}
        self._lock = Lock()
        self._nonce_expiry = nonce_expiry_seconds
    
    def generate_nonce(self, length: int = 32) -> str:
        """
        Generate a cryptographically secure random nonce.
        
        :param length: Length of the nonce in bytes
        :return: A hex-encoded nonce string
        """
        return secrets.token_hex(length)
    
    def validate_nonce(self, nonce: str) -> bool:
        """
        Validate a nonce, checking for uniqueness and preventing replay attacks.
        
        :param nonce: The nonce to validate
        :return: True if the nonce is valid and unique, False otherwise
        """
        current_time = time.time()
        
        with self._lock:
            # Remove expired nonces
            self._nonces = {
                k: v for k, v in self._nonces.items() 
                if current_time - v < self._nonce_expiry
            }
            
            # Check if nonce already exists
            if nonce in self._nonces:
                return False
            
            # Add new nonce
            self._nonces[nonce] = current_time
            return True
    
    def get_nonce_age(self, nonce: str) -> float:
        """
        Get the age of a tracked nonce.
        
        :param nonce: The nonce to check
        :return: Age of the nonce in seconds, or -1 if not found
        """
        with self._lock:
            timestamp = self._nonces.get(nonce, None)
            return time.time() - timestamp if timestamp is not None else -1
    
    def clear_nonces(self):
        """
        Manually clear all tracked nonces.
        """
        with self._lock:
            self._nonces.clear()