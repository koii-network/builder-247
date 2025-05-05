import time
from functools import lru_cache
from typing import Callable, Any

class JokeCache:
    """
    A caching mechanism for jokes with performance tracking.
    
    This class provides caching for jokes and tracks performance metrics
    such as cache hits, misses, and retrieval times.
    """
    
    def __init__(self, max_size: int = 128):
        """
        Initialize the JokeCache with a specified maximum cache size.
        
        :param max_size: Maximum number of jokes to cache
        """
        self._cache = {}
        self._max_size = max_size
        self._hits = 0
        self._misses = 0
        self._total_retrieval_time = 0
    
    def get(self, key: str, fetch_func: Callable[[str], Any]) -> Any:
        """
        Retrieve a joke from cache or fetch it using the provided function.
        
        :param key: Unique identifier for the joke
        :param fetch_func: Function to fetch the joke if not in cache
        :return: The cached or fetched joke
        """
        start_time = time.time()
        
        # Check if joke is in cache
        if key in self._cache:
            self._hits += 1
            retrieval_time = time.time() - start_time
            self._total_retrieval_time += retrieval_time
            return self._cache[key]
        
        # Fetch joke and add to cache
        self._misses += 1
        joke = fetch_func(key)
        
        # Manage cache size
        if len(self._cache) >= self._max_size:
            # Remove oldest entry if cache is full
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        self._cache[key] = joke
        
        retrieval_time = time.time() - start_time
        self._total_retrieval_time += retrieval_time
        
        return joke
    
    def get_performance_metrics(self) -> dict:
        """
        Retrieve performance metrics for the joke cache.
        
        :return: Dictionary of performance metrics
        """
        return {
            'total_hits': self._hits,
            'total_misses': self._misses,
            'cache_hit_ratio': (self._hits / (self._hits + self._misses)) if (self._hits + self._misses) > 0 else 0,
            'avg_retrieval_time': (self._total_retrieval_time / (self._hits + self._misses)) if (self._hits + self._misses) > 0 else 0,
            'current_cache_size': len(self._cache),
            'max_cache_size': self._max_size
        }
    
    def clear(self):
        """
        Clear the entire cache and reset performance metrics.
        """
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        self._total_retrieval_time = 0