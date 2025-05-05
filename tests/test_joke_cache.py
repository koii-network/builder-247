import time
import pytest
from src.joke_cache import JokeCache

def test_basic_caching():
    """Test basic caching functionality"""
    cache = JokeCache(max_size=2)
    
    def fetch_joke(key):
        return f"Joke for {key}"
    
    # First fetch should be a miss
    joke1 = cache.get("key1", fetch_joke)
    metrics1 = cache.get_performance_metrics()
    
    assert joke1 == "Joke for key1"
    assert metrics1['total_misses'] == 1
    assert metrics1['total_hits'] == 0
    
    # Second fetch of same key should be a hit
    joke2 = cache.get("key1", fetch_joke)
    metrics2 = cache.get_performance_metrics()
    
    assert joke2 == "Joke for key1"
    assert metrics2['total_misses'] == 1
    assert metrics2['total_hits'] == 1

def test_cache_size_limit():
    """Test that cache respects maximum size limit"""
    cache = JokeCache(max_size=2)
    
    def fetch_joke(key):
        return f"Joke for {key}"
    
    # Add two jokes
    cache.get("key1", fetch_joke)
    cache.get("key2", fetch_joke)
    
    # Add third joke should remove the oldest
    cache.get("key3", fetch_joke)
    
    metrics = cache.get_performance_metrics()
    assert metrics['current_cache_size'] == 2
    assert metrics['max_cache_size'] == 2

def test_cache_clear():
    """Test clearing the cache"""
    cache = JokeCache(max_size=2)
    
    def fetch_joke(key):
        return f"Joke for {key}"
    
    # Add jokes and get metrics
    cache.get("key1", fetch_joke)
    cache.get("key2", fetch_joke)
    
    initial_metrics = cache.get_performance_metrics()
    assert initial_metrics['total_misses'] == 2
    
    # Clear cache
    cache.clear()
    
    cleared_metrics = cache.get_performance_metrics()
    assert cleared_metrics['total_misses'] == 0
    assert cleared_metrics['total_hits'] == 0
    assert cleared_metrics['current_cache_size'] == 0

def test_performance_metrics():
    """Test performance metrics calculation"""
    cache = JokeCache(max_size=3)
    
    def fetch_joke(key):
        time.sleep(0.01)  # Simulate slow joke fetching
        return f"Joke for {key}"
    
    # Fetch jokes to generate metrics
    cache.get("key1", fetch_joke)
    cache.get("key1", fetch_joke)  # Hit
    cache.get("key2", fetch_joke)
    cache.get("key3", fetch_joke)
    
    metrics = cache.get_performance_metrics()
    
    assert metrics['total_misses'] == 3
    assert metrics['total_hits'] == 1
    assert 0 <= metrics['cache_hit_ratio'] <= 1
    assert metrics['avg_retrieval_time'] > 0

def test_edge_cases():
    """Test edge cases for joke caching"""
    cache = JokeCache(max_size=1)
    
    def fetch_joke(key):
        if key == "error_key":
            raise ValueError("Invalid joke key")
        return f"Joke for {key}"
    
    # Normal fetch
    joke = cache.get("normal_key", fetch_joke)
    assert joke == "Joke for normal_key"
    
    # Fetch with error in fetch function
    with pytest.raises(ValueError):
        cache.get("error_key", fetch_joke)