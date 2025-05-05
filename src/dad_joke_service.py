import requests

class DadJokeService:
    """
    A service for fetching dad jokes from an API.
    """
    BASE_URL = "https://icanhazdadjoke.com/"

    def __init__(self, api_key=None):
        """
        Initialize the Dad Joke Service.
        
        :param api_key: Optional API key (not required for this particular API)
        """
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "DadJokeService/1.0"
        }

    def get_random_joke(self):
        """
        Fetch a random dad joke.
        
        :return: A dictionary containing joke details
        :raises: requests.RequestException for network or API errors
        """
        try:
            response = requests.get(self.BASE_URL, headers=self.headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            joke_data = response.json()
            
            # Validate the joke data
            if not joke_data or 'joke' not in joke_data:
                raise ValueError("Invalid joke data received")
            
            return joke_data
        except (requests.RequestException, ValueError) as e:
            raise RuntimeError(f"Failed to fetch dad joke: {str(e)}")

    def search_jokes(self, term, limit=5):
        """
        Search for dad jokes containing a specific term.
        
        :param term: Search term for jokes
        :param limit: Maximum number of jokes to return (default 5)
        :return: A list of jokes matching the search term
        :raises: requests.RequestException for network or API errors
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
            
            search_results = response.json()
            
            # Validate search results
            if not search_results or 'results' not in search_results:
                return []
            
            return search_results['results']
        except (requests.RequestException, ValueError) as e:
            raise RuntimeError(f"Failed to search dad jokes: {str(e)}")