import pytest
import time
from src.dad_joke_cache import DadJokeCache

def test_add_and_get_joke():
    """Test adding and retrieving a joke."""
    cache = DadJokeCache()
    joke = "Why did the scarecrow win an award? Because he was outstanding in his field!"
    joke_id = cache.add_joke(joke)
    
    assert cache.get_joke(joke_id) == joke
    assert cache.get_cache_size() == 1

def test_joke_expiration():
    """Test that jokes expire after set time."""
    cache = DadJokeCache(default_expiration=1)
    joke = "Why don't scientists trust atoms? Because they make up everything!"
    joke_id = cache.add_joke(joke)
    
    # Wait for joke to expire
    time.sleep(2)
    
    assert cache.get_joke(joke_id) is None
    assert cache.get_cache_size() == 0

def test_custom_expiration():
    """Test adding a joke with custom expiration."""
    cache = DadJokeCache(default_expiration=10)
    joke = "I told my wife she was drawing her eyebrows too high. She looked surprised."
    joke_id = cache.add_joke(joke, expiration=2)
    
    # Wait for joke to expire
    time.sleep(3)
    
    assert cache.get_joke(joke_id) is None

def test_remove_joke():
    """Test removing a specific joke."""
    cache = DadJokeCache()
    joke = "Why do bees have sticky hair? Because they use honeycombs!"
    joke_id = cache.add_joke(joke)
    
    assert cache.remove_joke(joke_id) is True
    assert cache.get_joke(joke_id) is None
    assert cache.get_cache_size() == 0

def test_clear_expired():
    """Test clearing expired jokes."""
    cache = DadJokeCache(default_expiration=1)
    joke1 = "What do you call a fake noodle? An impasta!"
    joke2 = "Why did the math book look so sad? Because it had too many problems."
    
    joke_id1 = cache.add_joke(joke1)
    joke_id2 = cache.add_joke(joke2)
    
    # Wait for jokes to expire
    time.sleep(2)
    
    cleared_count = cache.clear_expired()
    assert cleared_count == 2
    assert cache.get_cache_size() == 0

def test_max_size_limit():
    """Test that cache respects max size limit."""
    cache = DadJokeCache(max_size=2)
    
    joke1 = "I'm afraid for the calendar. Its days are numbered."
    joke2 = "I used to be a baker, but I didn't make enough dough."
    joke3 = "Why did the coffee file a police report? Because it got mugged!"
    
    cache.add_joke(joke1)
    cache.add_joke(joke2)
    
    with pytest.raises(ValueError, match="Cache is full"):
        cache.add_joke(joke3)

def test_non_existent_joke():
    """Test retrieving a non-existent joke."""
    cache = DadJokeCache()
    assert cache.get_joke("non_existent_id") is None

def test_multiple_add_get_remove():
    """Test multiple operations on cache."""
    cache = DadJokeCache(max_size=10, default_expiration=5)
    
    jokes = [
        "Why don't eggs tell jokes? They'd crack each other up!",
        "I ordered a chicken and an egg from Amazon. I'll let you know.",
        "What do you call a boomerang that doesn't come back? A stick."
    ]
    
    joke_ids = [cache.add_joke(joke) for joke in jokes]
    
    # Retrieve and verify jokes
    for joke_id, joke in zip(joke_ids, jokes):
        assert cache.get_joke(joke_id) == joke
    
    # Remove a joke
    cache.remove_joke(joke_ids[1])
    assert cache.get_joke(joke_ids[1]) is None
    assert cache.get_cache_size() == 2