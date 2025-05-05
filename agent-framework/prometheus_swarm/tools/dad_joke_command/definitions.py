from typing import Protocol, Dict, Any

class DadJokeCommandHandler(Protocol):
    """
    Protocol defining the interface for a Dad Joke Command Handler.
    
    This interface ensures that any concrete implementation provides methods
    to handle dad joke-related commands and retrieve dad jokes.
    """
    
    def get_random_joke(self) -> str:
        """
        Retrieve a random dad joke.
        
        Returns:
            str: A random dad joke
        
        Raises:
            Exception: If unable to retrieve a joke
        """
        ...
    
    def tell_joke(self, context: Dict[str, Any] = None) -> str:
        """
        Tell a dad joke, optionally with additional context.
        
        Args:
            context (Dict[str, Any], optional): Additional context for joke telling
        
        Returns:
            str: The dad joke that was told
        
        Raises:
            ValueError: If joke cannot be told under specified context
        """
        ...
    
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
        ...