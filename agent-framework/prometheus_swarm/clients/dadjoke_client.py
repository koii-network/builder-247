import requests

class DadJokeClient:
    """
    Client for interacting with the icanhazdadjoke.com API
    """
    BASE_URL = "https://icanhazdadjoke.com/"

    def __init__(self, api_key=None):
        """
        Initialize the Dad Joke Client

        :param api_key: Optional API key (not required for this API)
        """
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Prometheus Swarm Agent (github.com/your-repo)"
        }

    def get_random_joke(self):
        """
        Fetch a random dad joke from the API

        :return: A dictionary containing the joke details
        :raises: requests.RequestException for network/API errors
        """
        try:
            response = requests.get(self.BASE_URL, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch dad joke: {str(e)}")

    def search_jokes(self, term):
        """
        Search for dad jokes containing a specific term

        :param term: Search term to find jokes
        :return: A list of jokes matching the search term
        :raises: requests.RequestException for network/API errors
        """
        if not term or not isinstance(term, str):
            raise ValueError("Search term must be a non-empty string")

        try:
            params = {"term": term, "limit": 30}
            response = requests.get(f"{self.BASE_URL}search", 
                                    headers=self.headers, 
                                    params=params)
            response.raise_for_status()
            return response.json().get('results', [])
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to search dad jokes: {str(e)}")