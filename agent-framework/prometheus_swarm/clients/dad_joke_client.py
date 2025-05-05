import requests

class DadJokeClient:
    """
    A client for fetching dad jokes from the icanhazdadjoke API.
    """
    BASE_URL = "https://icanhazdadjoke.com/"

    def __init__(self):
        """
        Initialize the Dad Joke Client with default headers.
        """
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Prometheus SwarmAI (github.com/your-org/project)"
        }

    def get_random_joke(self):
        """
        Fetch a random dad joke from the API.

        Returns:
            dict: A dictionary containing the joke details.
            
        Raises:
            requests.RequestException: If there's an error fetching the joke.
        """
        try:
            response = requests.get(self.BASE_URL, headers=self.headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch dad joke: {str(e)}")

    def search_jokes(self, term):
        """
        Search for dad jokes containing a specific term.

        Args:
            term (str): The search term to find jokes.

        Returns:
            dict: A dictionary containing search results.
            
        Raises:
            requests.RequestException: If there's an error searching jokes.
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}search", 
                headers=self.headers, 
                params={"term": term, "limit": 30}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to search dad jokes: {str(e)}")