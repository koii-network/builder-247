"""
Comprehensive Caching Error Handling Module

This module provides a robust and flexible caching mechanism with 
comprehensive error handling and logging capabilities.
"""

import functools
import time
import logging
from typing import Any, Callable, Optional, Dict
from threading import Lock

logger = logging.getLogger(__name__)

class CacheError(Exception):
    """Base exception for cache-related errors."""
    pass

class CacheTimeoutError(CacheError):
    """Raised when a cache operation times out."""
    pass

class CacheFullError(CacheError):
    """Raised when cache reaches maximum capacity."""
    pass

class CacheManager:
    """
    A thread-safe cache manager with comprehensive error handling.
    
    Features:
    - Thread-safe caching
    - Configurable cache size
    - Automatic expiration
    - Detailed logging
    - Flexible error handling
    """
    
    def __init__(self, max_size: int = 100, default_ttl: int = 300):
        """
        Initialize the cache manager.
        
        Args:
            max_size (int): Maximum number of items in cache
            default_ttl (int): Default time-to-live for cache entries in seconds
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        self._max_size = max_size
        self._default_ttl = default_ttl
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a cache entry with comprehensive error handling.
        
        Args:
            key (str): Cache key
            value (Any): Value to cache
            ttl (int, optional): Time-to-live for this specific entry
        
        Raises:
            CacheFullError: If cache is at maximum capacity
        """
        with self._lock:
            try:
                if len(self._cache) >= self._max_size:
                    raise CacheFullError(f"Cache has reached maximum size of {self._max_size}")
                
                self._cache[key] = {
                    'value': value,
                    'expires_at': time.time() + (ttl or self._default_ttl)
                }
                logger.info(f"Cached value for key: {key}")
            except Exception as e:
                logger.error(f"Error caching value for key {key}: {e}")
                raise
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a cache entry with comprehensive error handling.
        
        Args:
            key (str): Cache key to retrieve
        
        Returns:
            Optional[Any]: Cached value or None
        
        Raises:
            CacheError: If there are cache retrieval issues
        """
        with self._lock:
            try:
                entry = self._cache.get(key)
                
                if not entry:
                    logger.info(f"Cache miss for key: {key}")
                    return None
                
                if time.time() > entry['expires_at']:
                    logger.info(f"Cache expired for key: {key}")
                    del self._cache[key]
                    return None
                
                return entry['value']
            except Exception as e:
                logger.error(f"Error retrieving cache for key {key}: {e}")
                raise CacheError(f"Cache retrieval failed: {e}")
    
    def clear(self) -> None:
        """Clear entire cache with logging."""
        with self._lock:
            try:
                self._cache.clear()
                logger.info("Cache cleared successfully")
            except Exception as e:
                logger.error(f"Error clearing cache: {e}")
                raise

def cached(
    cache_manager: Optional[CacheManager] = None, 
    ttl: Optional[int] = None
) -> Callable:
    """
    Decorator for caching function results with comprehensive error handling.
    
    Args:
        cache_manager (Optional[CacheManager]): Cache manager instance
        ttl (Optional[int]): Time-to-live for cached results
    
    Returns:
        Callable: Decorated function with caching
    """
    if cache_manager is None:
        cache_manager = CacheManager()
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a unique cache key based on function and arguments
            cache_key = f"{func.__module__}.{func.__name__}:{str(args)}:{str(kwargs)}"
            
            try:
                # Attempt to retrieve from cache first
                cached_result = cache_manager.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # If not in cache, execute function
                result = func(*args, **kwargs)
                
                # Cache the result
                cache_manager.set(cache_key, result, ttl)
                
                return result
            
            except CacheError as ce:
                logger.warning(f"Cache error: {ce}. Executing function without cache.")
                return func(*args, **kwargs)
            
            except Exception as e:
                logger.error(f"Unexpected error in cached function: {e}")
                raise
        
        return wrapper
    
    return decorator