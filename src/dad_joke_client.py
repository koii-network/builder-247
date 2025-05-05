import requests

class DadJokeClient:
    """
    A client for fetching dad jokes from the icanhazdadjoke API.
    
    Attributes:
        base_url (str): Base URL for the icanhazdadjoke API
        headers (dict): Headers for the API request
    """
    
    def __init__(self):
        """
        Initialize the Dad Joke Client with default configuration.
        """
        self.base_url = "https://icanhazdadjoke.com/"
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Dad Joke API Client (github.com/yourusername/repo)"
        }
    
    def get_random_joke(self):
        """
        Fetch a random dad joke.
        
        Returns:
            str: The text of a random dad joke
        
        Raises:
            requests.RequestException: If there's an issue with the API request
            ValueError: If the joke cannot be retrieved
        """
        try:
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            joke_data = response.json()
            joke = joke_data.get('joke')
            
            if not joke:
                raise ValueError("Could not retrieve a joke from the API")
            
            return joke
        
        except requests.RequestException as e:
            raise requests.RequestException(f"Error fetching dad joke: {e}")
    
    def search_jokes(self, term, limit=5):
        """
        Search for dad jokes containing a specific term.
        
        Args:
            term (str): Search term to find jokes
            limit (int, optional): Maximum number of jokes to return. Defaults to 5.
        
        Returns:
            list: A list of jokes matching the search term
        
        Raises:
            ValueError: If search term is invalid or no jokes are found
        """
        if not term or not isinstance(term, str):
            raise ValueError("Search term must be a non-empty string")
        
        try:
            params = {
                "term": term,
                "limit": limit
            }
            
            response = requests.get(f"{self.base_url}search", 
                                    headers=self.headers, 
                                    params=params)
            response.raise_for_status()
            
            search_results = response.json()
            jokes = search_results.get('results', [])
            
            if not jokes:
                return []
            
            return [joke['joke'] for joke in jokes]
        
        except requests.RequestException as e:
            raise requests.RequestException(f"Error searching jokes: {e}")