import pytest
import threading
from src.dad_jokes_cache import DadJokesCache

def test_add_and_get_joke():
    """Test adding and retrieving a joke from the cache"""
    cache = DadJokesCache()
    joke_data = {"text": "Why don't scientists trust atoms?", "punchline": "Because they make up everything!"}
    
    # Add joke
    assert cache.add("joke1", joke_data) is True
    
    # Retrieve joke
    retrieved_joke = cache.get("joke1")
    assert retrieved_joke == joke_data

def test_duplicate_joke_prevention():
    """Test that duplicate jokes cannot be added"""
    cache = DadJokesCache()
    joke_data = {"text": "Test joke"}
    
    # First add should work
    assert cache.add("joke1", joke_data) is True
    
    # Second add with same ID should fail
    assert cache.add("joke1", joke_data) is False

def test_lru_cache_max_size():
    """Test LRU eviction when max size is reached"""
    cache = DadJokesCache(max_size=2)
    
    # Add two jokes
    cache.add("joke1", {"text": "Joke 1"})
    cache.add("joke2", {"text": "Joke 2"})
    
    # Third joke should push out the first
    cache.add("joke3", {"text": "Joke 3"})
    
    assert cache.get("joke1") is None  # First joke should be evicted
    assert cache.get("joke2") is not None
    assert cache.get("joke3") is not None

def test_remove_joke():
    """Test removing a joke from the cache"""
    cache = DadJokesCache()
    joke_data = {"text": "Test joke"}
    
    # Add joke
    cache.add("joke1", joke_data)
    
    # Remove joke
    assert cache.remove("joke1") is True
    assert cache.get("joke1") is None
    
    # Trying to remove non-existent joke
    assert cache.remove("joke2") is False

def test_clear_cache():
    """Test clearing all jokes from the cache"""
    cache = DadJokesCache()
    
    # Add multiple jokes
    cache.add("joke1", {"text": "Joke 1"})
    cache.add("joke2", {"text": "Joke 2"})
    
    # Clear cache
    cache.clear()
    assert cache.size() == 0

def test_cache_size():
    """Test getting the current cache size"""
    cache = DadJokesCache()
    
    cache.add("joke1", {"text": "Joke 1"})
    cache.add("joke2", {"text": "Joke 2"})
    
    assert cache.size() == 2

def test_get_all_jokes():
    """Test retrieving all jokes from the cache"""
    cache = DadJokesCache()
    joke1 = {"text": "Joke 1"}
    joke2 = {"text": "Joke 2"}
    
    cache.add("joke1", joke1)
    cache.add("joke2", joke2)
    
    all_jokes = cache.get_all_jokes()
    assert all_jokes == {"joke1": joke1, "joke2": joke2}

def test_thread_safety():
    """Test thread safety of the cache"""
    cache = DadJokesCache(max_size=100)
    
    def worker(start):
        for i in range(start, start + 50):
            joke_id = f"joke_{i}"
            cache.add(joke_id, {"text": f"Joke {i}"})
    
    # Create threads
    threads = [
        threading.Thread(target=worker, args=(0,)),
        threading.Thread(target=worker, args=(50,))
    ]
    
    # Start threads
    for t in threads:
        t.start()
    
    # Wait for threads to complete
    for t in threads:
        t.join()
    
    # Verify cache size
    assert cache.size() == 100

def test_recent_use_tracking():
    """Test that accessing a joke moves it to the end of the cache"""
    cache = DadJokesCache(max_size=2)
    
    # Add two jokes
    cache.add("joke1", {"text": "Joke 1"})
    cache.add("joke2", {"text": "Joke 2"})
    
    # Access first joke
    cache.get("joke1")
    
    # Add third joke
    cache.add("joke3", {"text": "Joke 3"})
    
    # joke2 should be evicted, not joke1
    assert cache.get("joke1") is not None
    assert cache.get("joke2") is None
    assert cache.get("joke3") is not None