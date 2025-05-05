import functools
import time
import logging
from typing import Any, Callable, Dict, Optional
from functools import wraps

logger = logging.getLogger(__name__)

class CacheError(Exception):
    """Base exception for caching-related errors."""
    pass

class CacheTimeoutError(CacheError):
    """Raised when cache retrieval or storage times out."""
    pass

class CacheStorageError(CacheError):
    """Raised when there's an issue with cache storage."""
    pass

class CacheRetrievalError(CacheError):
    """Raised when there's an issue retrieving from cache."""
    pass

def cache_with_error_handling(
    max_age: int = 300,  # 5 minutes default cache time
    max_size: int = 100,  # Maximum number of items in cache
    timeout: float = 1.0,  # Timeout for cache operations
    ignore_errors: bool = False  # Whether to suppress cache-related errors
) -> Callable:
    """
    A decorator for caching function results with comprehensive error handling.
    
    Args:
        max_age (int): Maximum time (in seconds) to keep a cache entry
        max_size (int): Maximum number of entries in the cache
        timeout (float): Maximum time allowed for cache operations
        ignore_errors (bool): Whether to suppress cache-related errors
    
    Returns:
        Decorated function with caching and error handling
    """
    def decorator(func: Callable) -> Callable:
        cache: Dict[Any, Dict[str, Any]] = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a key based on function args and kwargs
            key = str(args) + str(kwargs)

            try:
                # Check cache with timeout
                start_time = time.time()
                
                # Check cache entry existence and validity
                if key in cache:
                    entry = cache[key]
                    if time.time() - entry['timestamp'] < max_age:
                        return entry['value']
                    
                    # Remove expired entries
                    del cache[key]

                # Enforce max cache size
                if len(cache) >= max_size:
                    # Remove oldest entry
                    oldest_key = min(cache, key=lambda k: cache[k]['timestamp'])
                    del cache[oldest_key]

                # Execute function with timeout
                if time.time() - start_time > timeout:
                    raise CacheTimeoutError("Cache operation timed out")

                result = func(*args, **kwargs)

                # Store result in cache
                cache[key] = {
                    'value': result,
                    'timestamp': time.time()
                }

                return result

            except Exception as e:
                if ignore_errors:
                    logger.warning(f"Cache error (ignored): {e}")
                    return func(*args, **kwargs)
                
                if isinstance(e, CacheError):
                    raise
                
                raise CacheStorageError(f"Error in caching: {e}") from e

        # Expose cache management methods
        def clear_cache():
            """Clear the entire cache."""
            cache.clear()
        
        def get_cache_stats():
            """Get current cache statistics."""
            return {
                'size': len(cache),
                'max_size': max_size,
                'entries': list(cache.keys())
            }

        wrapper.clear_cache = clear_cache
        wrapper.get_cache_stats = get_cache_stats
        return wrapper

    return decorator