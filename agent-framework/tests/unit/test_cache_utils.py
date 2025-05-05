"""
Test suite for comprehensive caching error handling.
"""

import time
import pytest
from prometheus_swarm.utils.cache_utils import (
    CacheManager, 
    CacheFullError, 
    CacheError, 
    cached
)

def test_cache_basic_functionality():
    """Test basic cache set and get operations."""
    cache = CacheManager(max_size=10)
    
    cache.set('key1', 'value1')
    assert cache.get('key1') == 'value1'

def test_cache_expiration():
    """Test cache entry expiration."""
    cache = CacheManager(default_ttl=1)
    
    cache.set('key2', 'value2')
    time.sleep(2)  # Wait for expiration
    assert cache.get('key2') is None

def test_cache_max_size():
    """Test cache reaches maximum size."""
    cache = CacheManager(max_size=2)
    
    cache.set('key1', 'value1')
    cache.set('key2', 'value2')
    
    with pytest.raises(CacheFullError):
        cache.set('key3', 'value3')

def test_cache_clear():
    """Test cache clearing."""
    cache = CacheManager()
    
    cache.set('key1', 'value1')
    cache.set('key2', 'value2')
    
    cache.clear()
    assert cache.get('key1') is None
    assert cache.get('key2') is None

def test_cached_decorator():
    """Test the cached decorator functionality."""
    cache_manager = CacheManager()
    
    call_count = 0
    
    @cached(cache_manager=cache_manager, ttl=5)
    def expensive_function(x):
        nonlocal call_count
        call_count += 1
        return x * 2
    
    # First call should compute and cache
    result1 = expensive_function(5)
    assert result1 == 10
    assert call_count == 1
    
    # Second call should retrieve from cache
    result2 = expensive_function(5)
    assert result2 == 10
    assert call_count == 1  # Call count should remain 1

def test_cached_decorator_different_args():
    """Test cached decorator with different arguments."""
    cache_manager = CacheManager()
    
    call_count = 0
    
    @cached(cache_manager=cache_manager, ttl=5)
    def expensive_function(x):
        nonlocal call_count
        call_count += 1
        return x * 2
    
    result1 = expensive_function(5)
    result2 = expensive_function(6)
    
    assert result1 == 10
    assert result2 == 12
    assert call_count == 2  # Different args should cause different calls

def test_custom_ttl():
    """Test setting custom TTL per cache entry."""
    cache = CacheManager(default_ttl=10)
    
    cache.set('quick_expire', 'fast', ttl=1)
    cache.set('slow_expire', 'slow', ttl=5)
    
    time.sleep(2)
    
    assert cache.get('quick_expire') is None
    assert cache.get('slow_expire') is not None