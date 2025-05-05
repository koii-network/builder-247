import logging
from typing import List, Optional

class JokeFilter:
    """
    A class to filter and log jokes based on specified criteria.
    
    Attributes:
        logger (logging.Logger): Logger for recording joke filtering events
        blacklist (List[str]): List of words to filter out from jokes
    """
    
    def __init__(self, blacklist: Optional[List[str]] = None):
        """
        Initialize the JokeFilter with an optional blacklist.
        
        Args:
            blacklist (Optional[List[str]], optional): List of words to filter. Defaults to None.
        """
        self.logger = logging.getLogger(__name__)
        self.blacklist = blacklist or []
    
    def filter_joke(self, joke: str) -> Optional[str]:
        """
        Filter a joke based on the blacklist.
        
        Args:
            joke (str): The joke to filter
        
        Returns:
            Optional[str]: The filtered joke, or None if the joke contains blacklisted words
        """
        # Convert joke to lowercase for case-insensitive filtering
        joke_lower = joke.lower()
        
        # Check if any blacklisted word is in the joke
        for word in self.blacklist:
            if word.lower() in joke_lower:
                # Log the filtered joke
                self.logger.warning(f"Joke filtered due to blacklisted word: {word}")
                return None
        
        # If no blacklisted words are found, return the original joke
        self.logger.info(f"Joke passed filtering: {joke}")
        return joke
    
    def add_to_blacklist(self, words: List[str]) -> None:
        """
        Add words to the blacklist.
        
        Args:
            words (List[str]): Words to add to the blacklist
        """
        for word in words:
            if word not in self.blacklist:
                self.blacklist.append(word)
                self.logger.info(f"Added '{word}' to blacklist")
    
    def remove_from_blacklist(self, words: List[str]) -> None:
        """
        Remove words from the blacklist.
        
        Args:
            words (List[str]): Words to remove from the blacklist
        """
        for word in words:
            if word in self.blacklist:
                self.blacklist.remove(word)
                self.logger.info(f"Removed '{word}' from blacklist")