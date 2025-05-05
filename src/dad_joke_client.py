import requests

class DadJokeClient:
    """
    A client for interacting with the icanhazdadjoke.com API.

    Attributes:
        base_url (str): Base URL for the icanhazdadjoke API
        headers (dict): Request headers for the API
    """

    def __init__(self):
        """
        Initialize the Dad Joke API client with necessary headers.
        """
        self.base_url = "https://icanhazdadjoke.com/"
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Dad Joke API Python Client"
        }

    def get_random_joke(self):
        """
        Fetch a random dad joke from the API.

        Returns:
            str: The text of a random dad joke

        Raises:
            requests.RequestException: If there's an error fetching the joke
            ValueError: If the joke cannot be retrieved
        """
        try:
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            joke_data = response.json()
            
            if not joke_data or 'joke' not in joke_data:
                raise ValueError("Unable to retrieve joke")
            
            return joke_data['joke']
        
        except requests.RequestException as e:
            raise requests.RequestException(f"Error fetching dad joke: {e}")

    def search_jokes(self, term, limit=30):
        """
        Search for dad jokes containing a specific term.

        Args:
            term (str): Search term for jokes
            limit (int, optional): Maximum number of jokes to return. Defaults to 30.

        Returns:
            list: A list of jokes matching the search term

        Raises:
            requests.RequestException: If there's an error searching jokes
            ValueError: If search parameters are invalid
        """
        if not term or not isinstance(term, str):
            raise ValueError("Search term must be a non-empty string")

        if limit < 1 or limit > 30:
            raise ValueError("Limit must be between 1 and 30")

        try:
            params = {
                "term": term,
                "limit": limit
            }
            response = requests.get(f"{self.base_url}search", 
                                    params=params, 
                                    headers=self.headers)
            response.raise_for_status()
            search_data = response.json()

            if not search_data or 'results' not in search_data:
                return []

            return [joke['joke'] for joke in search_data['results']]
        
        except requests.RequestException as e:
            raise requests.RequestException(f"Error searching dad jokes: {e}")