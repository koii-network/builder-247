import time
import pytest
from src.joke_cache import JokeCache

def test_joke_cache_basic_functionality():
    """Test basic caching mechanism"""
    cache = JokeCache(max_size=2)
    
    def fetch_joke1():
        return "Why did the chicken cross the road?"
    
    def fetch_joke2():
        return "What do you call a bear with no teeth?"
    
    # First fetch should be a miss
    joke1 = cache.get('joke1', fetch_joke1)
    stats = cache.get_stats()
    assert stats['misses'] == 1
    assert stats['hits'] == 0
    assert joke1 == "Why did the chicken cross the road?"
    
    # Second fetch of same key should be a hit
    joke1_cached = cache.get('joke1', fetch_joke1)
    stats = cache.get_stats()
    assert stats['misses'] == 1
    assert stats['hits'] == 1
    assert joke1_cached == joke1

def test_joke_cache_max_size():
    """Test cache size limit"""
    cache = JokeCache(max_size=2)
    
    # Add more jokes than max size
    cache.get('joke1', lambda: "Joke 1")
    cache.get('joke2', lambda: "Joke 2")
    cache.get('joke3', lambda: "Joke 3")
    
    # First joke should be evicted
    stats = cache.get_stats()
    assert stats['misses'] == 3

def test_joke_cache_time_to_live():
    """Test time-to-live functionality"""
    cache = JokeCache(ttl=0.1)  # Very short TTL
    
    joke = cache.get('joke1', lambda: "A time-sensitive joke")
    
    # Wait beyond TTL
    time.sleep(0.2)
    
    # This should trigger a miss and fresh fetch
    cache.get('joke1', lambda: "A new joke")
    stats = cache.get_stats()
    assert stats['misses'] == 2

def test_joke_cache_statistics():
    """Test cache performance statistics"""
    cache = JokeCache()
    
    cache.get('joke1', lambda: "Joke 1")
    cache.get('joke1', lambda: "Joke 1")  # Hit
    cache.get('joke2', lambda: "Joke 2")
    
    stats = cache.get_stats()
    assert stats['hits'] == 1
    assert stats['misses'] == 2
    assert 0 <= stats['hit_rate'] <= 1
    assert stats['avg_access_time'] >= 0

def test_joke_cache_clear():
    """Test cache clearing"""
    cache = JokeCache()
    
    cache.get('joke1', lambda: "Joke 1")
    cache.get('joke2', lambda: "Joke 2")
    
    stats_before = cache.get_stats()
    assert stats_before['misses'] == 2
    
    cache.clear()
    
    stats_after = cache.get_stats()
    assert stats_after['hits'] == 0
    assert stats_after['misses'] == 0