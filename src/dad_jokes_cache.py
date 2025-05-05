from typing import Dict, Any, Optional
from collections import OrderedDict
import threading

class DadJokesCache:
    """
    An in-memory cache for Dad Jokes with thread-safe operations
    and configurable max size.
    
    Features:
    - LRU (Least Recently Used) eviction strategy
    - Thread-safe operations
    - Optional max cache size
    """
    
    def __init__(self, max_size: Optional[int] = None):
        """
        Initialize the Dad Jokes Cache
        
        Args:
            max_size (Optional[int]): Maximum number of jokes to store. 
                                      If None, cache size is unlimited.
        """
        self._cache: OrderedDict = OrderedDict()
        self._max_size = max_size
        self._lock = threading.Lock()
    
    def add(self, joke_id: str, joke_data: Dict[str, Any]) -> bool:
        """
        Add a joke to the cache
        
        Args:
            joke_id (str): Unique identifier for the joke
            joke_data (Dict[str, Any]): Joke details
        
        Returns:
            bool: True if added successfully, False if joke already exists
        """
        with self._lock:
            if joke_id in self._cache:
                return False
            
            # Check max size before adding
            if self._max_size is not None and len(self._cache) >= self._max_size:
                # Remove the least recently used item
                self._cache.popitem(last=False)
            
            self._cache[joke_id] = joke_data
            return True
    
    def get(self, joke_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a joke from the cache
        
        Args:
            joke_id (str): Unique identifier for the joke
        
        Returns:
            Optional[Dict[str, Any]]: Joke data if found, None otherwise
        """
        with self._lock:
            if joke_id not in self._cache:
                return None
            
            # Move the accessed item to the end (most recently used)
            value = self._cache[joke_id]
            del self._cache[joke_id]
            self._cache[joke_id] = value
            
            return value
    
    def remove(self, joke_id: str) -> bool:
        """
        Remove a joke from the cache
        
        Args:
            joke_id (str): Unique identifier for the joke
        
        Returns:
            bool: True if joke was found and removed, False otherwise
        """
        with self._lock:
            if joke_id not in self._cache:
                return False
            
            del self._cache[joke_id]
            return True
    
    def clear(self) -> None:
        """
        Clear all jokes from the cache
        """
        with self._lock:
            self._cache.clear()
    
    def size(self) -> int:
        """
        Get the current number of jokes in the cache
        
        Returns:
            int: Number of jokes in the cache
        """
        with self._lock:
            return len(self._cache)
    
    def get_all_jokes(self) -> Dict[str, Any]:
        """
        Get all jokes in the cache
        
        Returns:
            Dict[str, Any]: Copy of all jokes in the cache
        """
        with self._lock:
            return dict(self._cache)