import secrets
import time
from typing import Dict, Any, Optional

class NonceSecurityManager:
    """
    A security manager for generating and validating cryptographically secure nonces.
    
    Helps prevent replay attacks and ensure request uniqueness by providing 
    nonce generation and validation mechanisms.
    """
    
    def __init__(self, 
                 nonce_length: int = 32, 
                 max_age_seconds: int = 300):
        """
        Initialize the NonceSecurityManager.
        
        Args:
            nonce_length (int, optional): Length of generated nonce in bytes. Defaults to 32.
            max_age_seconds (int, optional): Maximum age of a valid nonce. Defaults to 5 minutes.
        """
        self._nonce_length = nonce_length
        self._max_age_seconds = max_age_seconds
        self._used_nonces: Dict[str, float] = {}
    
    def generate_nonce(self) -> str:
        """
        Generate a cryptographically secure nonce.
        
        Returns:
            str: A hex-encoded nonce
        """
        nonce = secrets.token_hex(self._nonce_length)
        current_time = time.time()
        self._used_nonces[nonce] = current_time
        return nonce
    
    def validate_nonce(self, nonce: str) -> bool:
        """
        Validate a nonce, checking for uniqueness and expiration.
        
        Args:
            nonce (str): The nonce to validate
        
        Returns:
            bool: True if nonce is valid, False otherwise
        """
        if not nonce:
            return False
        
        current_time = time.time()
        
        # Check and remove any expired nonces
        self.cleanup_expired_nonces()
        
        # Check if nonce exists and is not expired
        if nonce in self._used_nonces:
            del self._used_nonces[nonce]  # Consume the nonce after first validation
            return True
        
        return False
    
    def cleanup_expired_nonces(self) -> int:
        """
        Remove expired nonces from the tracking dictionary.
        
        Returns:
            int: Number of nonces removed
        """
        current_time = time.time()
        expired_nonces = [
            nonce for nonce, timestamp in self._used_nonces.items()
            if current_time - timestamp > self._max_age_seconds
        ]
        
        for nonce in expired_nonces:
            del self._used_nonces[nonce]
        
        return len(expired_nonces)