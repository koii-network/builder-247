import time
import pytest
from src.joke_cache import JokeCache

def test_basic_caching():
    """Test basic caching functionality"""
    joke_cache = JokeCache()
    
    @joke_cache.cache
    def get_joke(category):
        return f"A {category} joke"
    
    # First call - should be a cache miss
    first_joke = get_joke("programmer")
    metrics = joke_cache.get_performance_metrics()
    assert metrics['cache_misses'] == 1
    assert metrics['cache_hits'] == 0
    
    # Second call - should be a cache hit
    second_joke = get_joke("programmer")
    metrics = joke_cache.get_performance_metrics()
    assert metrics['cache_misses'] == 1
    assert metrics['cache_hits'] == 1
    assert first_joke == second_joke

def test_cache_size_limit():
    """Test that cache respects maximum size"""
    joke_cache = JokeCache(max_size=2)
    
    @joke_cache.cache
    def get_joke(category):
        return f"A {category} joke"
    
    # Add more entries than max_size
    get_joke("programmer")
    get_joke("dad")
    get_joke("science")
    
    # Verify cache size
    assert len(joke_cache._cache) == 2
    assert "science" in str(joke_cache._cache.keys())
    assert "dad" in str(joke_cache._cache.keys())

def test_cache_ttl():
    """Test time-based cache expiration"""
    joke_cache = JokeCache(default_ttl=0.1)  # 100ms TTL
    
    @joke_cache.cache
    def get_joke(category):
        return f"A {category} joke"
    
    # First call - cache miss
    first_joke = get_joke("programmer")
    
    # Second call - cache hit
    second_joke = get_joke("programmer")
    
    # Wait for TTL to expire
    time.sleep(0.2)
    
    # Third call - should be a cache miss again
    third_joke = get_joke("programmer")
    
    metrics = joke_cache.get_performance_metrics()
    assert metrics['cache_misses'] == 2
    assert metrics['cache_hits'] == 1

def test_performance_metrics():
    """Test performance metrics calculation"""
    joke_cache = JokeCache()
    
    @joke_cache.cache
    def get_joke(category):
        return f"A {category} joke"
    
    # Multiple calls to generate metrics
    get_joke("programmer")
    get_joke("programmer")
    get_joke("dad")
    
    metrics = joke_cache.get_performance_metrics()
    
    assert metrics['cache_hits'] == 1
    assert metrics['cache_misses'] == 2
    assert 0 <= metrics['hit_rate'] <= 1
    assert metrics['avg_lookup_time'] >= 0

def test_cache_clear():
    """Test cache clearing functionality"""
    joke_cache = JokeCache()
    
    @joke_cache.cache
    def get_joke(category):
        return f"A {category} joke"
    
    get_joke("programmer")
    get_joke("dad")
    
    metrics_before = joke_cache.get_performance_metrics()
    assert metrics_before['cache_hits'] == 1
    
    joke_cache.clear_cache()
    
    metrics_after = joke_cache.get_performance_metrics()
    assert metrics_after['cache_hits'] == 0
    assert metrics_after['cache_misses'] == 0
    assert len(joke_cache._cache) == 0