import logging
from typing import List, Union

class JokeFilterLogger:
    """
    A logging utility that filters and logs jokes based on specified criteria.
    
    Attributes:
        logger (logging.Logger): A logger instance for handling joke-related logs
        bad_words (List[str]): A list of words to filter out of jokes
    """
    
    def __init__(self, bad_words: Union[List[str], None] = None):
        """
        Initialize the JokeFilterLogger.
        
        Args:
            bad_words (List[str], optional): List of words to filter from jokes. 
                Defaults to None (no filtering).
        """
        self.logger = logging.getLogger('joke_filter_logger')
        self.logger.setLevel(logging.INFO)
        
        # If no bad words provided, use a default list
        self.bad_words = bad_words or ['racist', 'sexist', 'offensive']
    
    def filter_joke(self, joke: str) -> Union[str, None]:
        """
        Filter a joke based on bad words.
        
        Args:
            joke (str): The joke to be filtered
        
        Returns:
            Union[str, None]: Filtered joke if it passes checks, None otherwise
        """
        if not joke or not isinstance(joke, str):
            self.logger.warning(f"Invalid joke input: {joke}")
            return None
        
        # Convert joke to lowercase for case-insensitive filtering
        lowercase_joke = joke.lower()
        
        # Check if any bad words are in the joke
        for bad_word in self.bad_words:
            if bad_word.lower() in lowercase_joke:
                self.logger.warning(f"Joke contains inappropriate word: {bad_word}")
                return None
        
        # If no bad words found, log the joke and return it
        self.logger.info(f"Joke passed filtering: {joke}")
        return joke
    
    def batch_filter_jokes(self, jokes: List[str]) -> List[str]:
        """
        Filter a batch of jokes.
        
        Args:
            jokes (List[str]): List of jokes to filter
        
        Returns:
            List[str]: List of jokes that passed filtering
        """
        if not jokes:
            self.logger.warning("Empty jokes list provided")
            return []
        
        return [joke for joke in (self.filter_joke(joke) for joke in jokes) if joke is not None]