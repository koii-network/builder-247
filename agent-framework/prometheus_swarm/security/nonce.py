import secrets
import time
from typing import Dict, Any

class NonceSecurityManager:
    """
    Manages nonce generation and validation for security purposes.
    
    A nonce is a unique, one-time use token used to prevent replay attacks 
    and ensure the uniqueness of requests.
    """
    
    def __init__(self, 
                 nonce_length: int = 32, 
                 nonce_expiration: int = 300):
        """
        Initialize the NonceSecurityManager.
        
        :param nonce_length: Length of the generated nonce in bytes
        :param nonce_expiration: Expiration time for nonce in seconds (default 5 minutes)
        """
        self._nonce_length = nonce_length
        self._nonce_expiration = nonce_expiration
        self._active_nonces: Dict[str, float] = {}
    
    def generate_nonce(self) -> str:
        """
        Generate a cryptographically secure random nonce.
        
        :return: A unique nonce string
        """
        while True:
            nonce = secrets.token_hex(self._nonce_length)
            
            # Prevent duplicate nonces
            if nonce not in self._active_nonces:
                current_time = time.time()
                self._active_nonces[nonce] = current_time
                return nonce
    
    def validate_nonce(self, nonce: str) -> bool:
        """
        Validate a nonce, checking for:
        1. Existence in active nonces
        2. Not expired
        
        :param nonce: Nonce to validate
        :return: True if valid, False otherwise
        """
        if nonce not in self._active_nonces:
            return False
        
        current_time = time.time()
        nonce_time = self._active_nonces[nonce]
        
        # Check if nonce has expired
        if current_time - nonce_time > self._nonce_expiration:
            del self._active_nonces[nonce]
            return False
        
        # Remove nonce after successful validation to prevent reuse
        del self._active_nonces[nonce]
        return True
    
    def cleanup_expired_nonces(self) -> None:
        """
        Remove expired nonces from the active nonces dictionary.
        """
        current_time = time.time()
        expired_nonces = [
            nonce for nonce, timestamp 
            in self._active_nonces.items() 
            if current_time - timestamp > self._nonce_expiration
        ]
        
        for nonce in expired_nonces:
            del self._active_nonces[nonce]