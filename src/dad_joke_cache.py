from typing import Dict, Optional
from datetime import datetime, timedelta
import uuid

class DadJokeCache:
    """
    An in-memory cache for Dad Jokes with expiration and management features.
    
    The cache allows storing jokes with unique identifiers, optional expiration,
    and provides methods for adding, retrieving, and managing jokes.
    """
    
    def __init__(self, max_size: int = 100, default_expiration: int = 3600):
        """
        Initialize the Dad Joke Cache.
        
        Args:
            max_size (int, optional): Maximum number of jokes to store. Defaults to 100.
            default_expiration (int, optional): Default expiration time in seconds. Defaults to 1 hour.
        """
        self._cache: Dict[str, Dict] = {}
        self._max_size = max_size
        self._default_expiration = default_expiration
    
    def add_joke(self, joke: str, expiration: Optional[int] = None) -> str:
        """
        Add a joke to the cache.
        
        Args:
            joke (str): The dad joke to store
            expiration (int, optional): Expiration time in seconds. If None, uses default.
        
        Returns:
            str: Unique identifier for the stored joke
        
        Raises:
            ValueError: If cache is full
        """
        # Check cache size
        if len(self._cache) >= self._max_size:
            raise ValueError("Cache is full. Cannot add more jokes.")
        
        # Generate unique identifier
        joke_id = str(uuid.uuid4())
        
        # Set expiration time
        expires_at = datetime.now() + timedelta(
            seconds=expiration or self._default_expiration
        )
        
        # Store joke with metadata
        self._cache[joke_id] = {
            'joke': joke,
            'created_at': datetime.now(),
            'expires_at': expires_at
        }
        
        return joke_id
    
    def get_joke(self, joke_id: str) -> Optional[str]:
        """
        Retrieve a joke by its ID.
        
        Args:
            joke_id (str): Unique identifier of the joke
        
        Returns:
            Optional[str]: The joke text if found and not expired, None otherwise
        """
        # Check if joke exists
        if joke_id not in self._cache:
            return None
        
        # Check expiration
        joke_entry = self._cache[joke_id]
        if datetime.now() > joke_entry['expires_at']:
            # Remove expired joke
            del self._cache[joke_id]
            return None
        
        return joke_entry['joke']
    
    def remove_joke(self, joke_id: str) -> bool:
        """
        Remove a joke from the cache.
        
        Args:
            joke_id (str): Unique identifier of the joke
        
        Returns:
            bool: True if joke was removed, False if not found
        """
        if joke_id in self._cache:
            del self._cache[joke_id]
            return True
        return False
    
    def clear_expired(self) -> int:
        """
        Remove all expired jokes from the cache.
        
        Returns:
            int: Number of jokes removed
        """
        now = datetime.now()
        expired_jokes = [
            joke_id for joke_id, joke_entry 
            in self._cache.items() 
            if now > joke_entry['expires_at']
        ]
        
        for joke_id in expired_jokes:
            del self._cache[joke_id]
        
        return len(expired_jokes)
    
    def get_cache_size(self) -> int:
        """
        Get the current number of jokes in the cache.
        
        Returns:
            int: Number of jokes currently in the cache
        """
        return len(self._cache)
    
    def get_max_size(self) -> int:
        """
        Get the maximum cache size.
        
        Returns:
            int: Maximum number of jokes the cache can hold
        """
        return self._max_size