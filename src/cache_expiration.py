import time
from typing import Any, Dict, Optional


class ExpiringCache:
    """
    A cache implementation with configurable expiration time for entries.
    
    This cache allows storing key-value pairs with a specified time-to-live (TTL).
    Entries are automatically considered expired after their TTL has elapsed.
    """

    def __init__(self, default_ttl: int = 300):
        """
        Initialize the cache with a default time-to-live.

        Args:
            default_ttl (int, optional): Default expiration time in seconds. 
                                         Defaults to 300 seconds (5 minutes).
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = default_ttl

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a key-value pair in the cache with optional TTL.

        Args:
            key (str): The cache key.
            value (Any): The value to store.
            ttl (int, optional): Time-to-live in seconds. 
                                 Uses default_ttl if not specified.
        """
        expiration = time.time() + (ttl or self._default_ttl)
        self._cache[key] = {
            'value': value,
            'expiration': expiration
        }

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache if it hasn't expired.

        Args:
            key (str): The cache key to retrieve.

        Returns:
            Any: The cached value if found and not expired, None otherwise.
        """
        current_time = time.time()
        entry = self._cache.get(key)
        
        if entry is None or current_time > entry['expiration']:
            # Remove expired entries
            if entry:
                del self._cache[key]
            return None

        return entry['value']

    def delete(self, key: str) -> None:
        """
        Remove a specific key from the cache.

        Args:
            key (str): The cache key to delete.
        """
        self._cache.pop(key, None)

    def clear(self) -> None:
        """
        Clear all entries from the cache.
        """
        self._cache.clear()

    def get_all_valid_keys(self) -> list:
        """
        Get all keys that are currently valid (not expired).

        Returns:
            list: List of valid keys in the cache.
        """
        current_time = time.time()
        
        # Remove expired entries as we check
        valid_keys = []
        keys_to_remove = []
        
        for key, entry in self._cache.items():
            if current_time <= entry['expiration']:
                valid_keys.append(key)
            else:
                keys_to_remove.append(key)
        
        # Remove all expired entries
        for key in keys_to_remove:
            del self._cache[key]
        
        return valid_keys