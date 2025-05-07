import uuid
import time
from typing import Dict, Any
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
        self._generated_nonces: Dict[str, float] = {}
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
            self._generated_nonces[nonce] = current_time
            
            return nonce

    def validate_nonce(self, nonce: str, consume: bool = True) -> bool:
        """
        Validate a nonce, checking for uniqueness and expiration.
        
        Args:
            nonce (str): The nonce to validate.
            consume (bool): Whether to remove the nonce after validation. Default is True.
        
        Raises:
            NonceAlreadyUsedError: If the nonce is not found or has been validated.
        
        Returns:
            bool: True if the nonce is valid and has not been previously validated.
        """
        with self._lock:
            # Cleanup expired nonces
            self._cleanup_expired_nonces()
            
            # Check if nonce is present and not expired
            if nonce not in self._generated_nonces:
                raise NonceAlreadyUsedError(f"Nonce {nonce} is not valid or has been used.")
            
            # If consume is True, remove the nonce
            if consume:
                del self._generated_nonces[nonce]
            
            return True

    def _cleanup_expired_nonces(self):
        """
        Remove expired nonces from the tracking dictionary.
        """
        current_time = time.time()
        expired_nonces = [
            nonce for nonce, timestamp in self._generated_nonces.items()
            if current_time - timestamp > self._nonce_expiry
        ]
        
        # Remove expired nonces
        for nonce in expired_nonces:
            del self._generated_nonces[nonce]
        
        # Limit the number of tracked nonces
        if len(self._generated_nonces) > self._max_nonces:
            # Remove the oldest nonces first
            oldest_nonces = sorted(
                self._generated_nonces.items(), 
                key=lambda x: x[1]
            )[:len(self._generated_nonces) - self._max_nonces]
            
            for nonce, _ in oldest_nonces:
                del self._generated_nonces[nonce]

# Global singleton instance for easy import and use
nonce_manager = NonceManager()