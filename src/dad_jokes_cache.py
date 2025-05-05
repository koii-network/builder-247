from typing import Dict, Any, Optional
from collections import OrderedDict
import threading
import time

class DadJokesCache:
    """
    An in-memory cache for Dad Jokes with thread-safe operations
    and configurable max size and expiration.
    
    Features:
    - LRU (Least Recently Used) eviction strategy
    - Thread-safe operations
    - Optional max cache size
    - Optional joke expiration
    """
    
    def __init__(self, max_size: Optional[int] = None, joke_expiry: Optional[int] = None):
        """
        Initialize the Dad Jokes Cache
        
        Args:
            max_size (Optional[int]): Maximum number of jokes to store. 
                                      If None, cache size is unlimited.
            joke_expiry (Optional[int]): Time in seconds after which a joke expires.
                                         If None, jokes do not expire.
        """
        self._cache: OrderedDict = OrderedDict()
        self._max_size = max_size or float('inf')
        self._joke_expiry = joke_expiry
        self._lock = threading.Lock()
    
    def add(self, joke_id: str, joke_data: Dict[str, Any]) -> bool:
        """
        Add a joke to the cache
        
        Args:
            joke_id (str): Unique identifier for the joke
            joke_data (Dict[str, Any]): Joke details with timestamp
        
        Returns:
            bool: True if added successfully, False if joke already exists
        """
        with self._lock:
            if joke_id in self._cache:
                return False
            
            # Check max size before adding
            if len(self._cache) >= self._max_size:
                # Remove the least recently used item
                self._cache.popitem(last=False)
            
            # Ensure timestamp is added if not present
            if 'timestamp' not in joke_data:
                joke_data['timestamp'] = time.time()
            
            self._cache[joke_id] = joke_data
            return True
    
    def get(self, joke_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a joke from the cache
        
        Args:
            joke_id (str): Unique identifier for the joke
        
        Returns:
            Optional[Dict[str, Any]]: Joke data if found and not expired, None otherwise
        """
        with self._lock:
            if joke_id not in self._cache:
                return None
            
            # Check for expiration
            joke_data = self._cache[joke_id]
            if self._is_expired(joke_data):
                del self._cache[joke_id]
                return None
            
            # Move the accessed item to the end (most recently used)
            value = self._cache[joke_id]
            del self._cache[joke_id]
            self._cache[joke_id] = value
            
            return value
    
    def exists(self, joke_id: str) -> bool:
        """
        Check if a joke exists in the cache and is not expired
        
        Args:
            joke_id (str): Unique identifier for the joke
        
        Returns:
            bool: True if joke exists and is not expired, False otherwise
        """
        with self._lock:
            if joke_id not in self._cache:
                return False
            
            # Check for expiration
            joke_data = self._cache[joke_id]
            if self._is_expired(joke_data):
                del self._cache[joke_id]
                return False
            
            return True
    
    def _is_expired(self, joke_data: Dict[str, Any]) -> bool:
        """
        Check if a joke has expired
        
        Args:
            joke_data (Dict[str, Any]): Joke data
        
        Returns:
            bool: True if joke is expired, False otherwise
        """
        if self._joke_expiry is None:
            return False
        
        current_time = time.time()
        return current_time - joke_data['timestamp'] > self._joke_expiry
    
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
            Dict[str, Any]: Copy of all non-expired jokes in the cache
        """
        with self._lock:
            current_time = time.time()
            return {
                k: v for k, v in self._cache.items() 
                if not (self._joke_expiry and current_time - v['timestamp'] > self._joke_expiry)
            }