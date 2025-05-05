import requests

class DadJokeClient:
    """
    A client for fetching dad jokes from the icanhazdadjoke API.
    
    Attributes:
        base_url (str): Base URL for the icanhazdadjoke API
        headers (dict): HTTP headers for the API request
    """
    
    def __init__(self, api_url='https://icanhazdadjoke.com/'):
        """
        Initialize the Dad Joke Client.
        
        Args:
            api_url (str, optional): Base URL for the dad joke API. Defaults to icanhazdadjoke.com.
        """
        self.base_url = api_url
        self.headers = {
            'Accept': 'application/json',
            'User-Agent': 'Dad Joke API Client'
        }
    
    def get_random_joke(self):
        """
        Fetch a random dad joke from the API.
        
        Returns:
            str: A random dad joke text.
        
        Raises:
            requests.RequestException: If there's an error fetching the joke.
            ValueError: If no joke could be retrieved.
        """
        try:
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            joke_data = response.json()
            joke = joke_data.get('joke')
            
            if not joke:
                raise ValueError("No joke found in the API response")
            
            return joke
        
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch dad joke: {e}")
    
    def search_jokes(self, term):
        """
        Search for dad jokes containing a specific term.
        
        Args:
            term (str): Search term for jokes.
        
        Returns:
            list: A list of jokes matching the search term.
        
        Raises:
            requests.RequestException: If there's an error searching jokes.
            ValueError: If no search term is provided.
        """
        if not term:
            raise ValueError("Search term must not be empty")
        
        try:
            params = {'term': term}
            response = requests.get(f"{self.base_url}search", 
                                    headers=self.headers, 
                                    params=params)
            response.raise_for_status()
            
            search_data = response.json()
            jokes = search_data.get('results', [])
            
            return [joke['joke'] for joke in jokes]
        
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to search dad jokes: {e}")