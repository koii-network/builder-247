import requests
from typing import Dict, Optional
from .base_client import BaseClient

class DadJokeClient(BaseClient):
    """
    A client for fetching Dad Jokes from the icanhazdadjoke.com API.
    
    Attributes:
        base_url (str): Base URL for the Dad Joke API
        headers (Dict[str, str]): Headers for API requests
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Dad Joke Client.
        
        Args:
            api_key (Optional[str]): Optional API key (not required for this API)
        """
        self.base_url = "https://icanhazdadjoke.com/"
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Prometheus Swarm Dad Joke Client"
        }
    
    def get_random_joke(self) -> str:
        """
        Fetch a random dad joke.
        
        Returns:
            str: A random dad joke
        
        Raises:
            requests.RequestException: If there's an error fetching the joke
            ValueError: If the joke cannot be retrieved
        """
        try:
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()
            joke_data = response.json()
            
            if not joke_data or 'joke' not in joke_data:
                raise ValueError("No joke found in response")
            
            return joke_data['joke']
        except requests.RequestException as e:
            raise requests.RequestException(f"Error fetching dad joke: {e}")
    
    def get_joke_by_id(self, joke_id: str) -> str:
        """
        Fetch a specific dad joke by its ID.
        
        Args:
            joke_id (str): The unique identifier of the joke
        
        Returns:
            str: The requested dad joke
        
        Raises:
            requests.RequestException: If there's an error fetching the joke
            ValueError: If the joke cannot be retrieved
        """
        try:
            url = f"{self.base_url}j/{joke_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            joke_data = response.json()
            
            if not joke_data or 'joke' not in joke_data:
                raise ValueError(f"No joke found for ID: {joke_id}")
            
            return joke_data['joke']
        except requests.RequestException as e:
            raise requests.RequestException(f"Error fetching dad joke with ID {joke_id}: {e}")