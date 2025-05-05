import pytest
import time
from prometheus_swarm.utils.cache_config import CacheConfig, global_cache_config

def test_cache_config_initialization():
    """Test initialization of CacheConfig."""
    cache_config = CacheConfig(max_cache_size=10, max_memory_percent=0.7)
    
    stats = cache_config.get_cache_stats()
    assert stats['max_cache_size'] == 10
    assert stats['max_memory_percent'] == 0.7

def test_memory_limit_decorator():
    """Test the memory limit decorator for caching."""
    cache_config = CacheConfig(max_cache_size=2)
    
    @cache_config.memory_limit_decorator
    def expensive_computation(x):
        time.sleep(0.1)  # Simulate expensive computation
        return x * 2
    
    # First call - computes and caches
    result1 = expensive_computation(5)
    assert result1 == 10
    
    # Second call - retrieves from cache
    result2 = expensive_computation(5)
    assert result2 == 10
    
    # Check cache stats
    stats = cache_config.get_cache_stats()
    assert stats['cache_size'] == 1

def test_cache_size_limit():
    """Test cache size limitation."""
    cache_config = CacheConfig(max_cache_size=2)
    
    @cache_config.memory_limit_decorator
    def compute(x):
        return x * 2
    
    # Fill cache
    compute(1)
    compute(2)
    compute(3)  # This should remove the first cached item
    
    stats = cache_config.get_cache_stats()
    assert stats['cache_size'] == 2

def test_global_cache_config():
    """Test the global cache configuration."""
    assert isinstance(global_cache_config, CacheConfig)
    
    @global_cache_config.memory_limit_decorator
    def test_func(x):
        return x * 2
    
    result = test_func(7)
    assert result == 14
    
    stats = global_cache_config.get_cache_stats()
    assert stats['cache_size'] > 0

def test_cache_with_different_arguments():
    """Test caching with different function arguments."""
    cache_config = CacheConfig()
    
    @cache_config.memory_limit_decorator
    def multiply(x, y):
        return x * y
    
    result1 = multiply(2, 3)
    result2 = multiply(2, 3)
    result3 = multiply(3, 2)
    
    # Verify caching behavior
    assert result1 == 6
    assert result2 == 6
    assert result3 == 6
    
    stats = cache_config.get_cache_stats()
    assert stats['cache_size'] == 2  # Two unique argument combinations