import random
from typing import Dict, Any
import requests

class DefaultDadJokeCommandHandler:
    """
    Default implementation of the DadJokeCommandHandler.
    
    Uses an external API to fetch dad jokes and provides basic joke rating.
    """
    
    def __init__(self, api_url: str = "https://icanhazdadjoke.com/"):
        """
        Initialize the dad joke command handler.
        
        Args:
            api_url (str, optional): URL for dad joke API. Defaults to icanhazdadjoke.com.
        """
        self.api_url = api_url
        self.joke_ratings = {}
    
    def get_random_joke(self) -> str:
        """
        Retrieve a random dad joke from the API.
        
        Returns:
            str: A random dad joke
        
        Raises:
            Exception: If unable to retrieve a joke
        """
        headers = {
            "Accept": "text/plain",
            "User-Agent": "Prometheus Swarm Dad Joke Bot"
        }
        
        try:
            response = requests.get(self.api_url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch dad joke: {e}")
    
    def tell_joke(self, context: Dict[str, Any] = None) -> str:
        """
        Tell a dad joke, with optional context filtering.
        
        Args:
            context (Dict[str, Any], optional): Additional context for joke telling
        
        Returns:
            str: The dad joke that was told
        
        Raises:
            ValueError: If joke cannot be told under specified context
        """
        joke = self.get_random_joke()
        
        # Optional context-based filtering could be added here
        if context and context.get('filter_length') and len(joke) > context['filter_length']:
            raise ValueError(f"Joke too long: {len(joke)} characters")
        
        return joke
    
    def rate_joke(self, joke: str, rating: int) -> Dict[str, Any]:
        """
        Rate a dad joke.
        
        Args:
            joke (str): The joke to rate
            rating (int): Rating from 1-5
        
        Returns:
            Dict[str, Any]: Joke rating result
        
        Raises:
            ValueError: If rating is out of valid range
        """
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        
        # Track joke ratings
        if joke not in self.joke_ratings:
            self.joke_ratings[joke] = {'total_rating': rating, 'count': 1}
        else:
            self.joke_ratings[joke]['total_rating'] += rating
            self.joke_ratings[joke]['count'] += 1
        
        average_rating = self.joke_ratings[joke]['total_rating'] / self.joke_ratings[joke]['count']
        
        return {
            'joke': joke,
            'rating': rating,
            'average_rating': round(average_rating, 2),
            'total_ratings': self.joke_ratings[joke]['count']
        }