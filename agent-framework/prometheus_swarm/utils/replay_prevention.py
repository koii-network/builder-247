import time
import hashlib
import threading
from typing import Dict, Any

class ReplayAttackPrevention:
    """
    A utility class to prevent replay attacks by tracking and validating request uniqueness.
    
    This class maintains a cache of recent unique request identifiers to detect 
    and prevent replay attacks. It uses a timestamp-based sliding window approach 
    to limit the validity of requests.
    """
    
    def __init__(self, window_seconds: int = 300, max_cache_size: int = 1000):
        """
        Initialize the replay attack prevention mechanism.
        
        Args:
            window_seconds (int, optional): Time window for request validity. Defaults to 300 seconds (5 minutes).
            max_cache_size (int, optional): Maximum number of requests to cache. Defaults to 1000.
        """
        self._request_cache: Dict[str, float] = {}
        self._window_seconds = window_seconds
        self._max_cache_size = max_cache_size
        self._lock = threading.Lock()
        
        # Start a background thread to clean up expired entries
        self._cleanup_thread = threading.Thread(target=self._periodic_cleanup, daemon=True)
        self._cleanup_thread.start()
    
    def generate_request_id(self, request_data: Any) -> str:
        """
        Generate a unique identifier for a request to detect replays.
        
        Args:
            request_data (Any): The request data to generate a unique ID for.
        
        Returns:
            str: A unique request identifier.
        """
        # Convert request data to a string representation
        data_str = str(request_data)
        
        # Include current timestamp to make the ID time-sensitive
        timestamp = str(time.time())
        
        # Create a hash that combines data and timestamp
        return hashlib.sha256(f"{data_str}:{timestamp}".encode()).hexdigest()
    
    def is_unique_request(self, request_id: str) -> bool:
        """
        Check if a request is unique and not a replay.
        
        Args:
            request_id (str): The unique request identifier.
        
        Returns:
            bool: True if the request is unique, False if it's a potential replay.
        """
        current_time = time.time()
        
        with self._lock:
            # Check if request is in cache and within time window
            if request_id in self._request_cache:
                return False
            
            # Add request to cache
            self._request_cache[request_id] = current_time
            
            # Limit cache size
            if len(self._request_cache) > self._max_cache_size:
                oldest_key = min(self._request_cache, key=self._request_cache.get)
                del self._request_cache[oldest_key]
            
            return True
    
    def _periodic_cleanup(self):
        """
        Background thread to remove expired request entries.
        """
        while True:
            time.sleep(self._window_seconds / 2)  # Clean up every half window
            
            current_time = time.time()
            with self._lock:
                expired_keys = [
                    key for key, timestamp in self._request_cache.items()
                    if current_time - timestamp > self._window_seconds
                ]
                
                for key in expired_keys:
                    del self._request_cache[key]