import requests
from typing import Dict, Optional

class DadJokeClient:
    """
    Client for interacting with the icanhazdadjoke.com API
    """
    BASE_URL = "https://icanhazdadjoke.com/"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Dad Joke client
        
        :param api_key: Optional API key (not required for this free API)
        """
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Prometheus Swarm Dad Joke Integration"
        }
    
    def get_random_joke(self) -> Dict[str, str]:
        """
        Fetch a random dad joke from the API
        
        :return: Dictionary containing joke details
        :raises requests.RequestException: If there's an error fetching the joke
        """
        try:
            response = requests.get(self.BASE_URL, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch dad joke: {e}")
    
    def search_jokes(self, term: str, limit: int = 5) -> Dict[str, any]:
        """
        Search for dad jokes containing a specific term
        
        :param term: Search term for jokes
        :param limit: Maximum number of jokes to return
        :return: Dictionary of search results
        :raises requests.RequestException: If there's an error searching jokes
        """
        if not term:
            raise ValueError("Search term cannot be empty")
        
        params = {
            "term": term,
            "limit": limit
        }
        
        try:
            response = requests.get(f"{self.BASE_URL}search", 
                                    headers=self.headers, 
                                    params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to search dad jokes: {e}")