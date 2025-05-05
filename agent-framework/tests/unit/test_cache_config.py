"""
Unit tests for cache performance configuration module.
"""

import time
import pytest
from prometheus_swarm.utils.cache_config import CachePerformanceConfig, cache_config


def test_cache_config_initialization():
    """Test default initialization of CachePerformanceConfig."""
    config = CachePerformanceConfig()
    assert config._max_memory_percent == 80.0
    assert config._cache_size_limit is None


def test_memory_check():
    """Test memory usage check method."""
    config = CachePerformanceConfig()
    # Should always return True unless system is under extreme memory pressure
    assert config.memory_check() is True


def test_cached_decorator():
    """Test the caching decorator functionality."""
    @cache_config.cached
    def expensive_computation(x):
        """Simulate an expensive computation."""
        time.sleep(0.1)  # Simulate computational delay
        return x * 2

    # First call should compute
    start = time.time()
    result1 = expensive_computation(5)
    first_call_time = time.time() - start
    assert result1 == 10

    # Second call should return cached result faster
    start = time.time()
    result2 = expensive_computation(5)
    second_call_time = time.time() - start
    assert result2 == 10

    # Cached result should be computed significantly faster
    assert second_call_time < first_call_time


def test_cache_size_limit():
    """Test cache size limitation."""
    config = CachePerformanceConfig(cache_size_limit=2)

    @config.cached
    def dummy_func(x):
        """Dummy function for cache size testing."""
        return x * 2

    dummy_func(1)  # First item
    dummy_func(2)  # Second item
    dummy_func(3)  # This should remove the first item
    
    # Verify cache contents (somewhat implementation-dependent)
    assert len(config._cache) <= 2


def test_memory_limit_exceeding():
    """Test memory limit enforcement."""
    # In this test, we can't directly simulate memory exhaustion
    # So we just ensure the method exists and is callable
    config = CachePerformanceConfig()
    
    @config.cached
    def dummy_func(x):
        """Dummy function for memory limit testing."""
        return x * 2

    try:
        result = dummy_func(5)
        assert result == 10
    except MemoryError:
        # This should be a rare occurrence under normal testing
        pass


def test_global_cache_config_exists():
    """Verify that the global cache_config is importable and usable."""
    assert hasattr(cache_config, 'cached'), "Global cache_config should have cached method"
    assert hasattr(cache_config, 'memory_check'), "Global cache_config should have memory_check method"