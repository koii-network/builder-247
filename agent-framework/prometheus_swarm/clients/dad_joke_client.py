import requests
from typing import Dict, Optional

class DadJokeClient:
    """
    Client for interacting with the icanhazdadjoke.com API
    """
    BASE_URL = "https://icanhazdadjoke.com"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Dad Joke API client
        
        :param api_key: Optional API key (not required for this public API)
        """
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "PrometheusSwarm/1.0"
        }
    
    def get_random_joke(self) -> Dict[str, str]:
        """
        Fetch a random dad joke from the API
        
        :return: Dictionary containing joke details
        :raises: requests.RequestException for network or API errors
        """
        try:
            response = requests.get(
                self.BASE_URL, 
                headers=self.headers
            )
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch dad joke: {str(e)}")
    
    def search_jokes(self, term: str, limit: int = 30) -> Dict[str, any]:
        """
        Search for dad jokes containing a specific term
        
        :param term: Search term for jokes
        :param limit: Maximum number of jokes to return (default 30)
        :return: Dictionary containing search results
        :raises: requests.RequestException for network or API errors
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/search", 
                headers=self.headers,
                params={
                    "term": term,
                    "limit": limit
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to search dad jokes: {str(e)}")