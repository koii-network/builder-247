import time
from typing import Dict, Any, Optional
import threading
import uuid

class DistributedNonceValidator:
    """
    A thread-safe distributed nonce validation service that prevents replay attacks
    and ensures unique request processing across distributed systems.
    """
    
    def __init__(self, max_age: int = 3600, max_nonces: int = 10000):
        """
        Initialize the nonce validator.
        
        :param max_age: Maximum age of a nonce in seconds (default: 1 hour)
        :param max_nonces: Maximum number of nonces to store (default: 10000)
        """
        self._nonces: Dict[str, float] = {}
        self._lock = threading.Lock()
        self._max_age = max_age
        self._max_nonces = max_nonces
    
    def generate_nonce(self) -> str:
        """
        Generate a unique nonce.
        
        :return: A unique nonce string
        """
        return str(uuid.uuid4())
    
    def validate_nonce(self, nonce: str) -> bool:
        """
        Validate a nonce, ensuring it's unique and not expired.
        
        :param nonce: Nonce to validate
        :return: True if nonce is valid, False otherwise
        """
        current_time = time.time()
        
        with self._lock:
            # Remove expired nonces
            self._cleanup_expired_nonces(current_time)
            
            # Check if nonce exists
            if nonce in self._nonces:
                return False
            
            # If we've reached max nonces, prevent adding new nonces
            if len(self._nonces) >= self._max_nonces:
                return False
            
            # Store the nonce with current timestamp
            self._nonces[nonce] = current_time
            
            return True
    
    def _cleanup_expired_nonces(self, current_time: float) -> None:
        """
        Remove nonces that have exceeded max_age.
        
        :param current_time: Current timestamp
        """
        expired_nonces = [
            n for n, timestamp in self._nonces.items() 
            if current_time - timestamp > self._max_age
        ]
        
        for nonce in expired_nonces:
            del self._nonces[nonce]