from typing import Dict, Any

class DadJokeCommand:
    """
    Represents a Dad Joke command with method definitions.
    """
    def get_dad_joke(self) -> Dict[str, Any]:
        """
        Define the interface for retrieving a dad joke.
        
        Returns:
            Dict[str, Any]: A dictionary containing dad joke details.
        """
        raise NotImplementedError("Dad joke retrieval method must be implemented.")