"""
Cache Performance and Memory Limits Configuration Module

This module provides configuration and management for cache performance
and memory limits in the Prometheus Swarm framework.
"""

import psutil
import functools
import logging
from typing import Any, Callable

class CacheConfig:
    """
    Configures and manages cache performance and memory limits.
    """

    def __init__(self, 
                 max_memory_percent: float = 70.0, 
                 max_cache_size: int = 1000):
        """
        Initialize cache configuration with memory and size limits.

        Args:
            max_memory_percent (float): Maximum percentage of system memory to use. Defaults to 70%.
            max_cache_size (int): Maximum number of items to keep in cache. Defaults to 1000.
        """
        self.max_memory_percent = max_memory_percent
        self.max_cache_size = max_cache_size
        self.logger = logging.getLogger(__name__)

    def memory_limit_decorator(self, func: Callable) -> Callable:
        """
        Decorator to enforce memory usage limits for cached function calls.

        Args:
            func (Callable): The function to wrap with memory limit checks.

        Returns:
            Callable: Wrapped function with memory limit checks.
        """
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_memory_percent = psutil.virtual_memory().percent

            if current_memory_percent > self.max_memory_percent:
                self.logger.warning(
                    f"Memory usage ({current_memory_percent}%) exceeds limit "
                    f"({self.max_memory_percent}%). Clearing cache."
                )
                # Implement cache clearing mechanism here if needed
                raise MemoryError(f"Memory usage too high: {current_memory_percent}%")

            return func(*args, **kwargs)
        return wrapper

    def cached_with_limit(self, maxsize: int = None):
        """
        Create a cached decorator with size and memory limits.

        Args:
            maxsize (int, optional): Maximum number of items to cache. 
                                     Defaults to self.max_cache_size if not provided.

        Returns:
            Callable: Cached decorator with memory and size limits.
        """
        if maxsize is None:
            maxsize = self.max_cache_size

        def decorator(func: Callable) -> Callable:
            cached_func = functools.lru_cache(maxsize=maxsize)(func)
            return self.memory_limit_decorator(cached_func)

        return decorator

# Create a default global instance
default_cache_config = CacheConfig()