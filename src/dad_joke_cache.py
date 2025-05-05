from typing import Dict, Optional
import time
from collections import OrderedDict

class DadJokeCache:
    """
    An in-memory cache for Dad Jokes with configurable capacity and time-based expiration.
    
    Features:
    - Fixed capacity limit
    - Automatic expiration of jokes
    - Thread-safe operations
    - O(1) average time complexity for get and set operations
    """
    
    def __init__(self, capacity: int = 100, max_age_seconds: int = 3600):
        """
        Initialize the Dad Joke Cache
        
        :param capacity: Maximum number of jokes to store (default 100)
        :param max_age_seconds: Maximum age of a joke before it expires (default 1 hour)
        """
        self._cache: Dict[str, Dict] = OrderedDict()
        self._capacity = max(1, capacity)  # Ensure at least 1 capacity
        self._max_age = max(0, max_age_seconds)
    
    def add(self, joke_id: str, joke_text: str) -> bool:
        """
        Add a new joke to the cache
        
        :param joke_id: Unique identifier for the joke
        :param joke_text: The text of the joke
        :return: True if added successfully, False if not
        """
        if not joke_id or not joke_text:
            return False
        
        # Remove expired entries before adding
        self._remove_expired_entries()
        
        # If joke already exists, update its timestamp
        if joke_id in self._cache:
            del self._cache[joke_id]
        
        # If cache is full, remove the oldest entry
        if len(self._cache) >= self._capacity:
            self._cache.popitem(last=False)
        
        # Add new joke with current timestamp
        self._cache[joke_id] = {
            'text': joke_text,
            'timestamp': time.time()
        }
        
        return True
    
    def get(self, joke_id: str) -> Optional[str]:
        """
        Retrieve a joke from the cache
        
        :param joke_id: Unique identifier for the joke
        :return: Joke text if found and not expired, None otherwise
        """
        # Remove expired entries before retrieving
        self._remove_expired_entries()
        
        joke_entry = self._cache.get(joke_id)
        
        if joke_entry:
            # Move the accessed item to the end (most recently used)
            del self._cache[joke_id]
            self._cache[joke_id] = joke_entry
            return joke_entry['text']
        
        return None
    
    def _remove_expired_entries(self) -> None:
        """
        Remove entries that have exceeded the maximum age
        """
        current_time = time.time()
        expired_keys = [
            key for key, value in self._cache.items() 
            if current_time - value['timestamp'] > self._max_age
        ]
        
        for key in expired_keys:
            del self._cache[key]
    
    def clear(self) -> None:
        """
        Clear all entries from the cache
        """
        self._cache.clear()
    
    def __len__(self) -> int:
        """
        Get the current number of jokes in the cache
        
        :return: Number of jokes in the cache
        """
        self._remove_expired_entries()
        return len(self._cache)
    
    def capacity(self) -> int:
        """
        Get the maximum capacity of the cache
        
        :return: Maximum number of jokes the cache can hold
        """
        return self._capacity