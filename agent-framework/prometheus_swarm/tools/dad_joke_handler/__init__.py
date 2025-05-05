from typing import Protocol, runtime_checkable

@runtime_checkable
class DadJokeCommandHandlerProtocol(Protocol):
    """
    Protocol defining the interface for a Dad Joke Command Handler.
    This ensures any implementation can generate and interact with dad jokes.
    """

    def get_random_joke(self) -> str:
        """
        Retrieve a random dad joke.

        Returns:
            str: A dad joke string
        
        Raises:
            RuntimeError: If joke retrieval fails
        """
        ...

    def get_joke_by_category(self, category: str) -> str:
        """
        Retrieve a dad joke from a specific category.

        Args:
            category (str): The joke category

        Returns:
            str: A dad joke from the specified category
        
        Raises:
            ValueError: If the category is invalid
            RuntimeError: If joke retrieval fails
        """
        ...

    def rate_joke(self, joke: str, rating: int) -> bool:
        """
        Rate a dad joke.

        Args:
            joke (str): The joke to rate
            rating (int): Rating value (e.g., 1-5)

        Returns:
            bool: Whether the rating was successfully recorded
        
        Raises:
            ValueError: If rating is out of valid range
        """
        ...