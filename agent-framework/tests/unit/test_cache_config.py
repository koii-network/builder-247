"""
Unit tests for the CachePerformanceConfig utility.
"""

import pytest
import psutil
from unittest.mock import patch
from unittest.mock import MagicMock
from prometheus_swarm.utils.cache_config import CachePerformanceConfig
import logging

def test_get_system_memory():
    """Test getting system memory."""
    config = CachePerformanceConfig()
    total_memory = config.get_system_memory()
    assert total_memory > 0
    assert total_memory == psutil.virtual_memory().total

def test_calculate_cache_limits():
    """Test cache limit calculations."""
    config = CachePerformanceConfig()
    
    # Test with explicit memory
    total_memory = 8 * 1024 * 1024 * 1024  # 8 GB
    cache_size = config.calculate_cache_limits(
        total_memory, 
        max_cache_percentage=0.3, 
        min_cache_mb=100, 
        max_cache_mb=2048
    )
    
    # 30% of 8 GB is 2.4 GB, but limited to 2048 MB
    assert cache_size == 2048 * 1024 * 1024

    # Test with very small memory
    small_memory = 512 * 1024 * 1024  # 512 MB
    cache_size = config.calculate_cache_limits(
        small_memory, 
        max_cache_percentage=0.3, 
        min_cache_mb=100, 
        max_cache_mb=2048
    )
    
    # This should be the closest integer multiple of 1024*1024 to 100 MB
    assert cache_size == 104857600  # 100 MB represented in bytes

@patch('prometheus_swarm.utils.cache_config.resource')
def test_set_memory_limit(mock_resource):
    """Test setting memory limit."""
    # Mock the setrlimit method
    def mock_set_rlimit(resource_type, limits):
        assert resource_type == mock_resource.RLIMIT_AS
        assert len(limits) == 2
    
    mock_resource.RLIMIT_AS = 9  # A mock resource type
    mock_resource.setrlimit = mock_set_rlimit
    
    config = CachePerformanceConfig()
    
    # Test with default settings
    result = config.set_memory_limit()
    assert result is True

    # Test with explicit limit
    explicit_limit = 1024 * 1024 * 1024  # 1 GB
    result = config.set_memory_limit(explicit_limit)
    assert result is True

def test_optimize_cache_performance():
    """Test cache performance optimization."""
    config = CachePerformanceConfig()
    
    # Test default optimization
    opt_config = config.optimize_cache_performance()
    assert 'max_size' in opt_config
    assert 'eviction_policy' in opt_config
    assert opt_config['eviction_policy'] == 'lru'

    # Test with explicit cache size
    explicit_size = 500 * 1024 * 1024  # 500 MB
    opt_config = config.optimize_cache_performance(
        cache_size_bytes=explicit_size, 
        eviction_policy='fifo'
    )
    
    assert opt_config['max_size'] == explicit_size
    assert opt_config['eviction_policy'] == 'fifo'

def test_logging():
    """Test logging behavior."""
    # Create a test logger
    logger = logging.getLogger('test_cache_config')
    logger.setLevel(logging.INFO)
    
    # Create a stream handler to capture log messages
    stream_handler = logging.StreamHandler()
    logger.addHandler(stream_handler)
    
    # Initialize config with the test logger
    config = CachePerformanceConfig(logger)
    
    # Capture log output
    config.optimize_cache_performance()
    
    # Check if log message is present
    log_records = [record for record in logger.handlers[0].stream.getvalue().split('\n') if record]
    assert any('Cache performance optimized' in record for record in log_records)