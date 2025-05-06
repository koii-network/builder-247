import time
from typing import Dict, Any
from functools import lru_cache

class ReplayAttackDetector:
    """
    A utility class to detect and prevent replay attacks by tracking 
    unique request identifiers and their timestamps.
    """
    
    def __init__(self, max_window_seconds: int = 300, max_cache_size: int = 1000):
        """
        Initialize the Replay Attack Detector.
        
        :param max_window_seconds: Maximum time window for considering a request valid (default 5 minutes)
        :param max_cache_size: Maximum number of unique requests to cache (default 1000)
        """
        self._max_window_seconds = max_window_seconds
        self._request_cache: Dict[str, float] = {}
    
    def detect_replay(self, request_id: str) -> bool:
        """
        Check if a request is a potential replay attack.
        
        :param request_id: Unique identifier for the request
        :return: True if request is a replay, False otherwise
        """
        if not request_id:
            raise ValueError("Request ID cannot be empty")
        
        current_time = time.time()
        
        # Remove expired entries
        self._cleanup_expired_entries(current_time)
        
        # Check if request_id already exists within the time window
        if request_id in self._request_cache:
            return True
        
        # Add new request_id to cache
        self._request_cache[request_id] = current_time
        
        return False
    
    def _cleanup_expired_entries(self, current_time: float):
        """
        Remove entries older than the max time window.
        
        :param current_time: Current timestamp
        """
        expired_keys = [
            key for key, timestamp in self._request_cache.items()
            if current_time - timestamp > self._max_window_seconds
        ]
        
        for key in expired_keys:
            del self._request_cache[key]