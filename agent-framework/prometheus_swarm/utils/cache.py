import time
from typing import Any, Dict, Optional

class ExpiringCache:
    """
    A thread-safe, time-based cache implementation with expiration support.
    
    This cache allows storing key-value pairs with optional expiration times.
    Expired entries are automatically removed when accessed or during cleanup.
    """
    
    def __init__(self, default_ttl: Optional[float] = None):
        """
        Initialize an ExpiringCache.
        
        Args:
            default_ttl (Optional[float]): Default time-to-live in seconds for cache entries.
                If None, entries will not expire by default.
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = default_ttl
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """
        Set a value in the cache with an optional time-to-live.
        
        Args:
            key (str): The cache key.
            value (Any): The value to store.
            ttl (Optional[float]): Time-to-live in seconds. 
                If None, uses the default TTL set during initialization.
        """
        expiry = time.time() + (ttl or self._default_ttl) if ttl is not None or self._default_ttl is not None else None
        self._cache[key] = {
            'value': value,
            'expiry': expiry
        }
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache, checking for expiration.
        
        Args:
            key (str): The cache key to retrieve.
        
        Returns:
            Optional[Any]: The cached value if found and not expired, otherwise None.
        """
        entry = self._cache.get(key)
        
        if entry is None:
            return None
        
        if entry['expiry'] is not None and time.time() > entry['expiry']:
            del self._cache[key]
            return None
        
        return entry['value']
    
    def delete(self, key: str):
        """
        Delete a specific key from the cache.
        
        Args:
            key (str): The cache key to delete.
        """
        if key in self._cache:
            del self._cache[key]
    
    def clear(self):
        """
        Clear all entries from the cache.
        """
        self._cache.clear()
    
    def cleanup(self):
        """
        Remove all expired entries from the cache.
        """
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items() 
            if entry['expiry'] is not None and current_time > entry['expiry']
        ]
        
        for key in expired_keys:
            del self._cache[key]
    
    def __len__(self) -> int:
        """
        Get the number of non-expired entries in the cache.
        
        Returns:
            int: Number of entries in the cache.
        """
        self.cleanup()
        return len(self._cache)