"""Custom exceptions for caching operations."""

class CacheError(Exception):
    """Base exception for cache-related errors."""
    pass

class CacheConnectionError(CacheError):
    """Raised when unable to connect to the cache storage."""
    def __init__(self, message="Failed to establish cache connection"):
        self.message = message
        super().__init__(self.message)

class CacheWriteError(CacheError):
    """Raised when unable to write to cache."""
    def __init__(self, key=None, message="Failed to write to cache"):
        self.key = key
        self.message = f"{message}: {key}" if key else message
        super().__init__(self.message)

class CacheReadError(CacheError):
    """Raised when unable to read from cache."""
    def __init__(self, key=None, message="Failed to read from cache"):
        self.key = key
        self.message = f"{message}: {key}" if key else message
        super().__init__(self.message)

class CacheSerializationError(CacheError):
    """Raised when cache serialization or deserialization fails."""
    def __init__(self, data=None, message="Failed to serialize/deserialize cache data"):
        self.data = data
        self.message = f"{message}: {data}" if data else message
        super().__init__(self.message)

class CacheExpirationError(CacheError):
    """Raised when cached data is considered invalid or expired."""
    def __init__(self, key=None, message="Cached data has expired"):
        self.key = key
        self.message = f"{message}: {key}" if key else message
        super().__init__(self.message)