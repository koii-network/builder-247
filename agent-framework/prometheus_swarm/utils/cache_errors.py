"""
Comprehensive Caching Error Handling Module

This module provides custom exceptions and error handling mechanisms
for caching operations in the Prometheus Swarm framework.
"""

class CacheError(Exception):
    """Base exception for all caching-related errors."""
    pass

class CacheInitializationError(CacheError):
    """Raised when cache initialization fails."""
    pass

class CacheAccessError(CacheError):
    """Raised when accessing the cache encounters an issue."""
    pass

class CacheWriteError(CacheError):
    """Raised when writing to the cache fails."""
    pass

class CacheReadError(CacheError):
    """Raised when reading from the cache fails."""
    pass

class CacheEvictionError(CacheError):
    """Raised when cache eviction/clearing fails."""
    pass

def handle_cache_error(error_type, message=None, original_error=None):
    """
    Centralized error handling for cache operations.

    Args:
        error_type (type): The specific cache error type to raise
        message (str, optional): Custom error message
        original_error (Exception, optional): Original underlying error

    Raises:
        The specified cache error type
    """
    if not message and original_error:
        message = str(original_error)
    
    raise error_type(message) if message else error_type()