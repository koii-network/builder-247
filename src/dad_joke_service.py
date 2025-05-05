import requests

class DadJokeService:
    """
    A service layer for fetching and managing dad jokes.
    
    Attributes:
        base_url (str): The base URL for the icanhazdadjoke API
    """
    def __init__(self, base_url="https://icanhazdadjoke.com/"):
        """
        Initialize the DadJokeService with a base URL.
        
        Args:
            base_url (str, optional): URL for the dad joke API. Defaults to icanhazdadjoke.com.
        """
        self.base_url = base_url
        self.headers = {
            'Accept': 'application/json',
            'User-Agent': 'Dad Joke Service'
        }

    def get_random_joke(self):
        """
        Fetch a random dad joke from the API.
        
        Returns:
            dict: A dictionary containing the joke details with keys 'id' and 'joke'.
        
        Raises:
            requests.RequestException: If there's an error fetching the joke.
        """
        try:
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch dad joke: {e}")

    def get_joke_by_id(self, joke_id):
        """
        Fetch a specific dad joke by its ID.
        
        Args:
            joke_id (str): The unique identifier of the joke.
        
        Returns:
            dict: A dictionary containing the joke details with keys 'id' and 'joke'.
        
        Raises:
            requests.RequestException: If there's an error fetching the joke.
            ValueError: If no joke is found with the given ID.
        """
        try:
            url = f"{self.base_url}j/{joke_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            joke_data = response.json()
            
            if not joke_data or 'joke' not in joke_data:
                raise ValueError(f"No joke found with ID: {joke_id}")
            
            return joke_data
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch dad joke: {e}")

    def search_jokes(self, term, limit=30):
        """
        Search for dad jokes containing a specific term.
        
        Args:
            term (str): The search term to find jokes.
            limit (int, optional): Maximum number of jokes to return. Defaults to 30.
        
        Returns:
            list: A list of joke dictionaries matching the search term.
        
        Raises:
            requests.RequestException: If there's an error searching for jokes.
            ValueError: If the search term is too short.
        """
        if len(term) < 2:
            raise ValueError("Search term must be at least 2 characters long")

        try:
            params = {
                'term': term,
                'limit': limit
            }
            response = requests.get(f"{self.base_url}search", params=params, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            return result.get('results', [])
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to search dad jokes: {e}")