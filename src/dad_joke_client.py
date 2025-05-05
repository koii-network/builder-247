import requests

class DadJokeClient:
    """
    A client for fetching dad jokes from the icanhazdadjoke.com API.
    
    Attributes:
        base_url (str): Base URL for the icanhazdadjoke API
        headers (dict): Headers for API requests
    """
    
    def __init__(self, api_url="https://icanhazdadjoke.com/"):
        """
        Initialize the Dad Joke Client.
        
        Args:
            api_url (str, optional): Base URL for the API. Defaults to icanhazdadjoke.com.
        """
        self.base_url = api_url
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Dad Joke Client (github.com/example/dad-joke-client)"
        }
    
    def get_random_joke(self):
        """
        Fetch a random dad joke from the API.
        
        Returns:
            dict: A dictionary containing the joke details with 'id', 'joke', and 'status' keys.
        
        Raises:
            requests.RequestException: If there's a network or API error
            ValueError: If the API response is invalid
        """
        try:
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            joke_data = response.json()
            
            if not joke_data or 'joke' not in joke_data:
                raise ValueError("Invalid joke response from API")
            
            return joke_data
        
        except requests.RequestException as e:
            raise requests.RequestException(f"Error fetching joke: {e}")
    
    def search_jokes(self, term, limit=5):
        """
        Search for dad jokes containing a specific term.
        
        Args:
            term (str): Search term for jokes
            limit (int, optional): Maximum number of jokes to return. Defaults to 5.
        
        Returns:
            list: A list of joke dictionaries matching the search term
        
        Raises:
            requests.RequestException: If there's a network or API error
            ValueError: If the input parameters are invalid
        """
        if not term:
            raise ValueError("Search term cannot be empty")
        
        if limit < 1:
            raise ValueError("Limit must be at least 1")
        
        try:
            params = {
                "term": term,
                "limit": limit
            }
            response = requests.get(
                f"{self.base_url}search", 
                headers=self.headers, 
                params=params
            )
            response.raise_for_status()
            
            search_results = response.json()
            
            if not search_results or 'results' not in search_results:
                raise ValueError("Invalid search response from API")
            
            return search_results['results']
        
        except requests.RequestException as e:
            raise requests.RequestException(f"Error searching jokes: {e}")