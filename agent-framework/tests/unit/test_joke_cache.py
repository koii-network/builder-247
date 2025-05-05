import time
import pytest
from prometheus_swarm.utils.joke_cache import JokeCache

def test_joke_cache_basic_functionality():
    """Test basic caching and retrieval of jokes."""
    cache = JokeCache()
    
    # Add a joke
    cache.add('joke1', 'Why did the chicken cross the road?')
    
    # Retrieve the joke
    assert cache.get('joke1') == 'Why did the chicken cross the road?'
    
    # Verify length
    assert len(cache) == 1

def test_joke_cache_max_size():
    """Test that cache respects maximum size limit."""
    cache = JokeCache(max_size=2)
    
    # Add first two jokes
    cache.add('joke1', 'Joke 1')
    cache.add('joke2', 'Joke 2')
    
    # Add third joke, which should remove the oldest
    cache.add('joke3', 'Joke 3')
    
    # Verify oldest joke is removed
    assert cache.get('joke1') is None
    assert cache.get('joke2') is not None
    assert cache.get('joke3') is not None

def test_joke_cache_expiration():
    """Test that jokes expire after the specified time."""
    cache = JokeCache(expiration=0.5)  # Very short expiration for testing
    
    # Add a joke
    cache.add('joke1', 'Expiring joke')
    
    # Verify joke exists immediately
    assert cache.get('joke1') == 'Expiring joke'
    
    # Wait for expiration
    time.sleep(0.6)
    
    # Verify joke is now None
    assert cache.get('joke1') is None

def test_joke_cache_clear():
    """Test clearing the entire cache."""
    cache = JokeCache()
    
    # Add some jokes
    cache.add('joke1', 'Joke 1')
    cache.add('joke2', 'Joke 2')
    
    # Clear the cache
    cache.clear()
    
    # Verify cache is empty
    assert len(cache) == 0
    assert cache.get('joke1') is None
    assert cache.get('joke2') is None

def test_joke_cache_overwrite():
    """Test overwriting an existing joke in the cache."""
    cache = JokeCache()
    
    # Add an initial joke
    cache.add('joke1', 'Original joke')
    
    # Overwrite the joke
    cache.add('joke1', 'Updated joke')
    
    # Verify the joke is updated
    assert cache.get('joke1') == 'Updated joke'
    assert len(cache) == 1

def test_joke_cache_performance():
    """Basic performance test for cache operations."""
    cache = JokeCache(max_size=1000)
    
    # Add many jokes
    for i in range(1000):
        cache.add(f'joke{i}', f'Joke number {i}')
    
    # Verify last added joke
    assert cache.get('joke999') == 'Joke number 999'
    assert len(cache) == 1000
    
    # Verify retrieval performance
    assert cache.get('joke500') == 'Joke number 500'