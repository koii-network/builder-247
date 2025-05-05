import functools
import random
from typing import List, Dict, Any, Optional

class JokeCache:
    """
    A caching system for joke retrieval with configurable cache settings.
    """
    def __init__(self, max_cache_size: int = 100, cache_duration: int = 3600):
        """
        Initialize the JokeCache.

        :param max_cache_size: Maximum number of jokes to store in cache
        :param cache_duration: Time in seconds for which a cached joke remains valid
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._max_cache_size = max_cache_size
        self._cache_duration = cache_duration

    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """
        Check if a cache entry is still valid.

        :param cache_entry: The cache entry to validate
        :return: True if the cache entry is valid, False otherwise
        """
        import time
        current_time = time.time()
        return current_time - cache_entry.get('timestamp', 0) < self._cache_duration

    def add_joke(self, joke_type: str, joke_data: str) -> None:
        """
        Add a joke to the cache.

        :param joke_type: Category or type of joke
        :param joke_data: The joke content
        """
        import time
        
        # Evict oldest entries if cache is full
        if len(self._cache) >= self._max_cache_size:
            oldest_key = min(self._cache, key=lambda k: self._cache[k]['timestamp'])
            del self._cache[oldest_key]
        
        # Add new joke to cache
        self._cache[joke_data] = {
            'type': joke_type,
            'timestamp': time.time()
        }

    def get_joke(self, joke_type: Optional[str] = None) -> Optional[str]:
        """
        Retrieve a joke from the cache, optionally filtered by type.

        :param joke_type: Optional type of joke to retrieve
        :return: A joke from the cache, or None if no valid jokes are found
        """
        valid_jokes = [
            joke for joke, entry in self._cache.items()
            if self._is_cache_valid(entry) and (joke_type is None or entry['type'] == joke_type)
        ]
        
        return random.choice(valid_jokes) if valid_jokes else None

    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get statistics about the current cache.

        :return: A dictionary with cache statistics
        """
        return {
            'total_jokes': len(self._cache),
            'max_cache_size': self._max_cache_size
        }

def generate_random_joke(joke_type: Optional[str] = None) -> str:
    """
    Generate a random joke (mock implementation).

    :param joke_type: Optional type of joke to generate
    :return: A random joke string
    """
    joke_types = {
        'programming': [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Why do Java developers wear glasses? Because they can't C#.",
            "There are 10 types of people in the world: Those who understand binary, and those who don't."
        ],
        'dad': [
            "I told my wife she was drawing her eyebrows too high. She looked surprised.",
            "Why don't scientists trust atoms? Because they make up everything!",
            "I'm afraid for the calendar. Its days are numbered."
        ],
        None: [
            "A joke is a very serious thing.",
            "Laughter is the best medicine, but if you're laughing for no reason, you need medicine.",
            "Comedy is subjective."
        ]
    }
    
    selected_type = joke_type if joke_type in joke_types else None
    return random.choice(joke_types[selected_type])