import requests
from typing import Dict, Optional
from .base_client import BaseClient
from prometheus_swarm.utils.errors import APIClientError

class DadJokeClient(BaseClient):
    """
    A client for interacting with the icanhazdadjoke.com API to fetch dad jokes.

    Attributes:
        base_url (str): The base URL for the Dad Joke API.
        headers (Dict[str, str]): Headers for API requests.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Dad Joke API Client.

        Args:
            api_key (Optional[str], optional): Optional API key for future use. Defaults to None.
        """
        super().__init__()
        self.base_url = "https://icanhazdadjoke.com"
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "PrometheusSwarm/1.0 (https://github.com/your-project)"
        }

    def get_random_joke(self) -> str:
        """
        Fetch a random dad joke from the API.

        Returns:
            str: A random dad joke.

        Raises:
            APIClientError: If there's an error fetching the joke.
        """
        try:
            response = requests.get(
                f"{self.base_url}/",
                headers=self.headers
            )
            response.raise_for_status()
            joke_data = response.json()
            return joke_data.get('joke', 'No joke found')
        except requests.RequestException as e:
            raise APIClientError(f"Failed to fetch dad joke: {str(e)}")

    def search_jokes(self, term: str, limit: int = 5) -> list:
        """
        Search for dad jokes containing a specific term.

        Args:
            term (str): Search term for jokes.
            limit (int, optional): Maximum number of jokes to return. Defaults to 5.

        Returns:
            list: A list of jokes matching the search term.

        Raises:
            APIClientError: If there's an error searching for jokes.
        """
        try:
            response = requests.get(
                f"{self.base_url}/search",
                params={'term': term, 'limit': limit},
                headers=self.headers
            )
            response.raise_for_status()
            results = response.json()
            return [joke['joke'] for joke in results.get('results', [])]
        except requests.RequestException as e:
            raise APIClientError(f"Failed to search dad jokes: {str(e)}")