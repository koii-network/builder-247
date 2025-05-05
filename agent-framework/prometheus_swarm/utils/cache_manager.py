"""Provides a centralized cache management utility."""

import json
import time
from typing import Any, Optional

from .cache_errors import (
    CacheConnectionError,
    CacheReadError,
    CacheSerializationError,
    CacheWriteError,
    CacheExpirationError
)

class CacheManager:
    """Manages caching operations with robust error handling."""

    def __init__(self, cache_backend=None, default_expiry=3600):
        """
        Initialize the cache manager.

        Args:
            cache_backend: Optional cache storage backend (default: in-memory dict)
            default_expiry: Default cache expiration time in seconds
        """
        self._cache = cache_backend or {}
        self._default_expiry = default_expiry

    def set(
        self, 
        key: str, 
        value: Any, 
        expiry: Optional[int] = None
    ) -> None:
        """
        Store a value in the cache with optional expiration.

        Args:
            key: Unique cache key
            value: Value to be cached
            expiry: Optional expiration time in seconds

        Raises:
            CacheConnectionError: If cache is unavailable
            CacheWriteError: If writing to cache fails
            CacheSerializationError: If serialization fails
        """
        try:
            # Validate input
            if not key:
                raise ValueError("Cache key must not be empty")

            # Serialize value
            try:
                serialized_value = json.dumps(value)
            except TypeError as e:
                raise CacheSerializationError(value) from e

            # Store with metadata
            self._cache[key] = {
                'value': serialized_value,
                'timestamp': time.time(),
                'expiry': expiry or self._default_expiry
            }
        except Exception as e:
            if isinstance(e, (CacheSerializationError, ValueError)):
                raise
            raise CacheWriteError(key) from e

    def get(self, key: str) -> Any:
        """
        Retrieve a value from the cache.

        Args:
            key: Unique cache key

        Returns:
            Cached value if valid

        Raises:
            CacheReadError: If reading from cache fails
            CacheExpirationError: If cached data has expired
        """
        try:
            # Check if key exists
            if key not in self._cache:
                raise CacheReadError(key)

            # Get cache entry
            entry = self._cache[key]
            current_time = time.time()

            # Check expiration
            if current_time - entry['timestamp'] > entry['expiry']:
                del self._cache[key]  # Remove expired entry
                raise CacheExpirationError(key)

            # Deserialize and return
            try:
                return json.loads(entry['value'])
            except json.JSONDecodeError as e:
                raise CacheSerializationError() from e

        except Exception as e:
            if isinstance(e, (CacheReadError, CacheExpirationError, CacheSerializationError)):
                raise
            raise CacheReadError(key) from e

    def delete(self, key: str) -> None:
        """
        Remove an entry from the cache.

        Args:
            key: Unique cache key
        """
        try:
            del self._cache[key]
        except KeyError:
            pass  # Ignore if key doesn't exist

    def clear(self) -> None:
        """Clear entire cache."""
        self._cache.clear()