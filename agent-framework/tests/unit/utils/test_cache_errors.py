"""
Unit tests for the cache error handling module.
"""

import pytest
from prometheus_swarm.utils.cache_errors import (
    CacheError,
    CacheInitializationError,
    CacheAccessError,
    CacheWriteError,
    CacheReadError,
    CacheEvictionError,
    handle_cache_error
)

def test_cache_error_hierarchy():
    """Verify the error hierarchy and inheritance."""
    assert issubclass(CacheInitializationError, CacheError)
    assert issubclass(CacheAccessError, CacheError)
    assert issubclass(CacheWriteError, CacheError)
    assert issubclass(CacheReadError, CacheError)
    assert issubclass(CacheEvictionError, CacheError)

def test_handle_cache_error_with_message():
    """Test handle_cache_error with a custom message."""
    with pytest.raises(CacheInitializationError) as exc_info:
        handle_cache_error(CacheInitializationError, "Cache setup failed")
    
    assert str(exc_info.value) == "Cache setup failed"

def test_handle_cache_error_with_original_error():
    """Test handle_cache_error with an original error."""
    original_error = ValueError("Invalid cache configuration")
    
    with pytest.raises(CacheAccessError) as exc_info:
        handle_cache_error(CacheAccessError, original_error=original_error)
    
    assert str(exc_info.value) == "Invalid cache configuration"

def test_handle_cache_error_without_message():
    """Test handle_cache_error without a message."""
    with pytest.raises(CacheEvictionError):
        handle_cache_error(CacheEvictionError)

def test_cache_error_types():
    """Verify that different cache error types can be raised."""
    with pytest.raises(CacheInitializationError):
        raise CacheInitializationError("Cache could not be initialized")
    
    with pytest.raises(CacheWriteError):
        raise CacheWriteError("Failed to write to cache")
    
    with pytest.raises(CacheReadError):
        raise CacheReadError("Failed to read from cache")