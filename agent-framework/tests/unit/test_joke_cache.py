import time
import pytest
from prometheus_swarm.utils.joke_cache import JokeCache

def test_joke_cache_basic_functionality():
    """Test basic caching behavior."""
    cache = JokeCache(max_age=3600, max_size=10)
    
    # Mock joke retrieval function
    @cache.cached
    def get_joke(category):
        return f"Joke about {category}"
    
    # First call should compute
    result1 = get_joke("programming")
    assert result1 == "Joke about programming"
    
    # Subsequent calls should return cached result
    result2 = get_joke("programming")
    assert result2 == "Joke about programming"

def test_joke_cache_expiration():
    """Test cache entry expiration."""
    cache = JokeCache(max_age=1, max_size=10)
    
    @cache.cached
    def get_joke(category):
        return f"Joke about {category}"
    
    # First call
    result1 = get_joke("programming")
    assert result1 == "Joke about programming"
    
    # Wait for cache to expire
    time.sleep(2)
    
    # Next call should recompute
    result2 = get_joke("programming")
    assert result2 == "Joke about programming"

def test_joke_cache_max_size():
    """Test cache size limitation."""
    cache = JokeCache(max_age=3600, max_size=3)
    
    @cache.cached
    def get_joke(category):
        return f"Joke about {category}"
    
    # Fill cache beyond max size
    for i in range(5):
        get_joke(f"category_{i}")
    
    # Only the last 3 entries should remain
    assert len(cache._cache) == 3
    cached_keys = list(cache._cache.keys())
    assert all("category_" in str(key) and str(2) <= str(key)[-1] for key in cached_keys)

def test_cache_with_different_arguments():
    """Test caching with different function arguments."""
    cache = JokeCache(max_age=3600, max_size=10)
    
    @cache.cached
    def get_joke(category, length):
        return f"Joke about {category} of length {length}"
    
    result1 = get_joke("programming", 10)
    result2 = get_joke("programming", 10)
    result3 = get_joke("programming", 20)
    
    assert result1 == result2  # Same args, should be cached
    assert result1 != result3  # Different length, should be different