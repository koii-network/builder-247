import time
from typing import Dict, Any
from functools import wraps

class ReplayAttackPrevention:
    """
    Utility class to implement replay attack prevention mechanisms.
    
    This class provides methods to validate and track request uniqueness
    using timestamp and nonce strategies.
    """
    
    def __init__(self, max_time_diff: int = 300, max_nonce_cache: int = 1000):
        """
        Initialize replay attack prevention settings.
        
        Args:
            max_time_diff (int): Maximum time difference allowed between request and server time (in seconds)
            max_nonce_cache (int): Maximum number of nonces to cache
        """
        self.max_time_diff = max_time_diff
        self.max_nonce_cache = max_nonce_cache
        self._nonce_cache: Dict[str, float] = {}
    
    def is_request_valid(self, timestamp: float, nonce: str) -> bool:
        """
        Validate a request against replay attack prevention rules.
        
        Args:
            timestamp (float): Timestamp of the request
            nonce (str): Unique identifier for the request
        
        Returns:
            bool: Whether the request is valid and not a replay
        """
        current_time = time.time()
        
        # Check timestamp validity
        time_diff = abs(current_time - timestamp)
        if time_diff > self.max_time_diff:
            return False
        
        # Check nonce uniqueness
        if nonce in self._nonce_cache:
            return False
        
        # Add nonce to cache and remove old nonces if cache is full
        self._nonce_cache[nonce] = current_time
        if len(self._nonce_cache) > self.max_nonce_cache:
            # Remove the oldest nonce
            oldest_nonce = min(self._nonce_cache, key=self._nonce_cache.get)
            del self._nonce_cache[oldest_nonce]
        
        return True
    
    @property
    def nonce_cache_size(self) -> int:
        """
        Get the current size of the nonce cache.
        
        Returns:
            int: Number of nonces currently in the cache
        """
        return len(self._nonce_cache)
    
    def decorator(self, func):
        """
        Decorator to add replay attack prevention to a function.
        
        The decorated function should accept 'timestamp' and 'nonce' as kwargs.
        
        Args:
            func (callable): Function to protect against replay attacks
        
        Returns:
            callable: Protected function
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            timestamp = kwargs.get('timestamp', time.time())
            nonce = kwargs.get('nonce')
            
            if nonce is None:
                raise ValueError("Nonce is required for replay attack prevention")
            
            if not self.is_request_valid(timestamp, nonce):
                raise ValueError("Replay attack detected: Request is invalid")
            
            return func(*args, **kwargs)
        return wrapper

# Global replay attack prevention instance
replay_prevention = ReplayAttackPrevention()