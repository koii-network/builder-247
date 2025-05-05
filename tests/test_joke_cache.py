import pytest
import time
from src.joke_cache import JokeCache, generate_random_joke

def test_joke_cache_initialization():
    """Test JokeCache initialization."""
    cache = JokeCache()
    assert cache.get_cache_stats()['total_jokes'] == 0
    assert cache.get_cache_stats()['max_cache_size'] == 100

def test_joke_cache_add_and_retrieve():
    """Test adding and retrieving jokes from the cache."""
    cache = JokeCache()
    
    # Add multiple jokes
    jokes = [
        ('programming', "Why do programmers prefer dark mode? Because light attracts bugs!"),
        ('dad', "I told my wife she was drawing her eyebrows too high. She looked surprised."),
    ]
    
    for joke_type, joke in jokes:
        cache.add_joke(joke_type, joke)
    
    assert cache.get_cache_stats()['total_jokes'] == 2
    
    # Retrieve jokes
    retrieved_joke = cache.get_joke()
    assert retrieved_joke in [joke for _, joke in jokes]
    
    programming_joke = cache.get_joke('programming')
    assert programming_joke == "Why do programmers prefer dark mode? Because light attracts bugs!"

def test_joke_cache_max_size():
    """Test that the cache respects the maximum size."""
    cache = JokeCache(max_cache_size=3)
    
    # Add 4 jokes to trigger eviction
    for i in range(4):
        cache.add_joke('test', f"Test Joke {i}")
    
    assert cache.get_cache_stats()['total_jokes'] == 3

def test_joke_cache_expiration():
    """Test that jokes expire after the cache duration."""
    import time
    
    cache = JokeCache(max_cache_size=10, cache_duration=1)
    cache.add_joke('test', "Expiring Joke")
    
    # Wait for 2 seconds to ensure expiration
    time.sleep(2)
    
    assert cache.get_joke() is None

def test_random_joke_generation():
    """Test random joke generation function."""
    # Test generating jokes of different types
    programming_joke = generate_random_joke('programming')
    dad_joke = generate_random_joke('dad')
    generic_joke = generate_random_joke()
    
    assert programming_joke in [
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "Why do Java developers wear glasses? Because they can't C#.",
        "There are 10 types of people in the world: Those who understand binary, and those who don't."
    ]
    assert dad_joke in [
        "I told my wife she was drawing her eyebrows too high. She looked surprised.",
        "Why don't scientists trust atoms? Because they make up everything!",
        "I'm afraid for the calendar. Its days are numbered."
    ]
    assert generic_joke in [
        "A joke is a very serious thing.",
        "Laughter is the best medicine, but if you're laughing for no reason, you need medicine.",
        "Comedy is subjective."
    ]