import functools
from typing import Any, Callable
from datetime import datetime, timedelta

class JokeCache:
    """
    A simple in-memory cache for joke retrieval with time-based expiration.
    
    Args:
        max_age (int): Maximum age of cache entries in seconds. Defaults to 1 hour.
        max_size (int): Maximum number of entries to keep in cache. Defaults to 100.
    """
    def __init__(self, max_age: int = 3600, max_size: int = 100):
        self._cache = {}
        self._max_age = max_age
        self._max_size = max_size

    def _cleanup_expired(self):
        """Remove expired cache entries."""
        now = datetime.now()
        expired_keys = [
            key for key, (value, timestamp) in self._cache.items()
            if (now - timestamp).total_seconds() > self._max_age
        ]
        for key in expired_keys:
            del self._cache[key]

    def _prune_cache(self):
        """Ensure cache does not exceed maximum size."""
        if len(self._cache) > self._max_size:
            # Remove oldest entries first
            sorted_items = sorted(
                self._cache.items(), 
                key=lambda x: x[1][1]
            )
            for key, _ in sorted_items[:len(self._cache) - self._max_size]:
                del self._cache[key]

    def cached(self, func: Callable) -> Callable:
        """
        Decorator to cache function results.
        
        Args:
            func (Callable): Function to be cached.
        
        Returns:
            Callable: Wrapped function with caching logic.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a hashable cache key
            key = str(args) + str(kwargs)
            
            # Cleanup expired entries
            self._cleanup_expired()
            
            # Check if result is in cache
            if key in self._cache:
                result, _ = self._cache[key]
                return result
            
            # Call original function
            result = func(*args, **kwargs)
            
            # Store result in cache
            self._cache[key] = (result, datetime.now())
            
            # Prune cache if needed
            self._prune_cache()
            
            return result
        
        return wrapper

# Global joke cache instance
joke_cache = JokeCache()