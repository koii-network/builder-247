import requests
from typing import Dict, Optional

class DadJokeClient:
    """
    A client for fetching Dad Jokes from the icanhazdadjoke.com API.
    
    Attributes:
        base_url (str): Base URL for the Dad Joke API
        headers (Dict[str, str]): HTTP headers for the API request
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Dad Joke Client.
        
        Args:
            api_key (Optional[str]): Optional API key if required in the future
        """
        self.base_url = "https://icanhazdadjoke.com/"
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Prometheus Swarm Dad Joke Client"
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    def get_random_joke(self) -> str:
        """
        Fetch a random dad joke.
        
        Returns:
            str: A random dad joke
        
        Raises:
            requests.RequestException: If there's an error fetching the joke
            ValueError: If no joke is found
        """
        try:
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()
            joke_data = response.json()
            
            if not joke_data or 'joke' not in joke_data:
                raise ValueError("No joke found in the response")
            
            return joke_data['joke']
        except requests.RequestException as e:
            raise requests.RequestException(f"Error fetching dad joke: {e}")
    
    def search_jokes(self, term: str, limit: int = 5) -> Dict[str, list]:
        """
        Search for dad jokes containing a specific term.
        
        Args:
            term (str): Search term for jokes
            limit (int, optional): Maximum number of jokes to return. Defaults to 5.
        
        Returns:
            Dict[str, list]: A dictionary with search results
        
        Raises:
            requests.RequestException: If there's an error searching jokes
            ValueError: If search term is empty
        """
        if not term:
            raise ValueError("Search term cannot be empty")
        
        try:
            params = {
                "term": term,
                "limit": limit
            }
            response = requests.get(f"{self.base_url}search", 
                                    headers=self.headers, 
                                    params=params)
            response.raise_for_status()
            search_data = response.json()
            
            return {
                "total_jokes": search_data.get('total_jokes', 0),
                "jokes": [joke['joke'] for joke in search_data.get('results', [])]
            }
        except requests.RequestException as e:
            raise requests.RequestException(f"Error searching dad jokes: {e}")