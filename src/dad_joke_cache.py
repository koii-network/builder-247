from typing import Dict, Optional
from collections import OrderedDict

class DadJokeCache:
    """
    An in-memory cache for dad jokes with a fixed maximum capacity.
    
    The cache uses LRU (Least Recently Used) eviction strategy when 
    the maximum capacity is reached.
    
    Attributes:
        _max_capacity (int): Maximum number of jokes the cache can hold
        _cache (OrderedDict): Ordered dictionary to maintain joke entries
    """
    
    def __init__(self, max_capacity: int = 100):
        """
        Initialize the dad joke cache.
        
        Args:
            max_capacity (int, optional): Maximum number of jokes to cache. 
                Defaults to 100.
        
        Raises:
            ValueError: If max_capacity is less than 1
        """
        if max_capacity < 1:
            raise ValueError("Cache capacity must be at least 1")
        
        self._max_capacity = max_capacity
        self._cache: OrderedDict[str, str] = OrderedDict()
    
    def add(self, joke_id: str, joke_text: str) -> None:
        """
        Add a dad joke to the cache.
        
        If the cache is at max capacity, the least recently used joke is removed.
        If the joke already exists, it is moved to the most recently used position.
        
        Args:
            joke_id (str): Unique identifier for the joke
            joke_text (str): Text of the dad joke
        
        Raises:
            ValueError: If joke_id or joke_text is empty
        """
        if not joke_id or not joke_text:
            raise ValueError("Joke ID and text must not be empty")
        
        # If joke already exists, move it to the end (most recently used)
        if joke_id in self._cache:
            del self._cache[joke_id]
        
        # If cache is full, remove the least recently used item
        if len(self._cache) >= self._max_capacity:
            self._cache.popitem(last=False)
        
        # Add the new joke
        self._cache[joke_id] = joke_text
    
    def get(self, joke_id: str) -> Optional[str]:
        """
        Retrieve a dad joke from the cache.
        
        If the joke is found, it is moved to the most recently used position.
        
        Args:
            joke_id (str): Unique identifier for the joke
        
        Returns:
            Optional[str]: The joke text if found, None otherwise
        """
        if joke_id not in self._cache:
            return None
        
        # Move the joke to the end (most recently used)
        joke_text = self._cache[joke_id]
        del self._cache[joke_id]
        self._cache[joke_id] = joke_text
        
        return joke_text
    
    def remove(self, joke_id: str) -> bool:
        """
        Remove a dad joke from the cache.
        
        Args:
            joke_id (str): Unique identifier for the joke
        
        Returns:
            bool: True if the joke was removed, False if not found
        """
        if joke_id not in self._cache:
            return False
        
        del self._cache[joke_id]
        return True
    
    def clear(self) -> None:
        """
        Clear all jokes from the cache.
        """
        self._cache.clear()
    
    def get_capacity(self) -> int:
        """
        Get the maximum capacity of the cache.
        
        Returns:
            int: Maximum number of jokes the cache can hold
        """
        return self._max_capacity
    
    def get_current_size(self) -> int:
        """
        Get the current number of jokes in the cache.
        
        Returns:
            int: Current number of jokes in the cache
        """
        return len(self._cache)
    
    def contains(self, joke_id: str) -> bool:
        """
        Check if a joke is in the cache.
        
        Args:
            joke_id (str): Unique identifier for the joke
        
        Returns:
            bool: True if the joke is in the cache, False otherwise
        """
        return joke_id in self._cache