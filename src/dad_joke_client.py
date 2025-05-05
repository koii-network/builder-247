import requests
import random

class DadJokeClient:
    """
    A client for fetching dad jokes from the icanhazdadjoke API.
    
    Attributes:
        base_url (str): Base URL for the icanhazdadjoke API
        headers (dict): HTTP headers for the API request
    """
    
    def __init__(self):
        """
        Initialize the DadJokeClient with the icanhazdadjoke API base URL and headers.
        """
        self.base_url = 'https://icanhazdadjoke.com/'
        self.headers = {
            'Accept': 'application/json',
            'User-Agent': 'Dad Joke API Client (https://github.com/your-repo)'
        }
    
    def get_random_joke(self):
        """
        Fetch a random dad joke from the API.
        
        Returns:
            str: A random dad joke text
        
        Raises:
            requests.RequestException: If there's an error fetching the joke
            ValueError: If no joke could be retrieved
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
            raise requests.RequestException(f"Error fetching dad joke: {e}")
    
    def get_joke_by_id(self, joke_id):
        """
        Fetch a specific dad joke by its ID.
        
        Args:
            joke_id (str): The unique identifier of the joke
        
        Returns:
            str: The text of the requested joke
        
        Raises:
            requests.RequestException: If there's an error fetching the joke
            ValueError: If the joke is not found
        """
        if not joke_id:
            raise ValueError("Joke ID cannot be empty")
        
        try:
            url = f'{self.base_url}j/{joke_id}'
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            joke_data = response.json()
            joke = joke_data.get('joke')
            
            if not joke:
                raise ValueError(f"No joke found with ID {joke_id}")
            
            return joke
        except requests.RequestException as e:
            raise requests.RequestException(f"Error fetching joke with ID {joke_id}: {e}")
    
    def search_jokes(self, term, limit=30):
        """
        Search for dad jokes containing a specific term.
        
        Args:
            term (str): Search term to find jokes
            limit (int, optional): Maximum number of jokes to return. Defaults to 30.
        
        Returns:
            list: A list of jokes matching the search term
        
        Raises:
            requests.RequestException: If there's an error searching for jokes
            ValueError: If search term is empty or no jokes are found
        """
        if not term:
            raise ValueError("Search term cannot be empty")
        
        try:
            params = {
                'term': term,
                'limit': limit
            }
            response = requests.get(f'{self.base_url}search', 
                                    params=params, 
                                    headers=self.headers)
            response.raise_for_status()
            
            search_results = response.json()
            jokes = search_results.get('results', [])
            
            if not jokes:
                raise ValueError(f"No jokes found matching the term '{term}'")
            
            return [joke['joke'] for joke in jokes]
        except requests.RequestException as e:
            raise requests.RequestException(f"Error searching for jokes with term '{term}': {e}")