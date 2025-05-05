"""
Module for configuring cache performance and memory limits.

This module provides utilities to manage cache and memory configurations
for the Prometheus Swarm Agent Framework.
"""

import psutil
import functools
import threading
from typing import Optional, Callable, Any


class CachePerformanceConfig:
    """
    Manages cache performance and memory limits for the application.
    
    Provides decorators and utilities to control memory usage and caching strategies.
    """
    
    def __init__(
        self, 
        max_memory_percent: float = 80.0, 
        cache_size_limit: Optional[int] = None
    ):
        """
        Initialize cache and memory configuration.
        
        Args:
            max_memory_percent (float): Maximum percentage of system memory to use. 
                Defaults to 80% of total memory.
            cache_size_limit (Optional[int]): Maximum number of items to keep in cache.
                If None, no explicit size limit is set.
        """
        self._max_memory_percent = max_memory_percent
        self._cache_size_limit = cache_size_limit
        self._cache = {}
        self._cache_lock = threading.Lock()
    
    def memory_check(self) -> bool:
        """
        Check if current memory usage is within allowed limits.
        
        Returns:
            bool: True if memory usage is below max_memory_percent, False otherwise.
        """
        memory_usage = psutil.virtual_memory().percent
        return memory_usage <= self._max_memory_percent
    
    def cached(self, func: Callable) -> Callable:
        """
        A decorator to add caching with memory and size limit management.
        
        Args:
            func (Callable): Function to be cached.
        
        Returns:
            Callable: Wrapped function with caching and memory management.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key from function arguments
            key = str(args) + str(kwargs)
            
            # Check if entry exists in cache
            with self._cache_lock:
                if key in self._cache:
                    return self._cache[key]
                
                # Enforce cache size limit if set
                if (self._cache_size_limit is not None and 
                    len(self._cache) >= self._cache_size_limit):
                    # Remove oldest entry
                    self._cache.pop(next(iter(self._cache)))
            
            # Check memory before computation
            if not self.memory_check():
                raise MemoryError("Memory usage exceeds configured limit")
            
            # Compute result and cache it
            result = func(*args, **kwargs)
            
            with self._cache_lock:
                self._cache[key] = result
            
            return result
        
        return wrapper


# Global instance for easy import and use
cache_config = CachePerformanceConfig()