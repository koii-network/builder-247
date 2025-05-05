"""
Dad Joke Command Handler Interface Module

This module provides a command handler for retrieving and managing dad jokes.
"""

import random
import requests
from typing import Dict, Any, Optional


class DadJokeCommandHandler:
    """
    A command handler class for managing and retrieving dad jokes.
    """

    def __init__(self, api_url: str = "https://icanhazdadjoke.com/"):
        """
        Initialize the Dad Joke Command Handler.

        Args:
            api_url (str): The URL for fetching dad jokes. Defaults to icanhazdadjoke.com.
        """
        self.api_url = api_url
        self.joke_history: list[str] = []

    def get_random_joke(self) -> str:
        """
        Fetch a random dad joke from the API.

        Returns:
            str: A dad joke text.

        Raises:
            RuntimeError: If unable to fetch a joke from the API.
        """
        try:
            headers = {"Accept": "text/plain"}
            response = requests.get(self.api_url, headers=headers)
            response.raise_for_status()
            joke = response.text.strip()
            self.joke_history.append(joke)
            return joke
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch dad joke: {e}")

    def get_joke_history(self, limit: Optional[int] = None) -> list[str]:
        """
        Retrieve the history of dad jokes.

        Args:
            limit (Optional[int]): Maximum number of jokes to return. 
                                   If None, returns all jokes.

        Returns:
            list[str]: List of dad jokes from history.
        """
        return self.joke_history[:limit] if limit is not None else self.joke_history.copy()

    def clear_joke_history(self) -> None:
        """
        Clear the joke history.
        """
        self.joke_history.clear()

    def handle_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Handle different dad joke related commands.

        Args:
            command (str): The command to execute.
            **kwargs: Additional arguments for the command.

        Returns:
            Dict[str, Any]: Result of the command execution.
        """
        command = command.lower().strip()

        if command == "random":
            return {"joke": self.get_random_joke()}
        elif command == "history":
            limit = kwargs.get("limit")
            return {"history": self.get_joke_history(limit)}
        elif command == "clear_history":
            self.clear_joke_history()
            return {"status": "Joke history cleared"}
        else:
            raise ValueError(f"Unknown command: {command}")