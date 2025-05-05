import time
from functools import lru_cache
from typing import Callable, Any

class JokeCache:
    """
    A utility class for caching jokes with performance tracking.
    
    Provides a caching mechanism with optional performance measurement.
    Supports both decorator and method-based caching.
    """
    
    def __init__(self, max_size: int = 128):
        """
        Initialize the joke cache.
        
        :param max_size: Maximum number of jokes to cache, defaults to 128
        """
        self._cache = {}
        self._max_size = max_size
        self._hits = 0
        self._misses = 0
        self._total_lookup_time = 0
        
    def cached_joke(self, func: Callable) -> Callable:
        """
        Decorator to cache jokes and track performance.
        
        :param func: Function to be cached
        :return: Wrapped function with caching and performance tracking
        """
        cached_func = lru_cache(maxsize=self._max_size)(func)
        
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = cached_func(*args, **kwargs)
                is_hit = cached_func.cache_info().hits > 0
                
                if is_hit:
                    self._hits += 1
                else:
                    self._misses += 1
                
                return result
            finally:
                lookup_time = time.perf_counter() - start_time
                self._total_lookup_time += lookup_time
        
        return wrapper
    
    def get_performance_stats(self) -> dict:
        """
        Retrieve current caching performance statistics.
        
        :return: Dictionary of performance metrics
        """
        return {
            "total_hits": self._hits,
            "total_misses": self._misses,
            "hit_rate": self._hits / (self._hits + self._misses) if (self._hits + self._misses) > 0 else 0,
            "total_lookup_time": self._total_lookup_time
        }
    
    def reset_stats(self) -> None:
        """
        Reset all performance tracking statistics.
        """
        self._hits = 0
        self._misses = 0
        self._total_lookup_time = 0