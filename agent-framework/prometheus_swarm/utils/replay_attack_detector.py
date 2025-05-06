import time
from typing import Dict, Any, Optional

class ReplayAttackDetector:
    """
    A utility class to detect potential replay attacks by tracking request timestamps and nonces.
    
    This detector prevents replay attacks by:
    1. Tracking unique nonces
    2. Checking request timestamps
    3. Enforcing a time window for request validity
    """
    
    def __init__(self, max_time_window: int = 300, max_nonce_cache_size: int = 1000):
        """
        Initialize the replay attack detector.
        
        Args:
            max_time_window (int): Maximum time window for request validity in seconds. 
                                   Defaults to 5 minutes (300 seconds).
            max_nonce_cache_size (int): Maximum number of nonces to cache. 
                                        Helps prevent memory exhaustion.
        """
        self._nonce_cache: Dict[str, float] = {}
        self._max_time_window = max_time_window
        self._max_nonce_cache_size = max_nonce_cache_size
    
    def _prune_old_nonces(self) -> None:
        """
        Remove old nonces that are outside the time window.
        """
        current_time = time.time()
        expired_nonces = [
            nonce for nonce, timestamp in self._nonce_cache.items()
            if current_time - timestamp > self._max_time_window
        ]
        
        for nonce in expired_nonces:
            del self._nonce_cache[nonce]
    
    def detect_replay(self, nonce: str, timestamp: Optional[float] = None) -> bool:
        """
        Check if the given request is a potential replay attack.
        
        Args:
            nonce (str): A unique identifier for the request.
            timestamp (float, optional): Timestamp of the request. 
                                        If not provided, current time is used.
        
        Returns:
            bool: True if the request appears to be a replay attack, False otherwise.
        
        Raises:
            TypeError: If nonce is not a valid string.
        """
        # Input validation
        if not isinstance(nonce, str):
            raise TypeError("Nonce must be a string")
        
        # Use current time if no timestamp is provided
        current_time = timestamp or time.time()
        
        # Prune old nonces to keep the cache clean
        self._prune_old_nonces()
        
        # Check if nonce already exists
        if nonce in self._nonce_cache:
            return True
        
        # Check timestamp validity: reject if too far in past or future
        time_diff = abs(current_time - time.time())
        if time_diff > self._max_time_window:
            return True
        
        # If cache is getting too large, limit its size by removing the oldest entries
        if len(self._nonce_cache) >= self._max_nonce_cache_size:
            oldest_nonce = min(self._nonce_cache, key=self._nonce_cache.get)
            del self._nonce_cache[oldest_nonce]
        
        # Add new nonce to cache
        self._nonce_cache[nonce] = current_time
        
        return False