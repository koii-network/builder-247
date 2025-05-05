import time
from functools import lru_cache
from typing import Callable, Any

class JokeCache:
    """
    A caching mechanism for jokes with performance tracking and configurable cache size.
    
    This class provides a simple caching solution with the following features:
    - LRU (Least Recently Used) cache
    - Performance tracking
    - Configurable cache size
    """
    
    def __init__(self, max_size: int = 128, ttl: float = 3600.0):
        """
        Initialize the JokeCache.
        
        Args:
            max_size (int): Maximum number of jokes to cache. Defaults to 128.
            ttl (float): Time-to-live for cached jokes in seconds. Defaults to 1 hour.
        """
        self._cache = {}
        self._max_size = max_size
        self._ttl = ttl
        self._hits = 0
        self._misses = 0
        self._total_access_time = 0.0

    def get(self, key: str, fetch_func: Callable[[], Any]) -> Any:
        """
        Get a joke from cache or fetch it using the provided function.
        
        Args:
            key (str): Unique identifier for the joke
            fetch_func (Callable): Function to fetch the joke if not in cache
        
        Returns:
            The cached or freshly fetched joke
        """
        start_time = time.time()
        
        # Check if joke is in cache and not expired
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry['timestamp'] < self._ttl:
                self._hits += 1
                entry['timestamp'] = time.time()  # Update access time
                access_time = time.time() - start_time
                self._total_access_time += access_time
                return entry['value']
        
        # Cache miss: fetch and store the joke
        self._misses += 1
        joke = fetch_func()
        
        # Manage cache size
        if len(self._cache) >= self._max_size:
            # Remove the oldest entry
            oldest_key = min(self._cache, key=lambda k: self._cache[k]['timestamp'])
            del self._cache[oldest_key]
        
        # Store new joke in cache
        self._cache[key] = {
            'value': joke,
            'timestamp': time.time()
        }
        
        access_time = time.time() - start_time
        self._total_access_time += access_time
        
        return joke

    def get_stats(self):
        """
        Retrieve cache performance statistics.
        
        Returns:
            dict: Performance metrics including hits, misses, and average access time
        """
        total_accesses = self._hits + self._misses
        return {
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': self._hits / total_accesses if total_accesses > 0 else 0.0,
            'avg_access_time': (self._total_access_time / total_accesses) if total_accesses > 0 else 0.0
        }

    def clear(self):
        """
        Clear the entire cache and reset statistics.
        """
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        self._total_access_time = 0.0