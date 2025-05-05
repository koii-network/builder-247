"""
Dad Joke Command Handler Interface Module

This module provides an interface for interacting with dad jokes,
including fetching, filtering, and managing dad jokes.
"""

import random
import requests
from typing import Dict, List, Optional

class DadJokeCommandHandler:
    """
    A command handler for retrieving and managing dad jokes.
    
    Supports fetching random jokes, filtering by category, 
    and basic joke management.
    """
    
    def __init__(self, api_url: str = "https://icanhazdadjoke.com/"):
        """
        Initialize the Dad Joke Command Handler.
        
        Args:
            api_url (str, optional): The base URL for dad joke API. 
                Defaults to the icanhazdadjoke.com API.
        """
        self.api_url = api_url
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "OrcaFrameworkDadJokeClient/1.0"
        }
        self._joke_cache: List[str] = []
    
    def fetch_random_joke(self) -> Optional[str]:
        """
        Fetch a random dad joke from the API.
        
        Returns:
            Optional[str]: A random dad joke, or None if fetching fails.
        """
        try:
            response = requests.get(self.api_url, headers=self.headers)
            response.raise_for_status()
            joke_data = response.json()
            return joke_data.get('joke')
        except requests.RequestException:
            return None
    
    def fetch_multiple_jokes(self, count: int = 5) -> List[str]:
        """
        Fetch multiple random dad jokes.
        
        Args:
            count (int, optional): Number of jokes to fetch. Defaults to 5.
        
        Returns:
            List[str]: A list of dad jokes.
        """
        jokes = []
        for _ in range(count):
            joke = self.fetch_random_joke()
            if joke:
                jokes.append(joke)
        return jokes
    
    def filter_jokes_by_word(self, jokes: List[str], keyword: str) -> List[str]:
        """
        Filter jokes that contain a specific keyword.
        
        Args:
            jokes (List[str]): List of jokes to filter.
            keyword (str): Keyword to search for in jokes.
        
        Returns:
            List[str]: Filtered list of jokes containing the keyword.
        """
        return [joke for joke in jokes if keyword.lower() in joke.lower()]
    
    def get_joke_of_the_day(self) -> Optional[str]:
        """
        Simulate a 'joke of the day' feature by randomly selecting a joke.
        
        Returns:
            Optional[str]: A randomly selected joke, or None if no jokes available.
        """
        jokes = self.fetch_multiple_jokes()
        return random.choice(jokes) if jokes else None