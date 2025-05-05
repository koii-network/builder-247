import time
import pytest
from src.cache_expiration import ExpiringCache


def test_set_and_get_cache_entry():
    """Test setting and getting a cache entry"""
    cache = ExpiringCache()
    cache.set('key1', 'value1')
    assert cache.get('key1') == 'value1'


def test_cache_entry_expiration():
    """Test that cache entries expire after their TTL"""
    cache = ExpiringCache(default_ttl=1)
    cache.set('key1', 'value1')
    assert cache.get('key1') == 'value1'
    
    # Wait for entry to expire
    time.sleep(2)
    assert cache.get('key1') is None


def test_custom_ttl():
    """Test setting a custom TTL for a cache entry"""
    cache = ExpiringCache(default_ttl=10)
    cache.set('key1', 'value1', ttl=1)
    assert cache.get('key1') == 'value1'
    
    # Wait for entry to expire
    time.sleep(2)
    assert cache.get('key1') is None


def test_delete_cache_entry():
    """Test deleting a specific cache entry"""
    cache = ExpiringCache()
    cache.set('key1', 'value1')
    cache.set('key2', 'value2')
    
    cache.delete('key1')
    assert cache.get('key1') is None
    assert cache.get('key2') == 'value2'


def test_clear_cache():
    """Test clearing all entries from the cache"""
    cache = ExpiringCache()
    cache.set('key1', 'value1')
    cache.set('key2', 'value2')
    
    cache.clear()
    assert cache.get('key1') is None
    assert cache.get('key2') is None


def test_get_all_valid_keys():
    """Test retrieving all valid keys in the cache"""
    cache = ExpiringCache()
    
    # Set specific keys with varying TTLs
    cache.set('key1', 'value1', ttl=3)
    cache.set('key2', 'value2', ttl=1)
    cache.set('key3', 'value3', ttl=5)
    
    # First check: all keys should be valid
    assert set(cache.get_all_valid_keys()) == {'key1', 'key2', 'key3'}
    
    # Wait just over 1 second to expire key2
    time.sleep(1.1)
    
    # Second check: key2 should be removed
    assert set(cache.get_all_valid_keys()) == {'key1', 'key3'}
    
    # Wait to expire more keys
    time.sleep(2)
    
    # Final check: only key3 should remain
    assert cache.get_all_valid_keys() == ['key3']