import requests
from typing import Dict, Optional

class DadJokeClient:
    """
    A client for interacting with the icanhazdadjoke.com API.
    
    This client provides methods to fetch random dad jokes and search for jokes.
    """
    
    BASE_URL = "https://icanhazdadjoke.com/"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Dad Joke Client.
        
        Args:
            api_key (Optional[str]): Optional API key. Not required for this specific API.
        """
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Prometheus Swarm (github.com/your-org/your-repo)"
        }
    
    def get_random_joke(self) -> Dict[str, str]:
        """
        Fetch a random dad joke.
        
        Returns:
            Dict[str, str]: A dictionary containing the joke details
        
        Raises:
            requests.RequestException: If there's an error fetching the joke
        """
        response = requests.get(self.BASE_URL, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def search_jokes(self, term: str, limit: int = 30) -> Dict[str, any]:
        """
        Search for dad jokes containing a specific term.
        
        Args:
            term (str): Search term for jokes
            limit (int, optional): Maximum number of jokes to return. Defaults to 30.
        
        Returns:
            Dict[str, any]: Search results including matching jokes
        
        Raises:
            requests.RequestException: If there's an error searching jokes
        """
        params = {
            "term": term,
            "limit": limit
        }
        response = requests.get(f"{self.BASE_URL}/search", headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()