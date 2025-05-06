import hashlib
import time
from typing import Dict, Any

class ReplayAttackDetector:
    """
    A class to detect and prevent replay attacks by tracking request signatures.
    
    Replay attacks occur when a valid data transmission is maliciously repeated or delayed.
    This detector helps mitigate such attacks by tracking request uniqueness.
    """
    
    def __init__(self, window_seconds: int = 300, max_cache_size: int = 1000):
        """
        Initialize the Replay Attack Detector.
        
        Args:
            window_seconds (int): Time window for considering a request unique (default 5 minutes)
            max_cache_size (int): Maximum number of recent requests to track
        """
        self._request_cache: Dict[str, float] = {}
        self._window_seconds = window_seconds
        self._max_cache_size = max_cache_size
    
    def _generate_signature(self, request: Any) -> str:
        """
        Generate a unique signature for a request.
        
        Args:
            request (Any): The request to generate a signature for
        
        Returns:
            str: A unique signature for the request
        """
        # Convert request to a hashable, consistent string representation
        request_str = str(sorted(str(request).split()))
        
        # Include timestamp to prevent exact replays
        current_time = str(int(time.time()))
        
        # Create a hash of the request and timestamp
        return hashlib.sha256(f"{request_str}_{current_time}".encode()).hexdigest()
    
    def is_unique_request(self, request: Any) -> bool:
        """
        Check if a request is unique and has not been seen recently.
        
        Args:
            request (Any): The request to check
        
        Returns:
            bool: True if the request is unique, False if it might be a replay
        """
        current_time = time.time()
        signature = self._generate_signature(request)
        
        # Clean up old entries
        self._cleanup_cache(current_time)
        
        # Check if signature exists and is within the time window
        if signature in self._request_cache:
            return False
        
        # Store the signature with current timestamp
        self._request_cache[signature] = current_time
        
        return True
    
    def _cleanup_cache(self, current_time: float) -> None:
        """
        Remove old entries from the request cache.
        
        Args:
            current_time (float): Current timestamp
        """
        # Remove entries older than window_seconds
        self._request_cache = {
            sig: timestamp for sig, timestamp in self._request_cache.items()
            if current_time - timestamp <= self._window_seconds
        }
        
        # Trim cache if it grows too large
        if len(self._request_cache) > self._max_cache_size:
            # Remove oldest entries first
            sorted_cache = sorted(self._request_cache.items(), key=lambda x: x[1])
            self._request_cache = dict(sorted_cache[-self._max_cache_size:])