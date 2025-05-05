"""
Comprehensive Caching Error Handling Module

This module provides robust error handling and management for caching operations.
"""

import functools
import logging
from typing import Any, Callable, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')

class CacheError(Exception):
    """Base exception for caching-related errors."""
    pass

class CacheSetError(CacheError):
    """Raised when setting a cache value fails."""
    pass

class CacheGetError(CacheError):
    """Raised when retrieving a cache value fails."""
    pass

class CacheInvalidArgumentError(CacheError):
    """Raised when invalid arguments are provided to cache operations."""
    pass

def handle_cache_errors(func: Callable[..., T]) -> Callable[..., Optional[T]]:
    """
    Decorator to provide comprehensive error handling for caching methods.

    Args:
        func (Callable): The cache method to be wrapped.

    Returns:
        Callable: A wrapped function with error handling.

    Raises:
        CacheInvalidArgumentError: If invalid arguments are provided.
        CacheSetError: If setting a cache value fails.
        CacheGetError: If retrieving a cache value fails.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Validate arguments
            if args is None or len(args) == 0:
                raise CacheInvalidArgumentError("No arguments provided")

            return func(*args, **kwargs)

        except TypeError as e:
            logger.error(f"Invalid cache argument: {e}")
            raise CacheInvalidArgumentError(f"Invalid cache argument: {e}") from e
        except ValueError as e:
            logger.error(f"Invalid cache value: {e}")
            raise CacheSetError(f"Invalid cache value: {e}") from e
        except Exception as e:
            error_type = "setting" if func.__name__.startswith(("set", "update")) else "retrieving"
            logger.error(f"Error {error_type} cache: {e}")
            
            if error_type == "setting":
                raise CacheSetError(f"Failed to set cache: {e}") from e
            else:
                raise CacheGetError(f"Failed to retrieve cache: {e}") from e

    return wrapper

def safe_cache_set(cache, key: str, value: Any, timeout: Optional[int] = None) -> bool:
    """
    Safely set a value in the cache with comprehensive error handling.

    Args:
        cache: The cache object to use.
        key (str): The cache key.
        value (Any): The value to cache.
        timeout (Optional[int]): Optional expiration time.

    Returns:
        bool: True if cache set successfully, False otherwise.

    Raises:
        CacheInvalidArgumentError: For invalid input arguments.
        CacheSetError: If setting the cache fails.
    """
    try:
        if not key or not isinstance(key, str):
            raise CacheInvalidArgumentError("Invalid cache key")

        if value is None:
            raise CacheInvalidArgumentError("Cannot cache None value")

        if timeout is not None and (not isinstance(timeout, int) or timeout < 0):
            raise CacheInvalidArgumentError("Invalid timeout value")

        # Perform cache set with timeout
        if timeout is not None:
            cache.set(key, value, timeout=timeout)
        else:
            cache.set(key, value)

        return True

    except Exception as e:
        logger.error(f"Failed to set cache for key {key}: {e}")
        raise CacheSetError(f"Cache set failed for key {key}: {e}") from e

def safe_cache_get(cache, key: str, default: Optional[Any] = None) -> Optional[Any]:
    """
    Safely retrieve a value from the cache with comprehensive error handling.

    Args:
        cache: The cache object to use.
        key (str): The cache key.
        default (Optional[Any]): Default value if key not found.

    Returns:
        Optional[Any]: The cached value or default.

    Raises:
        CacheInvalidArgumentError: For invalid input arguments.
        CacheGetError: If retrieving the cache fails.
    """
    try:
        if not key or not isinstance(key, str):
            raise CacheInvalidArgumentError("Invalid cache key")

        value = cache.get(key)
        return value if value is not None else default

    except Exception as e:
        logger.error(f"Failed to get cache for key {key}: {e}")
        raise CacheGetError(f"Cache get failed for key {key}: {e}") from e