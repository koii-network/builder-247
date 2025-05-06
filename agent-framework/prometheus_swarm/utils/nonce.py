import time
import threading
from typing import Dict, Any


class NonceTracker:
    """
    A thread-safe nonce tracking mechanism to prevent replay attacks and duplicate requests.
    
    Tracks nonces with optional expiration to ensure unique request processing.
    """
    
    def __init__(self, expiration_time: int = 3600):
        """
        Initialize the NonceTracker.
        
        Args:
            expiration_time (int, optional): Time in seconds after which a nonce expires. 
                Defaults to 1 hour (3600 seconds).
        """
        self._nonces: Dict[str, float] = {}
        self._lock = threading.Lock()
        self._expiration_time = expiration_time
    
    def is_nonce_valid(self, nonce: str) -> bool:
        """
        Check if a nonce is valid (unique and not expired).
        
        Args:
            nonce (str): The nonce to validate.
        
        Returns:
            bool: True if the nonce is valid, False otherwise.
        """
        current_time = time.time()
        
        with self._lock:
            # Remove expired nonces
            self._cleanup_expired_nonces(current_time)
            
            # Check if nonce exists
            if nonce in self._nonces:
                return False
            
            # Add new nonce
            self._nonces[nonce] = current_time
            return True
    
    def _cleanup_expired_nonces(self, current_time: float) -> None:
        """
        Remove nonces that have expired.
        
        Args:
            current_time (float): Current timestamp.
        """
        expired_nonces = [
            key for key, timestamp in self._nonces.items()
            if current_time - timestamp > self._expiration_time
        ]
        
        for nonce in expired_nonces:
            del self._nonces[nonce]
    
    def set_expiration_time(self, expiration_time: int) -> None:
        """
        Set a new expiration time for nonces.
        
        Args:
            expiration_time (int): New expiration time in seconds.
        """
        with self._lock:
            self._expiration_time = expiration_time
    
    def clear(self) -> None:
        """
        Clear all tracked nonces.
        """
        with self._lock:
            self._nonces.clear()