import time
from functools import lru_cache
from typing import Callable, Any, Optional

class JokeCache:
    """
    A caching mechanism for jokes with performance tracking.
    
    This class provides caching functionality with optional 
    time-based expiration and performance metrics.
    """
    
    def __init__(self, max_size: int = 128, default_ttl: Optional[float] = None):
        """
        Initialize the JokeCache.
        
        :param max_size: Maximum number of jokes to cache
        :param default_ttl: Default time-to-live for cached jokes in seconds
        """
        self._cache = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        
        # Performance tracking
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_lookup_time = 0
    
    def cache(self, func: Callable[..., Any], ttl: Optional[float] = None) -> Callable[..., Any]:
        """
        Decorator to cache function results with optional TTL.
        
        :param func: Function to cache
        :param ttl: Time-to-live for cached results
        :return: Wrapped function with caching
        """
        def wrapper(*args, **kwargs):
            # Generate a unique cache key
            key = str(args) + str(kwargs)
            
            start_time = time.perf_counter()
            
            # Check if result is in cache and not expired
            if key in self._cache:
                cached_result, timestamp = self._cache[key]
                
                # Check TTL if set
                effective_ttl = ttl or self._default_ttl
                if (effective_ttl is None) or (time.time() - timestamp < effective_ttl):
                    self.cache_hits += 1
                    lookup_time = time.perf_counter() - start_time
                    self.total_lookup_time += lookup_time
                    return cached_result
            
            # Cache miss - call the original function
            self.cache_misses += 1
            result = func(*args, **kwargs)
            
            # Store result in cache
            self._cache[key] = (result, time.time())
            
            # Implement LRU by removing oldest entries if exceeding max_size
            if len(self._cache) > self._max_size:
                oldest_key = min(self._cache, key=lambda k: self._cache[k][1])
                del self._cache[oldest_key]
            
            lookup_time = time.perf_counter() - start_time
            self.total_lookup_time += lookup_time
            
            return result
        
        return wrapper
    
    def get_performance_metrics(self) -> dict:
        """
        Retrieve performance metrics for the cache.
        
        :return: Dictionary of performance metrics
        """
        total_lookups = self.cache_hits + self.cache_misses
        
        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': self.cache_hits / total_lookups if total_lookups > 0 else 0,
            'avg_lookup_time': (self.total_lookup_time / total_lookups) if total_lookups > 0 else 0
        }
    
    def clear_cache(self):
        """
        Clear the entire cache and reset performance metrics.
        """
        self._cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_lookup_time = 0