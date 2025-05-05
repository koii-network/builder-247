import requests
import random

class DadJokeService:
    """
    Service for fetching and managing dad jokes.
    """
    ICANHAZDADJOKE_API = "https://icanhazdadjoke.com/"

    def __init__(self, api_url=None):
        """
        Initialize the Dad Joke Service.
        
        :param api_url: Optional custom API URL, defaults to icanhazdadjoke.com
        """
        self.api_url = api_url or self.ICANHAZDADJOKE_API

    def get_random_joke(self):
        """
        Fetch a random dad joke from the API.
        
        :return: A dictionary containing joke details
        :raises requests.RequestException: If API request fails
        """
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'DadJokeService'
        }
        
        try:
            response = requests.get(self.api_url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch dad joke: {str(e)}")

    def get_joke_by_id(self, joke_id):
        """
        Fetch a specific dad joke by its ID.
        
        :param joke_id: Unique identifier for the joke
        :return: A dictionary containing joke details
        :raises ValueError: If joke_id is invalid
        :raises requests.RequestException: If API request fails
        """
        if not joke_id or not isinstance(joke_id, str):
            raise ValueError("Invalid joke ID")

        headers = {
            'Accept': 'application/json',
            'User-Agent': 'DadJokeService'
        }
        
        try:
            response = requests.get(f"{self.api_url}j/{joke_id}", headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch dad joke: {str(e)}")

    def search_jokes(self, term, limit=30):
        """
        Search for dad jokes containing a specific term.
        
        :param term: Search term
        :param limit: Maximum number of results (default 30)
        :return: List of jokes matching the search term
        :raises ValueError: If search term is invalid
        :raises requests.RequestException: If API request fails
        """
        if not term or not isinstance(term, str):
            raise ValueError("Invalid search term")

        headers = {
            'Accept': 'application/json',
            'User-Agent': 'DadJokeService'
        }
        
        params = {
            'term': term,
            'limit': limit
        }
        
        try:
            response = requests.get(f"{self.api_url}search", params=params, headers=headers)
            response.raise_for_status()
            return response.json().get('results', [])
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to search dad jokes: {str(e)}")