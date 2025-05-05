"""Test suite for cache manager."""

import time
import pytest

from prometheus_swarm.utils.cache_manager import CacheManager
from prometheus_swarm.utils.cache_errors import (
    CacheWriteError,
    CacheReadError,
    CacheSerializationError,
    CacheExpirationError
)

def test_cache_set_and_get():
    """Test basic cache set and get operations."""
    cache = CacheManager()
    
    # Simple set and get
    cache.set('test_key', 'test_value')
    assert cache.get('test_key') == 'test_value'

def test_cache_expiration():
    """Test cache entry expiration."""
    cache = CacheManager(default_expiry=1)
    
    cache.set('temporary', 'value')
    assert cache.get('temporary') == 'value'
    
    # Wait for expiration
    time.sleep(2)
    
    with pytest.raises(CacheExpirationError):
        cache.get('temporary')

def test_cache_delete():
    """Test cache deletion."""
    cache = CacheManager()
    
    cache.set('delete_me', 'value')
    assert cache.get('delete_me') == 'value'
    
    cache.delete('delete_me')
    
    with pytest.raises(CacheReadError):
        cache.get('delete_me')

def test_invalid_key():
    """Test behavior with invalid keys."""
    cache = CacheManager()
    
    with pytest.raises(CacheWriteError):
        cache.set('', 'value')

def test_unserialized_data():
    """Test handling of unserialized data."""
    cache = CacheManager()
    
    # Complex object that can't be easily serialized
    with pytest.raises(CacheSerializationError):
        cache.set('complex', object())

def test_cache_clear():
    """Test clearing entire cache."""
    cache = CacheManager()
    
    cache.set('key1', 'value1')
    cache.set('key2', 'value2')
    
    cache.clear()
    
    with pytest.raises(CacheReadError):
        cache.get('key1')
    
    with pytest.raises(CacheReadError):
        cache.get('key2')