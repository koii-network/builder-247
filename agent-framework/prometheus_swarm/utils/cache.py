"""Comprehensive Caching Utility with Advanced Error Handling.

This module provides robust caching mechanisms with thorough error management,
supporting flexible storage backends and detailed error tracking.
"""

import json
import os
import threading
import time
from typing import Any, Dict, Optional, Union
from functools import wraps

class CacheError(Exception):
    """Base exception for caching-related errors."""
    pass

class CacheConfigurationError(CacheError):
    """Error raised when cache is improperly configured."""
    pass

class CacheOperationError(CacheError):
    """Error raised during cache read/write operations."""
    pass

class CacheBackend:
    """Abstract base class for cache backends."""
    def __init__(self, cache_dir: str = '/tmp/prometheus_cache'):
        """
        Initialize cache backend with configurable directory.
        
        Args:
            cache_dir (str): Directory to store cache files
        
        Raises:
            CacheConfigurationError: If cache directory cannot be created or accessed
        """
        try:
            os.makedirs(cache_dir, exist_ok=True)
            self.cache_dir = cache_dir
        except (PermissionError, OSError) as e:
            raise CacheConfigurationError(f"Cannot create cache directory: {e}")
    
    def _get_cache_path(self, key: str) -> str:
        """Generate a safe cache file path for a given key."""
        sanitized_key = ''.join(c if c.isalnum() or c in '_-' else '_' for c in key)
        return os.path.join(self.cache_dir, f"{sanitized_key}.cache")
    
    def get(self, key: str, max_age: Optional[int] = None) -> Optional[Any]:
        """
        Retrieve a cached value.
        
        Args:
            key (str): Cache key
            max_age (int, optional): Maximum age of cache in seconds
        
        Returns:
            Cached value or None if not found/expired
        
        Raises:
            CacheOperationError: If reading cache fails
        """
        try:
            path = self._get_cache_path(key)
            if not os.path.exists(path):
                return None
            
            with open(path, 'r') as f:
                cache_data = json.load(f)
            
            if max_age is not None:
                current_time = time.time()
                if current_time - cache_data.get('timestamp', 0) > max_age:
                    return None
            
            return cache_data.get('value')
        except (FileNotFoundError, json.JSONDecodeError, PermissionError) as e:
            raise CacheOperationError(f"Failed to read cache: {e}")
    
    def set(self, key: str, value: Any) -> None:
        """
        Store a value in the cache.
        
        Args:
            key (str): Cache key
            value (Any): Value to cache
        
        Raises:
            CacheOperationError: If writing cache fails
        """
        try:
            path = self._get_cache_path(key)
            cache_data = {
                'value': value,
                'timestamp': time.time()
            }
            
            with open(path, 'w') as f:
                json.dump(cache_data, f)
        except (PermissionError, OSError) as e:
            raise CacheOperationError(f"Failed to write cache: {e}")
    
    def delete(self, key: str) -> None:
        """
        Delete a cached value.
        
        Args:
            key (str): Cache key to delete
        
        Raises:
            CacheOperationError: If deletion fails
        """
        try:
            path = self._get_cache_path(key)
            if os.path.exists(path):
                os.remove(path)
        except (PermissionError, OSError) as e:
            raise CacheOperationError(f"Failed to delete cache: {e}")

class ThreadSafeCache:
    """Thread-safe cache wrapper with advanced error handling."""
    
    def __init__(self, backend: Optional[CacheBackend] = None):
        """
        Initialize thread-safe cache.
        
        Args:
            backend (CacheBackend, optional): Cache backend to use
        """
        self._backend = backend or CacheBackend()
        self._lock = threading.Lock()
    
    def get(self, key: str, max_age: Optional[int] = None) -> Optional[Any]:
        """
        Thread-safe cache retrieval.
        
        Args:
            key (str): Cache key
            max_age (int, optional): Maximum cache age in seconds
        
        Returns:
            Cached value or None
        
        Raises:
            CacheOperationError: If retrieval fails
        """
        with self._lock:
            try:
                return self._backend.get(key, max_age)
            except CacheError as e:
                # Log error or handle as needed
                return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Thread-safe cache storage.
        
        Args:
            key (str): Cache key
            value (Any): Value to cache
        """
        with self._lock:
            try:
                self._backend.set(key, value)
            except CacheError:
                # Log error or handle as needed
                pass
    
    def delete(self, key: str) -> None:
        """
        Thread-safe cache deletion.
        
        Args:
            key (str): Cache key to delete
        """
        with self._lock:
            try:
                self._backend.delete(key)
            except CacheError:
                # Log error or handle as needed
                pass

def cacheable(max_age: Optional[int] = None, cache: Optional[ThreadSafeCache] = None):
    """
    Decorator for function caching with advanced error handling.
    
    Args:
        max_age (int, optional): Maximum cache age in seconds
        cache (ThreadSafeCache, optional): Custom cache instance
    
    Returns:
        Decorated function with caching
    """
    if cache is None:
        cache = ThreadSafeCache()
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a unique cache key based on function and arguments
            key = f"{func.__module__}.{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to retrieve cached result
            cached_result = cache.get(key, max_age)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            try:
                result = func(*args, **kwargs)
                cache.set(key, result)
                return result
            except Exception as e:
                # Optional: Add logging or error tracking
                raise
        
        return wrapper
    return decorator