"""
Dad Joke Command Handler Interface Module

This module provides a command handler interface for retrieving and managing dad jokes.
"""

from typing import Dict, Any, Optional
import random


class DadJokeCommandHandler:
    """
    A command handler for managing and retrieving dad jokes.
    
    Attributes:
        _jokes (List[str]): A list of dad jokes.
    """

    def __init__(self, initial_jokes: Optional[list[str]] = None):
        """
        Initialize the Dad Joke Command Handler.
        
        Args:
            initial_jokes (Optional[list[str]], optional): 
                A list of initial jokes to populate the joke collection. 
                Defaults to None.
        """
        self._jokes: list[str] = initial_jokes or [
            "I'm afraid for the calendar. Its days are numbered.",
            "I told my wife she was drawing her eyebrows too high. She looked surprised.",
            "Why don't scientists trust atoms? Because they make up everything!",
            "What do you call a fake noodle? An impasta!",
            "Why did the scarecrow win an award? Because he was outstanding in his field!"
        ]

    def get_random_joke(self) -> str:
        """
        Retrieve a random dad joke from the collection.
        
        Returns:
            str: A randomly selected dad joke.
        
        Raises:
            ValueError: If no jokes are available.
        """
        if not self._jokes:
            raise ValueError("No jokes available in the collection.")
        return random.choice(self._jokes)

    def add_joke(self, joke: str) -> bool:
        """
        Add a new joke to the collection.
        
        Args:
            joke (str): The joke to be added.
        
        Returns:
            bool: True if the joke was successfully added, False otherwise.
        
        Raises:
            ValueError: If the joke is empty or None.
        """
        if not joke or not isinstance(joke, str):
            raise ValueError("Joke must be a non-empty string.")
        
        # Prevent duplicate jokes (case-insensitive)
        if any(joke.strip().lower() == existing.strip().lower() for existing in self._jokes):
            return False
        
        self._jokes.append(joke.strip())
        return True

    def remove_joke(self, joke: str) -> bool:
        """
        Remove a specific joke from the collection.
        
        Args:
            joke (str): The joke to be removed.
        
        Returns:
            bool: True if the joke was successfully removed, False if not found.
        """
        try:
            self._jokes.remove(joke)
            return True
        except ValueError:
            return False

    def get_joke_count(self) -> int:
        """
        Get the total number of jokes in the collection.
        
        Returns:
            int: Number of jokes in the collection.
        """
        return len(self._jokes)

    def list_jokes(self) -> list[str]:
        """
        List all jokes in the collection.
        
        Returns:
            list[str]: A copy of all jokes in the collection.
        """
        return self._jokes.copy()

    def handle_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Handle various dad joke related commands.
        
        Args:
            command (str): The command to execute.
            **kwargs: Additional arguments for the command.
        
        Returns:
            Dict[str, Any]: A dictionary containing the result of the command.
        
        Raises:
            ValueError: For invalid commands.
        """
        command = command.lower().strip()
        
        if command == 'random':
            return {
                'success': True, 
                'joke': self.get_random_joke()
            }
        elif command == 'add':
            joke = kwargs.get('joke')
            if not joke:
                raise ValueError("Joke is required for 'add' command")
            return {
                'success': self.add_joke(joke),
                'joke': joke
            }
        elif command == 'remove':
            joke = kwargs.get('joke')
            if not joke:
                raise ValueError("Joke is required for 'remove' command")
            return {
                'success': self.remove_joke(joke),
                'joke': joke
            }
        elif command == 'list':
            return {
                'success': True,
                'jokes': self.list_jokes(),
                'count': self.get_joke_count()
            }
        else:
            raise ValueError(f"Unknown command: {command}")