"""
Dad Joke Command Handler Module

This module provides an interface for retrieving and handling dad jokes.
"""

import abc
import random
import typing


class DadJokeCommandHandler(abc.ABC):
    """
    Abstract base class for Dad Joke Command Handler.
    
    This interface defines methods for retrieving dad jokes with various specifications.
    """

    @abc.abstractmethod
    def get_random_joke(self) -> str:
        """
        Retrieve a random dad joke.
        
        Returns:
            str: A dad joke string
        
        Raises:
            RuntimeError: If no jokes are available
        """
        pass

    @abc.abstractmethod
    def get_joke_by_category(self, category: str) -> str:
        """
        Retrieve a dad joke from a specific category.
        
        Args:
            category (str): The category of dad joke to retrieve
        
        Returns:
            str: A dad joke from the specified category
        
        Raises:
            ValueError: If the category is invalid
            RuntimeError: If no jokes are available in the category
        """
        pass

    @abc.abstractmethod
    def add_joke(self, joke: str, category: typing.Optional[str] = None) -> bool:
        """
        Add a new dad joke to the collection.
        
        Args:
            joke (str): The dad joke to add
            category (str, optional): Category for the joke. Defaults to None.
        
        Returns:
            bool: True if joke was successfully added, False otherwise
        
        Raises:
            ValueError: If the joke is invalid or already exists
        """
        pass

    @abc.abstractmethod
    def get_joke_categories(self) -> typing.List[str]:
        """
        Retrieve all available joke categories.
        
        Returns:
            List[str]: A list of joke categories
        """
        pass