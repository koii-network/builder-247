import hashlib
import os
import time
from typing import Dict, Optional

class NonceMiddleware:
    """
    Middleware for generating and validating nonces to prevent replay attacks.
    
    This middleware provides functionality to:
    1. Generate unique nonces
    2. Validate nonces
    3. Manage nonce expiration
    """
    
    def __init__(self, max_age: int = 300, max_nonces: int = 100):
        """
        Initialize the NonceMiddleware.
        
        Args:
            max_age (int): Maximum age of a nonce in seconds (default: 5 minutes)
            max_nonces (int): Maximum number of nonces to store (default: 100)
        """
        self._used_nonces: Dict[str, float] = {}
        self._max_age = max_age
        self._max_nonces = max_nonces
    
    def generate_nonce(self) -> str:
        """
        Generate a unique, cryptographically secure nonce.
        
        Returns:
            str: A unique nonce string
        """
        # Remove expired nonces to prevent unbounded growth
        self._cleanup_nonces()
        
        # Generate a unique nonce using timestamp, random bytes, and salt
        timestamp = str(time.time()).encode('utf-8')
        random_bytes = os.urandom(16)
        salt = os.urandom(16)
        
        nonce = hashlib.sha256(timestamp + random_bytes + salt).hexdigest()
        
        # Store the nonce with its creation time
        self._used_nonces[nonce] = time.time()
        
        return nonce
    
    def validate_nonce(self, nonce: str) -> bool:
        """
        Validate a nonce, checking for:
        1. Uniqueness
        2. Not expired
        
        Args:
            nonce (str): The nonce to validate
        
        Returns:
            bool: True if nonce is valid, False otherwise
        """
        # Remove expired nonces
        self._cleanup_nonces()
        
        # Check if nonce exists and is not expired
        if nonce not in self._used_nonces:
            return False
        
        return True
    
    def _cleanup_nonces(self) -> None:
        """
        Remove expired nonces and limit total number of nonces.
        """
        current_time = time.time()
        
        # Remove expired nonces
        self._used_nonces = {
            n: t for n, t in self._used_nonces.items() 
            if current_time - t <= self._max_age
        }
        
        # If too many nonces, remove oldest
        if len(self._used_nonces) > self._max_nonces:
            oldest_nonces = sorted(
                self._used_nonces.items(), 
                key=lambda x: x[1]
            )[:len(self._used_nonces) - self._max_nonces]
            
            for nonce, _ in oldest_nonces:
                del self._used_nonces[nonce]