import random
import requests

class DadJokeService:
    """
    A service layer for fetching and managing dad jokes.
    
    This service provides methods to retrieve dad jokes from an external API 
    and manage a local collection of jokes.
    """
    
    def __init__(self, api_url='https://icanhazdadjoke.com/'):
        """
        Initialize the Dad Joke Service.
        
        Args:
            api_url (str, optional): The URL for fetching dad jokes. 
                                     Defaults to the icanhazdadjoke API.
        """
        self.api_url = api_url
        self.local_jokes = [
            "I told my wife she was drawing her eyebrows too high. She looked surprised.",
            "Why don't scientists trust atoms? Because they make up everything!",
            "I'm afraid for the calendar. Its days are numbered.",
            "I used to be a baker, but I wasn't making enough dough.",
            "Why do bees have sticky hair? Because they use honeycombs."
        ]
    
    def get_random_joke(self, source='api'):
        """
        Retrieve a random dad joke.
        
        Args:
            source (str, optional): Source of the joke. 
                                    Can be 'api', 'local', or 'mixed'. 
                                    Defaults to 'api'.
        
        Returns:
            str: A dad joke.
        
        Raises:
            ValueError: If an invalid source is provided.
            RuntimeError: If API request fails.
        """
        if source not in ['api', 'local', 'mixed']:
            raise ValueError("Invalid joke source. Must be 'api', 'local', or 'mixed'.")
        
        if source == 'local':
            return random.choice(self.local_jokes)
        
        if source == 'api':
            try:
                headers = {'Accept': 'text/plain'}
                response = requests.get(self.api_url, headers=headers)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                raise RuntimeError(f"Failed to fetch joke from API: {e}")
        
        # Mixed source
        joke_sources = self.local_jokes + [self._fetch_api_joke()]
        return random.choice(joke_sources)
    
    def _fetch_api_joke(self):
        """
        Internal method to fetch a joke from the API.
        
        Returns:
            str: A dad joke from the API.
        
        Raises:
            RuntimeError: If API request fails.
        """
        try:
            headers = {'Accept': 'text/plain'}
            response = requests.get(self.api_url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch joke from API: {e}")
    
    def add_local_joke(self, joke):
        """
        Add a new joke to the local collection.
        
        Args:
            joke (str): The joke to add.
        
        Raises:
            ValueError: If the joke is empty or not a string.
        """
        if not isinstance(joke, str):
            raise ValueError("Joke must be a string")
        
        joke = joke.strip()
        if not joke:
            raise ValueError("Joke cannot be empty")
        
        if joke not in self.local_jokes:
            self.local_jokes.append(joke)
    
    def get_local_jokes(self):
        """
        Retrieve the list of local jokes.
        
        Returns:
            list: A list of local dad jokes.
        """
        return self.local_jokes.copy()