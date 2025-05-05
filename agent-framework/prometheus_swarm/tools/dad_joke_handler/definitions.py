"""
Definitions for the Dad Joke Command Handler.

This module defines the interface and type hints for dad joke commands.
"""

from typing import Protocol, Optional, List

class DadJokeHandler(Protocol):
    """
    Protocol defining the interface for dad joke command handling.
    
    This protocol ensures that any implementation provides methods 
    for retrieving and managing dad jokes.
    """

    def get_random_joke(self) -> str:
        """
        Retrieve a random dad joke.
        
        Returns:
            str: A random dad joke
        """
        ...

    def get_joke_by_id(self, joke_id: str) -> Optional[str]:
        """
        Retrieve a specific dad joke by its unique identifier.
        
        Args:
            joke_id (str): Unique identifier for the dad joke
        
        Returns:
            Optional[str]: The dad joke if found, None otherwise
        """
        ...

    def add_joke(self, joke: str) -> str:
        """
        Add a new dad joke to the collection.
        
        Args:
            joke (str): The dad joke to add
        
        Returns:
            str: The unique identifier of the newly added joke
        """
        ...

    def search_jokes(self, query: str) -> List[str]:
        """
        Search for dad jokes matching a given query.
        
        Args:
            query (str): Search term or phrase
        
        Returns:
            List[str]: A list of dad jokes matching the query
        """
        ...

    def delete_joke(self, joke_id: str) -> bool:
        """
        Delete a dad joke by its unique identifier.
        
        Args:
            joke_id (str): Unique identifier of the joke to delete
        
        Returns:
            bool: True if joke was successfully deleted, False otherwise
        """
        ...