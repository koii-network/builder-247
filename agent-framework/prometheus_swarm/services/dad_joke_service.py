import random
import requests
from typing import Dict, Optional, List

class DadJokeService:
    """
    A service for fetching and managing dad jokes.
    
    This service provides functionality to retrieve dad jokes from an external API,
    with support for random selection and caching.
    """
    
    def __init__(self, cache_size: int = 50):
        """
        Initialize the Dad Joke Service.
        
        :param cache_size: Maximum number of jokes to cache, defaults to 50
        """
        self._api_url = "https://icanhazdadjoke.com/"
        self._headers = {
            "Accept": "application/json",
            "User-Agent": "Prometheus Swarm Dad Joke Service"
        }
        self._joke_cache: List[str] = []
        self._cache_size = cache_size
    
    def get_random_joke(self) -> Optional[str]:
        """
        Fetch a random dad joke.
        
        :return: A random dad joke as a string, or None if unable to fetch
        """
        try:
            response = requests.get(self._api_url, headers=self._headers)
            response.raise_for_status()
            joke_data = response.json()
            joke = joke_data.get('joke')
            
            if joke:
                # Add to cache, respecting cache size
                if len(self._joke_cache) >= self._cache_size:
                    self._joke_cache.pop(0)
                self._joke_cache.append(joke)
                return joke
            return None
        
        except requests.RequestException:
            return None
    
    def get_cached_jokes(self) -> List[str]:
        """
        Retrieve the current list of cached jokes.
        
        :return: A list of cached jokes
        """
        return self._joke_cache.copy()
    
    def clear_cache(self) -> None:
        """
        Clear the joke cache.
        """
        self._joke_cache.clear()