import pytest
import time
from src.dad_joke_cache import DadJokeCache

def test_dad_joke_cache_basic_functionality():
    """Test basic add and get operations"""
    cache = DadJokeCache()
    
    # Add a joke
    assert cache.add("joke1", "Why did the scarecrow win an award? Because he was outstanding in his field!")
    
    # Retrieve the joke
    assert cache.get("joke1") == "Why did the scarecrow win an award? Because he was outstanding in his field!"
    
    # Verify cache length
    assert len(cache) == 1

def test_dad_joke_cache_capacity():
    """Test cache capacity limit"""
    cache = DadJokeCache(capacity=2)
    
    # Add two jokes
    assert cache.add("joke1", "Joke 1")
    assert cache.add("joke2", "Joke 2")
    
    # Third joke should replace the first
    assert cache.add("joke3", "Joke 3")
    
    # First joke should be gone
    assert cache.get("joke1") is None
    
    # Other jokes should still be available
    assert cache.get("joke2") == "Joke 2"
    assert cache.get("joke3") == "Joke 3"

def test_dad_joke_cache_expiration():
    """Test joke expiration"""
    cache = DadJokeCache(capacity=10, max_age_seconds=1)
    
    # Add a joke
    assert cache.add("joke1", "Time-sensitive joke")
    
    # Joke should be retrievable immediately
    assert cache.get("joke1") == "Time-sensitive joke"
    
    # Wait for expiration
    time.sleep(1.1)
    
    # Joke should now be expired
    assert cache.get("joke1") is None
    assert len(cache) == 0

def test_dad_joke_cache_overwrite():
    """Test overwriting an existing joke"""
    cache = DadJokeCache()
    
    # Add initial joke
    assert cache.add("joke1", "Original Joke")
    assert cache.get("joke1") == "Original Joke"
    
    # Overwrite the joke
    assert cache.add("joke1", "Updated Joke")
    assert cache.get("joke1") == "Updated Joke"
    
    # Only one joke should be in the cache
    assert len(cache) == 1

def test_dad_joke_cache_invalid_input():
    """Test handling of invalid inputs"""
    cache = DadJokeCache()
    
    # Empty joke id or text should not be added
    assert not cache.add("", "Joke Text")
    assert not cache.add("joke1", "")
    assert len(cache) == 0

def test_dad_joke_cache_clear():
    """Test clearing the cache"""
    cache = DadJokeCache()
    
    # Add some jokes
    cache.add("joke1", "Joke 1")
    cache.add("joke2", "Joke 2")
    
    # Verify cache has items
    assert len(cache) == 2
    
    # Clear the cache
    cache.clear()
    
    # Verify cache is empty
    assert len(cache) == 0

def test_dad_joke_cache_capacity_minimum():
    """Test that cache capacity has a minimum of 1"""
    cache = DadJokeCache(capacity=0)
    
    # Verify minimum capacity is 1
    assert cache.capacity() == 1

def test_dad_joke_cache_max_age_minimum():
    """Test handling of negative max age"""
    cache = DadJokeCache(max_age_seconds=-1)
    
    # Jokes should effectively expire immediately
    cache.add("joke1", "Quick Joke")
    time.sleep(0.1)
    assert cache.get("joke1") is None