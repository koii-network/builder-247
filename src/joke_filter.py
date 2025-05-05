import logging
from typing import List, Optional

class JokeFilter:
    def __init__(self, offensive_words: Optional[List[str]] = None, max_length: Optional[int] = None):
        """
        Initialize a JokeFilter with optional filtering criteria.

        Args:
            offensive_words (List[str], optional): List of words to filter out. Defaults to None.
            max_length (int, optional): Maximum allowed joke length. Defaults to None.
        """
        self.offensive_words = offensive_words or []
        self.max_length = max_length
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def is_joke_appropriate(self, joke: str) -> bool:
        """
        Check if a joke meets filtering criteria.

        Args:
            joke (str): The joke to be checked.

        Returns:
            bool: True if the joke passes all filters, False otherwise.
        """
        # Check if any offensive words are in the joke
        if self.offensive_words:
            for word in self.offensive_words:
                if word.lower() in joke.lower():
                    self.logger.warning(f"Joke contains offensive word: {word}")
                    return False

        # Check joke length if max_length is set
        if self.max_length is not None and len(joke) > self.max_length:
            self.logger.warning(f"Joke exceeds maximum length of {self.max_length}")
            return False

        self.logger.info("Joke passed all filters")
        return True

    def filter_jokes(self, jokes: List[str]) -> List[str]:
        """
        Filter a list of jokes based on the set criteria.

        Args:
            jokes (List[str]): List of jokes to filter.

        Returns:
            List[str]: List of jokes that pass the filtering criteria.
        """
        return [joke for joke in jokes if self.is_joke_appropriate(joke)]