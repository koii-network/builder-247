import uuid
import time
from typing import Dict, Set
from threading import Lock

class NonceError(Exception):
    """Base exception for nonce-related errors."""
    pass

class NonceAlreadyUsedError(NonceError):
    """Raised when a nonce has already been used."""
    pass

class NonceExpiredError(NonceError):
    """Raised when a nonce has expired."""
    pass

class NonceManager:
    """
    Manages nonce generation, validation, and tracking.
    
    Provides thread-safe nonce management with expiration and uniqueness checks.
    """
    def __init__(self, max_nonces: int = 1000, nonce_expiry: int = 300):
        """
        Initialize the NonceManager.
        
        Args:
            max_nonces (int): Maximum number of nonces to track. Default is 1000.
            nonce_expiry (int): Nonce expiration time in seconds. Default is 5 minutes.
        """
        self._used_nonces: Dict[str, float] = {}
        self._lock = Lock()
        self._max_nonces = max_nonces
        self._nonce_expiry = nonce_expiry

    def generate_nonce(self) -> str:
        """
        Generate a unique nonce.
        
        Returns:
            str: A unique nonce value.
        """
        with self._lock:
            # Cleanup expired nonces
            self._cleanup_expired_nonces()
            
            # Generate a unique nonce
            nonce = str(uuid.uuid4())
            current_time = time.time()
            self._used_nonces[nonce] = current_time
            
            return nonce

    def validate_nonce(self, nonce: str, consume: bool = True) -> bool:
        """
        Validate a nonce, checking for uniqueness and expiration.
        
        Args:
            nonce (str): The nonce to validate.
            consume (bool): Whether to mark the nonce as used after validation. Default is True.
        
        Raises:
            NonceAlreadyUsedError: If the nonce has been used before.
            NonceExpiredError: If the nonce has expired.
        
        Returns:
            bool: True if the nonce is valid.
        """
        with self._lock:
            # Cleanup expired nonces
            self._cleanup_expired_nonces()
            
            # Check if nonce is already used
            if nonce in self._used_nonces:
                raise NonceAlreadyUsedError(f"Nonce {nonce} has already been used.")
            
            # Mark the nonce as used if consume is True
            if consume:
                self._used_nonces[nonce] = time.time()
            
            return True

    def _cleanup_expired_nonces(self):
        """
        Remove expired nonces from the tracking dictionary.
        """
        current_time = time.time()
        expired_nonces = [
            nonce for nonce, timestamp in self._used_nonces.items()
            if current_time - timestamp > self._nonce_expiry
        ]
        
        for nonce in expired_nonces:
            del self._used_nonces[nonce]
        
        # Limit the number of tracked nonces
        if len(self._used_nonces) > self._max_nonces:
            oldest_nonces = sorted(
                self._used_nonces.items(), 
                key=lambda x: x[1]
            )[:len(self._used_nonces) - self._max_nonces]
            
            for nonce, _ in oldest_nonces:
                del self._used_nonces[nonce]

# Global singleton instance for easy import and use
nonce_manager = NonceManager()