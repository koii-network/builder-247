import time
import hashlib
from typing import Dict, Any

class ReplayAttackPrevention:
    """
    Utility class to prevent replay attacks by tracking request signatures and timestamps.
    
    This class maintains a cache of recent request signatures to detect and prevent 
    replay attacks by ensuring each request is unique and not too old.
    """
    
    def __init__(self, max_cache_size: int = 1000, max_request_age_seconds: int = 300):
        """
        Initialize the replay attack prevention mechanism.
        
        Args:
            max_cache_size (int): Maximum number of unique requests to track.
            max_request_age_seconds (int): Maximum allowed age of a request in seconds.
        """
        self._request_cache: Dict[str, float] = {}
        self._max_cache_size = max_cache_size
        self._max_request_age = max_request_age_seconds
    
    def _generate_signature(self, request_data: Dict[str, Any]) -> str:
        """
        Generate a unique signature for a request.
        
        Args:
            request_data (Dict[str, Any]): The request data to generate a signature for.
        
        Returns:
            str: A unique signature for the request.
        """
        # Convert request data to a sorted, stringified version to ensure consistent hashing
        stringified_data = str(sorted(request_data.items()))
        return hashlib.sha256(stringified_data.encode()).hexdigest()
    
    def is_replay_attack(self, request_data: Dict[str, Any]) -> bool:
        """
        Check if the current request is a potential replay attack.
        
        Args:
            request_data (Dict[str, Any]): The request data to check.
        
        Returns:
            bool: True if the request appears to be a replay attack, False otherwise.
        """
        current_time = time.time()
        signature = self._generate_signature(request_data)
        
        # Clean up expired entries
        self._clean_cache(current_time)
        
        # Check if signature exists and is recent
        if signature in self._request_cache:
            return True
        
        # Add new signature to cache
        self._request_cache[signature] = current_time
        
        # Manage cache size
        if len(self._request_cache) > self._max_cache_size:
            oldest_key = min(self._request_cache, key=self._request_cache.get)
            del self._request_cache[oldest_key]
        
        return False
    
    def _clean_cache(self, current_time: float) -> None:
        """
        Remove expired entries from the request cache.
        
        Args:
            current_time (float): The current timestamp.
        """
        expired_keys = [
            key for key, timestamp in self._request_cache.items()
            if current_time - timestamp > self._max_request_age
        ]
        
        for key in expired_keys:
            del self._request_cache[key]

# Global replay attack prevention instance
replay_preventer = ReplayAttackPrevention()