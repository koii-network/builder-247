import requests
import random

class DadJokeService:
    """
    A service for fetching and managing dad jokes from an API.
    """
    
    API_BASE_URL = "https://icanhazdadjoke.com/"
    
    def __init__(self, api_key=None):
        """
        Initialize the Dad Joke Service.
        
        :param api_key: Optional API key for authentication
        """
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "DadJokeService/1.0"
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    def get_random_joke(self):
        """
        Fetch a random dad joke from the API.
        
        :return: A dictionary containing the joke details
        :raises requests.RequestException: If there's an issue fetching the joke
        """
        try:
            response = requests.get(self.API_BASE_URL, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch dad joke: {str(e)}")
    
    def search_jokes(self, term=None, limit=5):
        """
        Search for dad jokes containing a specific term.
        
        :param term: Optional search term
        :param limit: Maximum number of jokes to return
        :return: A list of jokes matching the search term
        :raises requests.RequestException: If there's an issue searching jokes
        """
        if not term:
            return []
        
        try:
            params = {
                "term": term,
                "limit": limit
            }
            response = requests.get(
                f"{self.API_BASE_URL}search", 
                headers=self.headers, 
                params=params
            )
            response.raise_for_status()
            return response.json().get('results', [])
        except requests.RequestException as e:
            raise ValueError(f"Failed to search dad jokes: {str(e)}")
    
    def validate_joke(self, joke):
        """
        Validate if a joke meets certain criteria.
        
        :param joke: A joke dictionary
        :return: Boolean indicating if the joke is valid
        """
        if not isinstance(joke, dict):
            return False
        
        required_keys = ['id', 'joke', 'status']
        return all(key in joke for key in required_keys) and \
               isinstance(joke.get('joke', ''), str) and \
               len(joke.get('joke', '')) > 0