import requests
from typing import Dict, Optional
from .base_client import Client

class DadJokeClient(Client):
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
        super().__init__()  # Initialize base Client
        self.base_url = "https://icanhazdadjoke.com/"
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Prometheus Swarm Dad Joke Client"
        }
    
    def _get_default_model(self) -> str:
        """Model is not applicable for a joke API client."""
        return "dadjoke_api"
    
    def _get_api_name(self) -> str:
        """Return the name of the API."""
        return "DadJoke"
    
    def _convert_tool_to_api_format(self, tool: Dict) -> Dict:
        """Not applicable for this client."""
        return {}
    
    def _convert_message_to_api_format(self, message: Dict) -> Dict:
        """Not applicable for this client."""
        return {}
    
    def _convert_api_response_to_message(self, response: Dict) -> Dict:
        """Not applicable for this client."""
        return {}
    
    def _make_api_call(self, **kwargs) -> Dict:
        """Not applicable for this client."""
        return {}
    
    def _format_tool_response(self, response: str) -> Dict:
        """Not applicable for this client."""
        return {}
    
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