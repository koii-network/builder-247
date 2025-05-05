"""
Unit tests for the cache configuration module.
"""

import pytest
import time
import psutil
from unittest.mock import patch
from prometheus_swarm.utils.cache_config import CacheConfig, default_cache_config

class TestCacheConfig:
    def test_default_initialization(self):
        config = CacheConfig()
        assert config.max_memory_percent == 70.0
        assert config.max_cache_size == 1000

    def test_custom_initialization(self):
        config = CacheConfig(max_memory_percent=80.0, max_cache_size=500)
        assert config.max_memory_percent == 80.0
        assert config.max_cache_size == 500

    def test_cached_with_limit(self):
        @default_cache_config.cached_with_limit(maxsize=3)
        def test_function(x):
            return x * 2

        # Test caching behavior
        assert test_function(2) == 4
        assert test_function(2) == 4  # Cached result
        assert test_function(3) == 6
        assert test_function(4) == 8

    @patch('psutil.virtual_memory')
    def test_memory_limit_decorator_exceeds_limit(self, mock_memory):
        # Simulate memory usage exceeding limit
        mock_memory.return_value.percent = 80.0

        config = CacheConfig(max_memory_percent=70.0)

        @config.memory_limit_decorator
        def test_function():
            return "function called"

        with pytest.raises(MemoryError, match="Memory usage too high"):
            test_function()

    @patch('psutil.virtual_memory')
    def test_memory_limit_decorator_within_limit(self, mock_memory):
        # Simulate memory usage within limit
        mock_memory.return_value.percent = 50.0

        config = CacheConfig(max_memory_percent=70.0)

        @config.memory_limit_decorator
        def test_function(x):
            return x * 2

        assert test_function(5) == 10

    def test_cached_with_limit_size_restriction(self):
        @default_cache_config.cached_with_limit(maxsize=2)
        def test_function(x):
            return x * 2

        # Fill the cache
        test_function(1)
        test_function(2)
        test_function(3)  # This should replace the oldest entry

        # Verify cache behavior
        with pytest.raises(TypeError):
            test_function(1)  # First cached entry should be evicted
        assert test_function(2) == 4  # Second entry still cached
        assert test_function(3) == 6  # Third entry is cached