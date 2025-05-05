import time
import pytest

from prometheus_swarm.utils.cache_expiration import CacheManager


def test_cache_set_and_get():
    """Test basic cache set and get functionality."""
    cache = CacheManager()
    cache.set('test_key', 'test_value')
    assert cache.get('test_key') == 'test_value'


def test_cache_expiration():
    """Test that cache entries expire after TTL."""
    cache = CacheManager(default_ttl=1)
    cache.set('test_key', 'test_value')
    time.sleep(1.1)  # Wait slightly longer than TTL
    assert cache.get('test_key') is None


def test_custom_ttl():
    """Test custom TTL for specific entries."""
    cache = CacheManager(default_ttl=10)
    cache.set('short_key', 'short_value', ttl=1)
    cache.set('long_key', 'long_value', ttl=5)
    
    time.sleep(1.1)
    assert cache.get('short_key') is None
    assert cache.get('long_key') == 'long_value'


def test_get_ttl():
    """Test retrieving remaining TTL."""
    cache = CacheManager(default_ttl=3)
    cache.set('test_key', 'test_value')
    ttl = cache.get_ttl('test_key')
    
    assert ttl is not None
    assert 2.5 <= ttl <= 3.0
    
    time.sleep(2)
    assert 0.5 <= cache.get_ttl('test_key') <= 1.0
    
    time.sleep(2)
    assert cache.get_ttl('test_key') is None


def test_delete_entry():
    """Test explicit deletion of cache entries."""
    cache = CacheManager()
    cache.set('key1', 'value1')
    cache.set('key2', 'value2')
    
    cache.delete('key1')
    assert cache.get('key1') is None
    assert cache.get('key2') == 'value2'


def test_clear_cache():
    """Test clearing entire cache."""
    cache = CacheManager()
    cache.set('key1', 'value1')
    cache.set('key2', 'value2')
    
    cache.clear()
    assert cache.get('key1') is None
    assert cache.get('key2') is None


def test_non_existent_key():
    """Test behavior with non-existent keys."""
    cache = CacheManager()
    assert cache.get('non_existent') is None
    assert cache.get_ttl('non_existent') is None