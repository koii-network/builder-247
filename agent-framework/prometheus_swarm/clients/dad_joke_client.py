import requests
from typing import Dict, Optional

class DadJokeClient:
    """
    A client for fetching Dad Jokes from the icanhazdadjoke.com API.
    """
    BASE_URL = "https://icanhazdadjoke.com"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Dad Joke Client.

        :param api_key: Optional API key (not required for this public API)
        """
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Prometheus Swarm Dad Joke Client (https://github.com/yourusername/project)"
        }

    def get_random_joke(self) -> str:
        """
        Fetch a random dad joke.

        :return: A random dad joke
        :raises requests.RequestException: If there's an error fetching the joke
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()['joke']
        except (requests.RequestException, KeyError) as e:
            raise ValueError(f"Failed to fetch dad joke: {str(e)}")

    def search_jokes(self, term: str, limit: int = 5) -> Dict[str, list]:
        """
        Search for dad jokes containing a specific term.

        :param term: Search term to find jokes
        :param limit: Maximum number of jokes to return (default 5)
        :return: Dictionary with search results
        :raises ValueError: If search term is invalid or no jokes found
        """
        if not term or len(term.strip()) == 0:
            raise ValueError("Search term must not be empty")

        try:
            response = requests.get(
                f"{self.BASE_URL}/search",
                params={'term': term, 'limit': limit},
                headers=self.headers
            )
            response.raise_for_status()
            results = response.json()

            if results['total_jokes'] == 0:
                return {"jokes": [], "total_jokes": 0}

            return {
                "jokes": [joke['joke'] for joke in results['results']],
                "total_jokes": results['total_jokes']
            }
        except (requests.RequestException, KeyError) as e:
            raise ValueError(f"Failed to search dad jokes: {str(e)}")