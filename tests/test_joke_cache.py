import time
import pytest
from src.joke_cache import JokeCache

def test_joke_cache_initialization():
    """Test that the JokeCache can be initialized with default parameters."""
    cache = JokeCache()
    assert cache.get_cache_size() == 0

def test_add_and_retrieve_joke():
    """Test adding and retrieving a joke from the cache."""
    cache = JokeCache()
    joke_data = {"text": "Why did the chicken cross the road?", "category": "classic"}
    joke_id = "chicken_joke"
    
    assert cache.add_joke(joke_id, joke_data) is True
    retrieved_joke = cache.get_joke(joke_id)
    
    assert retrieved_joke == joke_data
    assert cache.get_cache_size() == 1

def test_joke_cache_max_size():
    """Test that the cache respects the maximum size limit."""
    cache = JokeCache(max_size=2)
    
    joke1 = {"text": "Joke 1", "category": "test"}
    joke2 = {"text": "Joke 2", "category": "test"}
    joke3 = {"text": "Joke 3", "category": "test"}
    
    assert cache.add_joke("joke1", joke1) is True
    assert cache.add_joke("joke2", joke2) is True
    assert cache.add_joke("joke3", joke3) is False

def test_joke_cache_expiration():
    """Test that jokes expire after the specified time."""
    cache = JokeCache(expiration_time=0.1)  # 0.1 seconds for testing
    
    joke_data = {"text": "Expired joke", "category": "temporary"}
    joke_id = "temp_joke"
    
    assert cache.add_joke(joke_id, joke_data) is True
    
    # Wait for joke to expire
    time.sleep(0.2)
    
    assert cache.get_joke(joke_id) is None
    assert cache.get_cache_size() == 0

def test_clear_cache():
    """Test clearing the entire cache."""
    cache = JokeCache()
    
    joke_data = {"text": "Clearable joke", "category": "test"}
    cache.add_joke("joke1", joke_data)
    cache.add_joke("joke2", joke_data)
    
    assert cache.get_cache_size() == 2
    cache.clear()
    assert cache.get_cache_size() == 0

def test_cache_multiple_jokes():
    """Test adding and retrieving multiple jokes."""
    cache = JokeCache()
    
    jokes = {
        "joke1": {"text": "Joke 1", "category": "test1"},
        "joke2": {"text": "Joke 2", "category": "test2"},
        "joke3": {"text": "Joke 3", "category": "test3"}
    }
    
    for joke_id, joke_data in jokes.items():
        cache.add_joke(joke_id, joke_data)
    
    assert cache.get_cache_size() == 3
    
    for joke_id, joke_data in jokes.items():
        assert cache.get_joke(joke_id) == joke_data