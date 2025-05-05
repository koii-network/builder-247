import requests

class DadJokeService:
    """
    A service to interact with the icanhazdadjoke.com API for retrieving dad jokes.
    """
    BASE_URL = "https://icanhazdadjoke.com/"
    
    def __init__(self, api_key=None):
        """
        Initialize the Dad Joke Service.
        
        :param api_key: Optional API key (not required for this public API)
        """
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Dad Joke Service"
        }
    
    def get_random_joke(self):
        """
        Fetch a random dad joke from the API.
        
        :return: A dictionary containing the joke details
        :raises requests.RequestException: If there's an error fetching the joke
        """
        try:
            response = requests.get(self.BASE_URL, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch dad joke: {str(e)}")
    
    def search_jokes(self, term, limit=30):
        """
        Search for dad jokes containing a specific term.
        
        :param term: Search term for jokes
        :param limit: Maximum number of jokes to return (default 30)
        :return: A list of jokes matching the search term
        :raises requests.RequestException: If there's an error searching jokes
        """
        if not term or not isinstance(term, str):
            raise ValueError("Search term must be a non-empty string")
        
        try:
            params = {
                "term": term,
                "limit": limit
            }
            response = requests.get(f"{self.BASE_URL}search", 
                                    headers=self.headers, 
                                    params=params)
            response.raise_for_status()
            return response.json().get('results', [])
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to search dad jokes: {str(e)}")