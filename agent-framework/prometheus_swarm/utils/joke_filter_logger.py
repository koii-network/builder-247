import logging
import re
from typing import Optional, List, Union

class JokeFilterLogger:
    """
    A custom logger that implements joke filtering and logging capabilities.
    
    This logger allows filtering out jokes based on specified categories, 
    offensive content, or custom filter rules.
    """
    
    def __init__(
        self, 
        logger_name: str = 'joke_filter_logger', 
        log_level: int = logging.INFO,
        blocked_words: Optional[List[str]] = None,
        blocked_categories: Optional[List[str]] = None
    ):
        """
        Initialize the JokeFilterLogger.
        
        Args:
            logger_name (str): Name of the logger. Defaults to 'joke_filter_logger'.
            log_level (int): Logging level. Defaults to logging.INFO.
            blocked_words (List[str], optional): List of words to block in jokes.
            blocked_categories (List[str], optional): List of joke categories to block.
        """
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(log_level)
        
        # Setup handler if not already set
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        self.blocked_words = blocked_words or []
        self.blocked_categories = blocked_categories or []
    
    def is_joke_acceptable(self, joke: str, categories: Optional[List[str]] = None) -> bool:
        """
        Determine if a joke is acceptable based on filtering rules.
        
        Args:
            joke (str): The joke text to evaluate.
            categories (List[str], optional): Categories of the joke.
        
        Returns:
            bool: True if the joke is acceptable, False otherwise.
        """
        # Check categories
        if categories and any(cat in self.blocked_categories for cat in categories):
            return False
        
        # Check blocked words
        if any(word.lower() in joke.lower() for word in self.blocked_words):
            return False
        
        return True
    
    def log_joke(
        self, 
        joke: str, 
        categories: Optional[List[str]] = None, 
        log_level: int = logging.INFO
    ) -> Optional[str]:
        """
        Log a joke after applying filtering rules.
        
        Args:
            joke (str): The joke text to log.
            categories (List[str], optional): Categories of the joke.
            log_level (int): Logging level for the joke. Defaults to logging.INFO.
        
        Returns:
            Optional[str]: The logged joke if acceptable, None otherwise.
        """
        if self.is_joke_acceptable(joke, categories):
            self.logger.log(log_level, joke)
            return joke
        return None
    
    def add_blocked_word(self, word: str) -> None:
        """
        Add a word to the blocked words list.
        
        Args:
            word (str): Word to block in jokes.
        """
        if word not in self.blocked_words:
            self.blocked_words.append(word)
    
    def add_blocked_category(self, category: str) -> None:
        """
        Add a category to the blocked categories list.
        
        Args:
            category (str): Category to block.
        """
        if category not in self.blocked_categories:
            self.blocked_categories.append(category)