import random
import requests
from typing import Dict, Optional

class DadJokeService:
    """Service layer for retrieving and managing dad jokes."""

    def __init__(self, api_url: str = "https://icanhazdadjoke.com/"):
        """
        Initialize the Dad Joke Service.

        Args:
            api_url (str, optional): Base URL for dad joke API. 
                                     Defaults to icanhazdadjoke.com.
        """
        self.api_url = api_url
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Prometheus Swarm Dad Joke Service"
        }

    def get_random_joke(self) -> Optional[Dict[str, str]]:
        """
        Retrieve a random dad joke from the API.

        Returns:
            Optional[Dict[str, str]]: A dictionary containing joke details, 
                                      or None if joke retrieval fails.
        """
        try:
            response = requests.get(self.api_url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None

    def generate_custom_joke(self, topics: Optional[list] = None) -> str:
        """
        Generate a custom dad joke based on optional topics.

        Args:
            topics (Optional[list], optional): List of topics to inspire the joke. 
                                               Defaults to None.

        Returns:
            str: A generated dad joke.
        """
        dad_joke_templates = [
            "Why did the {subject} {verb} the {object}? {punchline}",
            "I'm thinking about a joke about {subject}, but {punchline}",
            "What do you call a {subject} that {verb}? {punchline}"
        ]

        if not topics:
            topics = ["programmer", "engineer", "scientist", "bear", "chicken"]

        subject = random.choice(topics)
        verbs = ["cross", "go", "want", "decide", "attempt"]
        objects = ["road", "mountain", "computer", "challenge"]
        punchlines = [
            "Because it was there!",
            "That's a great question.",
            "I have no idea, but it's hilarious!",
            "Nobody knows, but it's comedy gold!",
            "To get to the other side, obviously!"
        ]

        return random.choice(dad_joke_templates).format(
            subject=subject,
            verb=random.choice(verbs),
            object=random.choice(objects),
            punchline=random.choice(punchlines)
        )

    def validate_joke(self, joke: str, max_length: int = 280) -> bool:
        """
        Validate a dad joke for appropriateness and length.

        Args:
            joke (str): The joke to validate.
            max_length (int, optional): Maximum allowed joke length. 
                                        Defaults to 280.

        Returns:
            bool: True if joke is valid, False otherwise.
        """
        if not joke:
            return False
        
        # Check joke length
        if len(joke) > max_length:
            return False
        
        # Simple profanity check (can be expanded)
        banned_words = ['bad word', 'offensive term']
        return not any(word.lower() in joke.lower() for word in banned_words)