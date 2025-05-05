"""
Unit tests for the caching error handling module.
"""

import pytest
from unittest.mock import Mock, patch
from prometheus_swarm.utils.caching import (
    safe_cache_set, 
    safe_cache_get, 
    handle_cache_errors,
    CacheInvalidArgumentError,
    CacheSetError,
    CacheGetError
)

class MockCache:
    def __init__(self):
        self._storage = {}

    def set(self, key, value, timeout=None):
        self._storage[key] = value

    def get(self, key):
        return self._storage.get(key)

def test_safe_cache_set():
    mock_cache = MockCache()

    # Test successful cache set
    assert safe_cache_set(mock_cache, "test_key", "test_value") is True
    assert mock_cache.get("test_key") == "test_value"

    # Test with timeout
    assert safe_cache_set(mock_cache, "timeout_key", "timeout_value", timeout=10) is True
    assert mock_cache.get("timeout_key") == "timeout_value"

def test_safe_cache_set_invalid_arguments():
    mock_cache = MockCache()

    # Test invalid key
    with pytest.raises(CacheInvalidArgumentError):
        safe_cache_set(mock_cache, "", "value")
    
    with pytest.raises(CacheInvalidArgumentError):
        safe_cache_set(mock_cache, None, "value")

    # Test None value
    with pytest.raises(CacheInvalidArgumentError):
        safe_cache_set(mock_cache, "key", None)

    # Test invalid timeout
    with pytest.raises(CacheInvalidArgumentError):
        safe_cache_set(mock_cache, "key", "value", timeout=-1)

def test_safe_cache_get():
    mock_cache = MockCache()
    
    # Populate cache
    mock_cache.set("existing_key", "existing_value")

    # Test retrieving existing key
    assert safe_cache_get(mock_cache, "existing_key") == "existing_value"

    # Test retrieving non-existing key with default
    assert safe_cache_get(mock_cache, "nonexistent_key", default="default_value") == "default_value"

def test_safe_cache_get_invalid_arguments():
    mock_cache = MockCache()

    # Test invalid key
    with pytest.raises(CacheInvalidArgumentError):
        safe_cache_get(mock_cache, "")

    with pytest.raises(CacheInvalidArgumentError):
        safe_cache_get(mock_cache, None)

@handle_cache_errors
def mock_cache_method(cache, *args, **kwargs):
    if len(args) == 0:
        raise TypeError("No arguments")
    return cache.set(*args, **kwargs)

def test_handle_cache_errors_decorator():
    mock_cache = MockCache()

    # Test successful case
    assert mock_cache_method(mock_cache, "key", "value") is None

    # Test with no arguments
    with pytest.raises(CacheInvalidArgumentError):
        mock_cache_method(mock_cache)

    # Simulating a cache error
    with patch.object(MockCache, 'set', side_effect=ValueError("Invalid value")):
        with pytest.raises(CacheSetError):
            mock_cache_method(mock_cache, "key", "value")