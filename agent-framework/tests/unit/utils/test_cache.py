import time
import pytest
from prometheus_swarm.utils.cache import ExpiringCache

def test_cache_basic_set_get():
    """Test basic set and get functionality."""
    cache = ExpiringCache()
    cache.set('key1', 'value1')
    assert cache.get('key1') == 'value1'

def test_cache_with_ttl():
    """Test cache with specific time-to-live."""
    cache = ExpiringCache()
    cache.set('key1', 'value1', ttl=0.1)
    assert cache.get('key1') == 'value1'
    
    time.sleep(0.2)
    assert cache.get('key1') is None

def test_cache_default_ttl():
    """Test cache with default time-to-live."""
    cache = ExpiringCache(default_ttl=0.1)
    cache.set('key1', 'value1')
    assert cache.get('key1') == 'value1'
    
    time.sleep(0.2)
    assert cache.get('key1') is None

def test_cache_delete():
    """Test deleting a specific key."""
    cache = ExpiringCache()
    cache.set('key1', 'value1')
    cache.set('key2', 'value2')
    
    cache.delete('key1')
    assert cache.get('key1') is None
    assert cache.get('key2') == 'value2'

def test_cache_clear():
    """Test clearing the entire cache."""
    cache = ExpiringCache()
    cache.set('key1', 'value1')
    cache.set('key2', 'value2')
    
    cache.clear()
    assert cache.get('key1') is None
    assert cache.get('key2') is None

def test_cache_cleanup():
    """Test manual cleanup of expired entries."""
    cache = ExpiringCache()
    cache.set('key1', 'value1', ttl=0.1)
    cache.set('key2', 'value2', ttl=1.0)
    
    time.sleep(0.2)
    cache.cleanup()
    
    assert len(cache) == 1
    assert cache.get('key1') is None
    assert cache.get('key2') == 'value2'

def test_cache_length():
    """Test length of the cache."""
    cache = ExpiringCache()
    cache.set('key1', 'value1', ttl=0.1)
    cache.set('key2', 'value2')
    
    assert len(cache) == 2
    time.sleep(0.2)
    assert len(cache) == 1