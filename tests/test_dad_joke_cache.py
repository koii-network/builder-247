import pytest
from src.dad_joke_cache import DadJokeCache

def test_initial_cache_creation():
    """Test creating a cache with default and custom capacity."""
    default_cache = DadJokeCache()
    assert default_cache.get_capacity() == 100
    assert default_cache.get_current_size() == 0

    custom_cache = DadJokeCache(max_capacity=50)
    assert custom_cache.get_capacity() == 50
    assert custom_cache.get_current_size() == 0

def test_invalid_cache_capacity():
    """Test that creating a cache with invalid capacity raises an error."""
    with pytest.raises(ValueError, match="Cache capacity must be at least 1"):
        DadJokeCache(max_capacity=0)
    
    with pytest.raises(ValueError, match="Cache capacity must be at least 1"):
        DadJokeCache(max_capacity=-10)

def test_add_and_get_joke():
    """Test adding and retrieving jokes from the cache."""
    cache = DadJokeCache(max_capacity=3)
    
    # Add jokes
    cache.add("joke1", "Why did the scarecrow win an award? Because he was outstanding in his field!")
    cache.add("joke2", "I'm afraid for the calendar. Its days are numbered.")
    
    # Retrieve jokes
    assert cache.get("joke1") == "Why did the scarecrow win an award? Because he was outstanding in his field!"
    assert cache.get("joke2") == "I'm afraid for the calendar. Its days are numbered."
    assert cache.get_current_size() == 2
    
    # Verify contains method
    assert cache.contains("joke1") is True
    assert cache.contains("joke3") is False

def test_lru_eviction():
    """Test that least recently used items are evicted when cache is full."""
    cache = DadJokeCache(max_capacity=3)
    
    # Fill the cache
    cache.add("joke1", "Joke 1")
    cache.add("joke2", "Joke 2")
    cache.add("joke3", "Joke 3")
    
    # Accessing joke1 moves it to most recently used
    cache.get("joke1")
    
    # Add a fourth joke, which should remove joke2 (least recently used)
    cache.add("joke4", "Joke 4")
    
    assert cache.contains("joke1") is True
    assert cache.contains("joke3") is True
    assert cache.contains("joke4") is True
    assert cache.contains("joke2") is False

def test_add_existing_joke():
    """Test adding a joke that already exists in the cache."""
    cache = DadJokeCache(max_capacity=3)
    
    cache.add("joke1", "First version")
    assert cache.get("joke1") == "First version"
    
    # Updating an existing joke moves it to most recently used
    cache.add("joke1", "Updated version")
    assert cache.get("joke1") == "Updated version"
    
    # Verify only one entry exists
    assert cache.get_current_size() == 1

def test_remove_joke():
    """Test removing jokes from the cache."""
    cache = DadJokeCache(max_capacity=3)
    
    cache.add("joke1", "Joke 1")
    cache.add("joke2", "Joke 2")
    
    # Remove existing joke
    assert cache.remove("joke1") is True
    assert cache.contains("joke1") is False
    assert cache.get_current_size() == 1
    
    # Remove non-existing joke
    assert cache.remove("joke3") is False

def test_clear_cache():
    """Test clearing the entire cache."""
    cache = DadJokeCache(max_capacity=3)
    
    cache.add("joke1", "Joke 1")
    cache.add("joke2", "Joke 2")
    assert cache.get_current_size() == 2
    
    cache.clear()
    assert cache.get_current_size() == 0

def test_add_invalid_joke():
    """Test that adding jokes with empty ID or text raises an error."""
    cache = DadJokeCache()
    
    with pytest.raises(ValueError, match="Joke ID and text must not be empty"):
        cache.add("", "A joke")
    
    with pytest.raises(ValueError, match="Joke ID and text must not be empty"):
        cache.add("joke1", "")