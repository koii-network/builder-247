import time
from typing import Dict, Any, Optional
from functools import lru_cache

class JokeCache:
    """
    A caching mechanism for jokes with configurable cache size and expiration.
    
    This class provides an efficient way to cache and retrieve jokes, 
    with support for cache size limits and optional time-based expiration.
    """
    
    def __init__(self, max_size: int = 100, expiration: float = 3600.0):
        """
        Initialize the JokeCache.
        
        Args:
            max_size (int): Maximum number of jokes to store in the cache. Defaults to 100.
            expiration (float): Time in seconds before a cached joke expires. Defaults to 1 hour.
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._max_size = max_size
        self._expiration = expiration
    
    def add(self, key: str, joke: str) -> None:
        """
        Add a joke to the cache.
        
        Args:
            key (str): Unique identifier for the joke.
            joke (str): The joke text to cache.
        """
        # Remove oldest entry if cache is full
        if len(self._cache) >= self._max_size:
            oldest_key = min(self._cache, key=lambda k: self._cache[k]['timestamp'])
            del self._cache[oldest_key]
        
        # Add new joke
        self._cache[key] = {
            'joke': joke,
            'timestamp': time.time()
        }
    
    def get(self, key: str) -> Optional[str]:
        """
        Retrieve a joke from the cache.
        
        Args:
            key (str): Unique identifier for the joke.
        
        Returns:
            Optional[str]: The joke if found and not expired, otherwise None.
        """
        entry = self._cache.get(key)
        
        if entry is None:
            return None
        
        # Check for expiration
        if time.time() - entry['timestamp'] > self._expiration:
            del self._cache[key]
            return None
        
        return entry['joke']
    
    def clear(self) -> None:
        """
        Clear the entire cache.
        """
        self._cache.clear()
    
    def __len__(self) -> int:
        """
        Get the current number of jokes in the cache.
        
        Returns:
            int: Number of jokes in the cache.
        """
        return len(self._cache)