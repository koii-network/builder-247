import pytest
import threading
import time
from src.dad_jokes_cache import DadJokesCache

def test_add_and_get_joke():
    """Test adding and retrieving a joke from the cache"""
    cache = DadJokesCache()
    joke_data = {"text": "Why don't scientists trust atoms?", "punchline": "Because they make up everything!", "timestamp": time.time()}
    
    # Add joke
    assert cache.add("joke1", joke_data) is True
    
    # Retrieve joke
    retrieved_joke = cache.get("joke1")
    assert retrieved_joke == joke_data

def test_duplicate_joke_prevention():
    """Test that duplicate jokes cannot be added"""
    cache = DadJokesCache()
    joke_data = {"text": "Test joke", "timestamp": time.time()}
    
    # First add should work
    assert cache.add("joke1", joke_data) is True
    
    # Second add with same ID should fail
    assert cache.add("joke1", joke_data) is False

def test_lru_cache_max_size():
    """Test LRU eviction when max size is reached"""
    cache = DadJokesCache(max_size=2)
    
    # Add two jokes
    cache.add("joke1", {"text": "Joke 1", "timestamp": time.time()})
    cache.add("joke2", {"text": "Joke 2", "timestamp": time.time()})
    
    # Third joke should push out the first
    cache.add("joke3", {"text": "Joke 3", "timestamp": time.time()})
    
    assert cache.get("joke1") is None  # First joke should be evicted
    assert cache.get("joke2") is not None
    assert cache.get("joke3") is not None

def test_remove_joke():
    """Test removing a joke from the cache"""
    cache = DadJokesCache()
    joke_data = {"text": "Test joke", "timestamp": time.time()}
    
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
    cache.add("joke1", {"text": "Joke 1", "timestamp": time.time()})
    cache.add("joke2", {"text": "Joke 2", "timestamp": time.time()})
    
    # Clear cache
    cache.clear()
    assert cache.size() == 0

def test_cache_size():
    """Test getting the current cache size"""
    cache = DadJokesCache()
    
    cache.add("joke1", {"text": "Joke 1", "timestamp": time.time()})
    cache.add("joke2", {"text": "Joke 2", "timestamp": time.time()})
    
    assert cache.size() == 2

def test_joke_exists():
    """Test checking if a joke exists"""
    cache = DadJokesCache()
    joke_data = {"text": "Exists joke", "timestamp": time.time()}
    
    cache.add("joke1", joke_data)
    assert cache.exists("joke1") is True
    assert cache.exists("joke2") is False

def test_joke_expiration():
    """Test joke expiration"""
    cache = DadJokesCache(joke_expiry=1)  # 1 second expiry
    
    # Add a joke
    cache.add("joke1", {"text": "Expiring joke", "timestamp": time.time()})
    
    # Wait for expiration
    time.sleep(1.1)
    
    # Joke should be considered expired
    assert cache.exists("joke1") is False
    assert cache.get("joke1") is None

def test_multiple_jokes_beyond_50():
    """Test adding more than 50 unique jokes"""
    cache = DadJokesCache(max_size=100)
    
    # Add more than 50 unique jokes
    for i in range(60):
        cache.add(f"joke_{i}", {"text": f"Joke {i}", "timestamp": time.time()})
    
    assert cache.size() == 60

def test_thread_safety():
    """Test thread safety of the cache"""
    cache = DadJokesCache(max_size=100)
    
    def worker(start):
        for i in range(start, start + 50):
            joke_id = f"joke_{i}"
            cache.add(joke_id, {"text": f"Joke {i}", "timestamp": time.time()})
    
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
    cache.add("joke1", {"text": "Joke 1", "timestamp": time.time()})
    cache.add("joke2", {"text": "Joke 2", "timestamp": time.time()})
    
    # Access first joke
    cache.get("joke1")
    
    # Add third joke
    cache.add("joke3", {"text": "Joke 3", "timestamp": time.time()})
    
    # joke2 should be evicted, not joke1
    assert cache.get("joke1") is not None
    assert cache.get("joke2") is None
    assert cache.get("joke3") is not None