import random
import requests

class DadJokeService:
    """
    A service layer for fetching and managing dad jokes.
    
    Uses the icanhazdadjoke.com API to retrieve random dad jokes.
    """
    
    BASE_URL = "https://icanhazdadjoke.com/"
    
    def __init__(self, api_key=None):
        """
        Initialize the Dad Joke Service.
        
        :param api_key: Optional API key (not required for icanhazdadjoke.com)
        """
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Dad Joke Service (github.com/your-repo)"
        }
    
    def get_random_joke(self):
        """
        Fetch a random dad joke from the API.
        
        :return: A dictionary containing the joke details
        :raises: requests.RequestException if network or API error occurs
        """
        try:
            response = requests.get(self.BASE_URL, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch dad joke: {str(e)}")
    
    def get_joke_by_id(self, joke_id):
        """
        Fetch a specific dad joke by its ID.
        
        :param joke_id: Unique identifier for the joke
        :return: A dictionary containing the joke details
        :raises: ValueError if joke not found or API error
        """
        if not joke_id:
            raise ValueError("Joke ID cannot be empty")
        
        try:
            url = f"{self.BASE_URL}j/{joke_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch joke with ID {joke_id}: {str(e)}")
    
    def get_joke_text(self, joke_dict):
        """
        Extract the joke text from a joke dictionary.
        
        :param joke_dict: Dictionary containing joke details
        :return: The joke text
        :raises: KeyError if joke text cannot be extracted
        """
        try:
            return joke_dict['joke']
        except KeyError:
            raise ValueError("Invalid joke dictionary format")