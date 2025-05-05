import time
from typing import Any, Dict, Optional


class CacheManager:
    """
    A generic cache manager with configurable expiration strategies.
    
    Supports in-memory caching with time-based expiration.
    """
    
    def __init__(self, default_ttl: int = 300):
        """
        Initialize the cache manager.
        
        :param default_ttl: Default time-to-live in seconds, defaults to 5 minutes
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = default_ttl
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache with optional TTL.
        
        :param key: Unique identifier for the cache entry
        :param value: Value to be cached
        :param ttl: Time-to-live in seconds, uses default if not specified
        """
        expiration_time = time.time() + (ttl or self._default_ttl)
        self._cache[key] = {
            'value': value,
            'expiration': expiration_time
        }
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.
        
        :param key: Unique identifier for the cache entry
        :return: Cached value if exists and not expired, None otherwise
        """
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        
        # Check if entry is expired
        if time.time() > entry['expiration']:
            del self._cache[key]
            return None
        
        return entry['value']
    
    def delete(self, key: str) -> None:
        """
        Explicitly delete a cache entry.
        
        :param key: Unique identifier for the cache entry
        """
        if key in self._cache:
            del self._cache[key]
    
    def clear(self) -> None:
        """
        Clear all cache entries.
        """
        self._cache.clear()
    
    def get_ttl(self, key: str) -> Optional[float]:
        """
        Get remaining time-to-live for a cache entry.
        
        :param key: Unique identifier for the cache entry
        :return: Remaining TTL in seconds, or None if key doesn't exist or is expired
        """
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        remaining_ttl = entry['expiration'] - time.time()
        
        if remaining_ttl <= 0:
            del self._cache[key]
            return None
        
        return remaining_ttl