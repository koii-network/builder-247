"""Unit tests for the comprehensive caching utility."""

import os
import tempfile
import time
import pytest
from prometheus_swarm.utils.cache import (
    CacheBackend, 
    ThreadSafeCache, 
    cacheable, 
    CacheError, 
    CacheConfigurationError, 
    CacheOperationError
)

@pytest.fixture
def temp_cache_dir():
    """Create a temporary cache directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

def test_cache_backend_initialization(temp_cache_dir):
    """Test cache backend initialization."""
    backend = CacheBackend(cache_dir=temp_cache_dir)
    assert os.path.exists(temp_cache_dir)
    assert backend.cache_dir == temp_cache_dir

def test_cache_backend_get_set(temp_cache_dir):
    """Test basic get and set operations."""
    backend = CacheBackend(cache_dir=temp_cache_dir)
    
    # Set and retrieve simple value
    backend.set('test_key', {'data': 42})
    result = backend.get('test_key')
    assert result == {'data': 42}

def test_cache_backend_expiration(temp_cache_dir):
    """Test cache expiration."""
    backend = CacheBackend(cache_dir=temp_cache_dir)
    
    # Set value and simulate aging
    backend.set('expiring_key', 'test_value')
    
    # Should be retrievable initially
    assert backend.get('expiring_key') == 'test_value'
    
    # Test with max_age
    assert backend.get('expiring_key', max_age=0) is None

def test_cache_backend_delete(temp_cache_dir):
    """Test cache deletion."""
    backend = CacheBackend(cache_dir=temp_cache_dir)
    
    backend.set('delete_key', 'some_value')
    assert backend.get('delete_key') == 'some_value'
    
    backend.delete('delete_key')
    assert backend.get('delete_key') is None

def test_thread_safe_cache(temp_cache_dir):
    """Test thread-safe cache operations."""
    backend = CacheBackend(cache_dir=temp_cache_dir)
    safe_cache = ThreadSafeCache(backend)
    
    safe_cache.set('thread_key', 'thread_value')
    assert safe_cache.get('thread_key') == 'thread_value'

def test_cacheable_decorator():
    """Test the cacheable decorator."""
    @cacheable(max_age=60)
    def expensive_computation(x):
        """Simulate an expensive function."""
        return x * 2
    
    # First call should compute
    result1 = expensive_computation(5)
    assert result1 == 10
    
    # Subsequent calls retrieve cached value
    result2 = expensive_computation(5)
    assert result2 == 10

def test_invalid_cache_dir():
    """Test handling of invalid cache directory."""
    with pytest.raises(CacheConfigurationError):
        CacheBackend('/nonexistent/impossible/path')

def test_cache_key_sanitization(temp_cache_dir):
    """Test that cache keys are properly sanitized."""
    backend = CacheBackend(cache_dir=temp_cache_dir)
    
    # Test various key formats
    test_keys = [
        'normal_key',
        'key-with-hyphens',
        'key with spaces',
        'key!@#$%^&*()',
        '123numeric_key'
    ]
    
    for key in test_keys:
        backend.set(key, f'value_for_{key}')
        assert backend.get(key) == f'value_for_{key}'