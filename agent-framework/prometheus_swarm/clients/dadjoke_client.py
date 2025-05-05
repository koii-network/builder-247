import requests
import typing

class DadJokeClient:
    """
    A client for fetching dad jokes from the icanhazdadjoke API.
    
    Attributes:
        base_url (str): Base URL for the icanhazdadjoke API
        headers (dict): Headers to include with API requests
    """
    
    def __init__(self, api_url: str = "https://icanhazdadjoke.com/"):
        """
        Initialize the Dad Joke API Client.
        
        Args:
            api_url (str, optional): Base URL for the dad joke API. Defaults to icanhazdadjoke.com.
        """
        self.base_url = api_url
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Dad Joke Python Client (github.com/project)"
        }
    
    def get_random_joke(self) -> typing.Dict[str, str]:
        """
        Fetch a random dad joke from the API.
        
        Returns:
            dict: A dictionary containing joke details with 'id', 'joke', and 'status' keys
        
        Raises:
            requests.RequestException: If there's a network or API error
        """
        try:
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch dad joke: {e}")
    
    def get_joke_by_id(self, joke_id: str) -> typing.Dict[str, str]:
        """
        Fetch a specific dad joke by its ID.
        
        Args:
            joke_id (str): The unique identifier of the joke
        
        Returns:
            dict: A dictionary containing joke details with 'id', 'joke', and 'status' keys
        
        Raises:
            requests.RequestException: If there's a network or API error
            ValueError: If no joke ID is provided
        """
        if not joke_id:
            raise ValueError("Joke ID cannot be empty")
        
        try:
            url = f"{self.base_url}j/{joke_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch dad joke with ID {joke_id}: {e}")
    
    def search_jokes(self, term: str, limit: int = 30) -> typing.Dict[str, typing.Any]:
        """
        Search for dad jokes containing a specific term.
        
        Args:
            term (str): Search term to find jokes
            limit (int, optional): Maximum number of jokes to return. Defaults to 30.
        
        Returns:
            dict: A dictionary containing search results with 'current_page', 'limit', 
                  'results', 'search_term', 'total_jokes', and 'total_pages' keys
        
        Raises:
            requests.RequestException: If there's a network or API error
            ValueError: If search term is empty or limit is invalid
        """
        if not term:
            raise ValueError("Search term cannot be empty")
        
        if limit < 1:
            raise ValueError("Limit must be a positive integer")
        
        try:
            params = {
                "term": term,
                "limit": limit
            }
            response = requests.get(f"{self.base_url}search", 
                                    params=params, 
                                    headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to search dad jokes: {e}")