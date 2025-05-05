import time
import pytest
from prometheus_swarm.utils.caching import (
    cache_with_error_handling, 
    CacheError, 
    CacheTimeoutError, 
    CacheStorageError
)

def test_basic_caching():
    @cache_with_error_handling()
    def expensive_function(x):
        time.sleep(0.1)  # Simulate expensive computation
        return x * 2

    # First call should compute
    result1 = expensive_function(5)
    assert result1 == 10

    # Second call should return cached result
    start_time = time.time()
    result2 = expensive_function(5)
    assert result2 == 10
    assert time.time() - start_time < 0.01  # Should be much faster

def test_cache_max_size():
    @cache_with_error_handling(max_size=2)
    def square(x):
        return x * x

    square(1)
    square(2)
    square(3)  # This should push out the first entry

    cache_stats = square.get_cache_stats()
    assert cache_stats['size'] == 2
    assert cache_stats['max_size'] == 2

def test_cache_expiration():
    @cache_with_error_handling(max_age=0.1)
    def slow_function(x):
        return x * 2

    result1 = slow_function(5)
    assert result1 == 10

    time.sleep(0.2)  # Wait for cache to expire

    result2 = slow_function(5)
    assert result2 == 10  # Should recompute

def test_cache_error_handling():
    def error_prone_function(x):
        if x == 0:
            raise ValueError("Cannot process zero")
        return x * 2

    # Without ignoring errors
    with pytest.raises(CacheStorageError):
        @cache_with_error_handling()
        def decorated_func(x):
            return error_prone_function(x)
        
        decorated_func(0)

    # With ignored errors
    @cache_with_error_handling(ignore_errors=True)
    def safe_func(x):
        return error_prone_function(x)

    with pytest.raises(ValueError):
        safe_func(0)

def test_cache_management():
    @cache_with_error_handling()
    def mult(x):
        return x * 2

    mult(5)
    mult(6)

    stats = mult.get_cache_stats()
    assert stats['size'] == 2

    mult.clear_cache()
    stats = mult.get_cache_stats()
    assert stats['size'] == 0

def test_timeout_handling():
    def slow_function(x):
        time.sleep(2)  # Deliberately slow
        return x * 2

    with pytest.raises(CacheTimeoutError):
        @cache_with_error_handling(timeout=0.1)
        def decorated_func(x):
            return slow_function(x)
        
        decorated_func(5)