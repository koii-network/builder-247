import time
from functools import wraps
from typing import Dict, Any

class ReplayPreventionError(Exception):
    """Exception raised for replay attack attempts."""
    pass

class ReplayPreventionMiddleware:
    """
    Middleware to prevent replay attacks by tracking request timestamps.
    
    This implementation uses a sliding window approach to prevent replay attacks.
    It maintains a cache of recent request signatures and their timestamps.
    """
    
    def __init__(self, window_seconds: int = 60, max_cache_size: int = 1000):
        """
        Initialize the replay prevention middleware.
        
        :param window_seconds: Time window in seconds for considering a request unique
        :param max_cache_size: Maximum number of requests to cache
        """
        self._request_cache: Dict[str, float] = {}
        self._window_seconds = window_seconds
        self._max_cache_size = max_cache_size
    
    def _clean_cache(self):
        """Remove old entries from the cache."""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self._request_cache.items() 
            if current_time - timestamp > self._window_seconds
        ]
        for key in expired_keys:
            del self._request_cache[key]
    
    def is_replay_request(self, request_signature: str) -> bool:
        """
        Check if a request is a potential replay attack.
        
        :param request_signature: Unique signature for the request
        :return: True if the request is a potential replay, False otherwise
        """
        # Clean up old cache entries
        self._clean_cache()
        
        # Check if the signature exists in recent requests
        current_time = time.time()
        
        if request_signature in self._request_cache:
            return True
        
        # Add new request to cache
        self._request_cache[request_signature] = current_time
        
        # Limit cache size
        if len(self._request_cache) > self._max_cache_size:
            # Remove the oldest entry
            oldest_key = min(self._request_cache, key=self._request_cache.get)
            del self._request_cache[oldest_key]
        
        return False

# Global middleware instance
replay_prevention = ReplayPreventionMiddleware()

def prevent_replay(f):
    """
    Decorator to prevent replay attacks on route handlers.
    
    The request signature is created from the request's body and timestamp.
    
    :raises ReplayPreventionError: If a potential replay attack is detected
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Create a request signature
        request = args[0] if args else kwargs.get('request')
        
        if not request:
            raise ValueError("No request object found")
        
        # Extract request body and timestamp
        try:
            request_body = request.get_json() if hasattr(request, 'get_json') else {}
        except Exception:
            request_body = {}
        
        current_time = time.time()
        request_signature = f"{hash(frozenset(request_body.items()))}-{current_time}"
        
        # Check for replay attack
        if replay_prevention.is_replay_request(request_signature):
            raise ReplayPreventionError("Potential replay attack detected")
        
        return f(*args, **kwargs)
    return wrapper