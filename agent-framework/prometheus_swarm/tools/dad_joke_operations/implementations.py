import random
import requests
from typing import Dict, Any

from .definitions import DadJokeCommand

class DadJokeCommandHandler(DadJokeCommand):
    """
    Concrete implementation of the Dad Joke command handler.
    Retrieves dad jokes from an external API.
    """
    def get_dad_joke(self) -> Dict[str, Any]:
        """
        Retrieve a random dad joke from the icanhazdadjoke API.
        
        Returns:
            Dict[str, Any]: A dictionary containing the dad joke details.
            
        Raises:
            requests.RequestException: If there's an issue fetching the joke.
        """
        try:
            headers = {'Accept': 'application/json'}
            response = requests.get('https://icanhazdadjoke.com/', headers=headers)
            response.raise_for_status()
            joke_data = response.json()
            
            return {
                'joke': joke_data.get('joke', 'No joke found'),
                'id': joke_data.get('id', None)
            }
        except requests.RequestException as e:
            # If the API fails, return a local backup joke
            backup_jokes = [
                "Why don't scientists trust atoms? Because they make up everything!",
                "I told my wife she was drawing her eyebrows too high. She looked surprised.",
                "Why do programmers prefer dark mode? Because light attracts bugs!",
                "What do you call a fake noodle? An impasta!",
                "Why did the scarecrow win an award? Because he was outstanding in his field!"
            ]
            return {
                'joke': random.choice(backup_jokes),
                'id': None,
                'error': str(e)
            }