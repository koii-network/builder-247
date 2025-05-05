import functools
import os
from typing import Any, Callable, Dict, Optional

class CacheConfig:
    """
    A utility class for configuring cache performance and memory limits.
    
    This class provides methods to:
    - Set global cache size limits
    - Configure caching strategies
    - Implement memory-aware caching decorators
    """
    
    def __init__(self, 
                 max_cache_size: Optional[int] = None, 
                 max_memory_percent: float = 0.5):
        """
        Initialize cache configuration.
        
        Args:
            max_cache_size (Optional[int]): Maximum number of items to cache. 
                Defaults to None (unlimited).
            max_memory_percent (float): Maximum percentage of system memory 
                to use for caching. Defaults to 0.5 (50%).
        """
        self._max_cache_size = max_cache_size
        self._max_memory_percent = max_memory_percent
        self._cache: Dict[str, Any] = {}
    
    def memory_limit_decorator(self, func: Callable) -> Callable:
        """
        A decorator that adds memory-aware caching to a function.
        
        Args:
            func (Callable): The function to be cached.
        
        Returns:
            Callable: A wrapped function with caching and memory management.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate a unique cache key based on function arguments
            cache_key = str(args) + str(kwargs)
            
            # Check if result is already cached
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            # Check memory limits before caching
            if self._is_memory_limit_exceeded():
                self._clear_cache()
            
            # Check cache size limit
            if (self._max_cache_size is not None and 
                len(self._cache) >= self._max_cache_size):
                # Remove oldest item if cache is full
                self._cache.pop(list(self._cache.keys())[0])
            
            # Compute and cache result
            result = func(*args, **kwargs)
            self._cache[cache_key] = result
            
            return result
        
        return wrapper
    
    def _is_memory_limit_exceeded(self) -> bool:
        """
        Check if the current memory usage exceeds configured limits.
        
        Returns:
            bool: True if memory limit is exceeded, False otherwise.
        """
        try:
            import psutil
            
            # Get system memory usage
            memory = psutil.virtual_memory()
            memory_used_percent = memory.percent / 100.0
            
            return memory_used_percent > self._max_memory_percent
        except ImportError:
            # Default to False if psutil is not available
            return False
    
    def _clear_cache(self):
        """
        Clear the entire cache when memory limits are exceeded.
        """
        self._cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Retrieve current cache statistics.
        
        Returns:
            Dict[str, Any]: A dictionary with cache statistics.
        """
        return {
            'cache_size': len(self._cache),
            'max_cache_size': self._max_cache_size,
            'max_memory_percent': self._max_memory_percent
        }

# Global cache configuration instance
global_cache_config = CacheConfig()