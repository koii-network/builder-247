import time
from typing import Dict, Any, Optional

class JokeCache:
    """
    A caching mechanism for jokes with configurable expiration and capacity.
    
    Attributes:
        _cache (Dict[str, Dict[str, Any]]): Internal cache storage
        _max_size (int): Maximum number of jokes to store
        _expiration_time (float): Time-to-live for cached jokes in seconds
    """
    
    def __init__(self, max_size: int = 100, expiration_time: float = 3600.0):
        """
        Initialize the joke cache.
        
        Args:
            max_size (int, optional): Maximum number of jokes to cache. Defaults to 100.
            expiration_time (float, optional): Time-to-live for jokes in seconds. Defaults to 1 hour.
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._max_size = max_size
        self._expiration_time = expiration_time
    
    def add_joke(self, joke_id: str, joke_data: Dict[str, Any]) -> bool:
        """
        Add a joke to the cache.
        
        Args:
            joke_id (str): Unique identifier for the joke
            joke_data (Dict[str, Any]): Joke content and metadata
        
        Returns:
            bool: True if joke was added, False if cache is full
        """
        # Remove expired entries before adding new joke
        self._clean_expired_entries()
        
        # Check if cache is at max capacity
        if len(self._cache) >= self._max_size:
            return False
        
        # Add joke with current timestamp
        self._cache[joke_id] = {
            'data': joke_data,
            'timestamp': time.time()
        }
        return True
    
    def get_joke(self, joke_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a joke from the cache.
        
        Args:
            joke_id (str): Unique identifier for the joke
        
        Returns:
            Optional[Dict[str, Any]]: Joke data if found and not expired, None otherwise
        """
        # Check if joke exists and is not expired
        entry = self._cache.get(joke_id)
        if not entry:
            return None
        
        current_time = time.time()
        if current_time - entry['timestamp'] > self._expiration_time:
            del self._cache[joke_id]
            return None
        
        return entry['data']
    
    def _clean_expired_entries(self) -> None:
        """
        Remove expired jokes from the cache.
        """
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time - entry['timestamp'] > self._expiration_time
        ]
        
        for key in expired_keys:
            del self._cache[key]
    
    def clear(self) -> None:
        """
        Clear the entire cache.
        """
        self._cache.clear()
    
    def get_cache_size(self) -> int:
        """
        Get the current number of jokes in the cache.
        
        Returns:
            int: Number of jokes in the cache
        """
        return len(self._cache)