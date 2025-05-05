import time
import pytest
from prometheus_swarm.utils.joke_cache import JokeCache

def test_joke_cache_decorator():
    joke_cache = JokeCache(max_size=5)
    
    @joke_cache.cached_joke
    def get_joke(category):
        """Simulated joke generation function"""
        time.sleep(0.01)  # Simulate processing time
        return f"Joke about {category}"
    
    # First call (miss)
    first_joke = get_joke("programming")
    assert first_joke == "Joke about programming"
    
    # Second call (hit)
    cached_joke = get_joke("programming")
    assert cached_joke == "Joke about programming"
    
    # Check performance stats
    stats = joke_cache.get_performance_stats()
    assert stats['total_misses'] == 1
    assert stats['total_hits'] == 1
    assert 0 <= stats['hit_rate'] <= 1
    assert stats['total_lookup_time'] > 0

def test_joke_cache_max_size():
    joke_cache = JokeCache(max_size=3)
    
    @joke_cache.cached_joke
    def get_joke(category):
        return f"Joke about {category}"
    
    # Fill cache
    get_joke("cat1")
    get_joke("cat2")
    get_joke("cat3")
    get_joke("cat4")  # This will evict the oldest cache entry
    
    # Verify stats
    stats = joke_cache.get_performance_stats()
    assert stats['total_misses'] == 4
    assert stats['total_hits'] == 0

def test_joke_cache_reset_stats():
    joke_cache = JokeCache()
    
    @joke_cache.cached_joke
    def get_joke(category):
        return f"Joke about {category}"
    
    get_joke("tech")
    get_joke("tech")  # Hit
    
    stats = joke_cache.get_performance_stats()
    assert stats['total_misses'] == 1
    assert stats['total_hits'] == 1
    
    joke_cache.reset_stats()
    reset_stats = joke_cache.get_performance_stats()
    assert reset_stats['total_misses'] == 0
    assert reset_stats['total_hits'] == 0
    assert reset_stats['total_lookup_time'] == 0