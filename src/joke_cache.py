import functools
import time
from typing import Callable, Any, Dict

class JokeCache:
    """
    A simple in-memory caching mechanism for joke retrieval.
    
    Provides decorators and methods to cache function results with optional expiration.
    """
    
    def __init__(self, default_expiry: int = 3600):
        """
        Initialize the joke cache.
        
        :param default_expiry: Default cache expiration time in seconds (default: 1 hour)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_expiry = default_expiry
    
    def cached(self, expiry: int = None):
        """
        Decorator to cache function results.
        
        :param expiry: Specific expiration time for this cache entry
        :return: Decorated function with caching
        """
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Create a cache key based on function name and arguments
                cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                
                # Check if entry exists and is not expired
                if self.is_cached(cache_key):
                    return self.get(cache_key)
                
                # Call the original function
                result = func(*args, **kwargs)
                
                # Store the result in cache
                cache_expiry = expiry or self._default_expiry
                self.set(cache_key, result, cache_expiry)
                
                return result
            return wrapper
        return decorator
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """
        Generate a unique cache key based on function name and arguments.
        
        :param func_name: Name of the function
        :param args: Positional arguments
        :param kwargs: Keyword arguments
        :return: Unique cache key
        """
        key_parts = [func_name]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return ":".join(key_parts)
    
    def set(self, key: str, value: Any, expiry: int = None):
        """
        Set a value in the cache with an optional expiration.
        
        :param key: Cache key
        :param value: Value to store
        :param expiry: Expiration time in seconds
        """
        expiry = expiry or self._default_expiry
        self._cache[key] = {
            'value': value,
            'expires_at': time.time() + expiry
        }
    
    def get(self, key: str) -> Any:
        """
        Retrieve a value from the cache.
        
        :param key: Cache key
        :return: Cached value
        :raises KeyError: If key is not found or has expired
        """
        if not self.is_cached(key):
            raise KeyError(f"Cache key '{key}' not found or expired")
        return self._cache[key]['value']
    
    def is_cached(self, key: str) -> bool:
        """
        Check if a key exists in the cache and has not expired.
        
        :param key: Cache key
        :return: True if key exists and is not expired, False otherwise
        """
        if key not in self._cache:
            return False
        
        return time.time() < self._cache[key]['expires_at']
    
    def clear(self, key: str = None):
        """
        Clear cache entries.
        
        :param key: Optional specific key to clear. If None, clears entire cache.
        """
        if key:
            self._cache.pop(key, None)
        else:
            self._cache.clear()