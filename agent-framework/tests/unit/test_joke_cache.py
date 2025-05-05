import time
import pytest
from prometheus_swarm.utils.joke_cache import JokeCache, cached_joke_generator

def test_joke_cache_basic_functionality():
    """Test basic caching mechanism."""
    cache = JokeCache(max_size=2)
    
    # Add jokes to cache
    cache.set('joke1', 'Why did the chicken cross the road?')
    cache.set('joke2', 'What do you call a bear with no teeth?')
    
    # Verify retrieval
    assert cache.get('joke1') == 'Why did the chicken cross the road?'
    assert cache.get('joke2') == 'What do you call a bear with no teeth?'

def test_joke_cache_max_size():
    """Test that cache respects maximum size."""
    cache = JokeCache(max_size=2)
    
    cache.set('joke1', 'Joke 1')
    cache.set('joke2', 'Joke 2')
    cache.set('joke3', 'Joke 3')  # This should evict the oldest joke
    
    assert cache.get('joke1') is None
    assert cache.get('joke2') == 'Joke 2'
    assert cache.get('joke3') == 'Joke 3'

def test_joke_cache_expiration():
    """Test cache entry expiration."""
    cache = JokeCache(max_size=2, max_age=0.1)  # Very short expiration
    
    cache.set('joke1', 'Expired Joke')
    time.sleep(0.2)  # Wait for expiration
    
    assert cache.get('joke1') is None

def test_joke_cache_stats():
    """Test cache performance statistics."""
    cache = JokeCache()
    
    cache.set('joke1', 'Funny Joke')
    
    # Simulate lookups
    cache.get('joke1')  # Hit
    cache.get('joke2')  # Miss
    
    stats = cache.stats
    
    assert stats['hits'] == 1
    assert stats['misses'] == 1
    assert 0 <= stats['hit_rate'] <= 100

def test_cached_joke_generator():
    """Test the cached joke generator decorator."""
    cache = JokeCache()
    
    @cached_joke_generator(cache)
    def generate_joke(topic):
        return f"A {topic} walks into a bar..."
    
    # First call generates and caches
    joke1 = generate_joke('programmer')
    assert joke1 == "A programmer walks into a bar..."
    
    # Second call retrieves from cache
    joke2 = generate_joke('programmer')
    assert joke2 == joke1
    
    # Check stats
    assert cache.stats['hits'] == 1
    assert cache.stats['misses'] == 1

def test_joke_cache_concurrent_size():
    """Ensure cache size limit is enforced under concurrent-like scenarios."""
    cache = JokeCache(max_size=3)
    
    # Simulate filling the cache
    cache.set('joke1', 'Joke 1')
    cache.set('joke2', 'Joke 2')
    cache.set('joke3', 'Joke 3')
    cache.set('joke4', 'Joke 4')  # This should remove the oldest joke
    
    assert cache.get('joke1') is None
    assert cache.get('joke2') == 'Joke 2'
    assert cache.get('joke3') == 'Joke 3'
    assert cache.get('joke4') == 'Joke 4'