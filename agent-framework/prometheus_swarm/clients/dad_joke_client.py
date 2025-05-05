import requests
from typing import Dict, Optional, Any

class DadJokeClient:
    """
    A client for fetching dad jokes from the icanhazdadjoke API.
    
    This service provides methods to retrieve random dad jokes 
    and search for jokes based on specific keywords.
    """

    BASE_URL = "https://icanhazdadjoke.com"

    def __init__(self, timeout: int = 10):
        """
        Initialize the Dad Joke Client.
        
        :param timeout: Request timeout in seconds, defaults to 10
        """
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Prometheus Swarm Dad Joke Service"
        }
        self.timeout = timeout

    def get_random_joke(self) -> Optional[str]:
        """
        Fetch a random dad joke.
        
        :return: A random dad joke string, or None if request fails
        """
        try:
            response = requests.get(
                self.BASE_URL, 
                headers=self.headers, 
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json().get('joke')
        except (requests.RequestException, ValueError, KeyError):
            return None

    def search_jokes(self, term: str, limit: int = 5) -> list:
        """
        Search for dad jokes containing a specific term.
        
        :param term: Search term for jokes
        :param limit: Maximum number of jokes to return, defaults to 5
        :return: List of jokes matching the search term
        """
        if not term or not isinstance(term, str):
            return []

        try:
            response = requests.get(
                f"{self.BASE_URL}/search", 
                params={"term": term, "limit": limit},
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Extract jokes from the response
            results = response.json().get('results', [])
            return [joke.get('joke') for joke in results if joke.get('joke')]
        
        except (requests.RequestException, ValueError, KeyError):
            return []