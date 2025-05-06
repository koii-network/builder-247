import time
import hashlib
import threading
from typing import Dict, Any, Optional

class DistributedNonceValidator:
    """
    A thread-safe distributed nonce validation service.
    
    This class provides mechanisms to validate and track nonces across 
    distributed systems to prevent replay attacks and ensure request uniqueness.
    """
    
    def __init__(self, expiration_time: int = 3600, max_nonces: int = 10000):
        """
        Initialize the nonce validator.
        
        :param expiration_time: Time in seconds after which a nonce expires, defaults to 1 hour
        :param max_nonces: Maximum number of nonces to store before pruning, defaults to 10000
        """
        self._nonces: Dict[str, float] = {}
        self._lock = threading.Lock()
        self._expiration_time = expiration_time
        self._max_nonces = max_nonces
    
    def generate_nonce(self, data: Any) -> str:
        """
        Generate a unique nonce based on input data and current timestamp.
        
        :param data: Data to be included in nonce generation
        :return: A unique nonce string
        """
        current_time = time.time()
        nonce_input = f"{data}{current_time}"
        return hashlib.sha256(nonce_input.encode()).hexdigest()
    
    def validate_nonce(self, nonce: str) -> bool:
        """
        Validate a nonce, checking for uniqueness and non-expiration.
        
        :param nonce: Nonce to validate
        :return: True if nonce is valid and unique, False otherwise
        """
        current_time = time.time()
        
        with self._lock:
            # Prune expired nonces
            self._prune_expired_nonces(current_time)
            
            # Check if nonce exists and is not expired
            if nonce in self._nonces:
                return False
            
            # Add new nonce if max limit not reached
            if len(self._nonces) >= self._max_nonces:
                return False
            
            # Store the nonce with current timestamp
            self._nonces[nonce] = current_time
            return True
    
    def _prune_expired_nonces(self, current_time: float) -> None:
        """
        Remove nonces that have expired.
        
        :param current_time: Current timestamp to compare against
        """
        expired_nonces = [
            nonce for nonce, timestamp in self._nonces.items() 
            if current_time - timestamp > self._expiration_time
        ]
        
        for nonce in expired_nonces:
            del self._nonces[nonce]
    
    def get_nonce_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current nonce store.
        
        :return: Dictionary with nonce statistics
        """
        with self._lock:
            current_time = time.time()
            self._prune_expired_nonces(current_time)
            
            return {
                'total_nonces': len(self._nonces),
                'max_nonces': self._max_nonces,
                'expiration_time': self._expiration_time
            }