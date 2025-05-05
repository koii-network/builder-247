"""
Joke Filtering Logging Module

This module provides functionality for logging jokes with optional filtering.
"""

import logging
from typing import List, Optional


class JokeFilterLogger:
    """
    A logger specifically designed for filtering and logging jokes.
    
    Provides methods to log jokes with optional content filtering.
    """

    def __init__(
        self, 
        logger: Optional[logging.Logger] = None, 
        filters: Optional[List[str]] = None
    ):
        """
        Initialize the JokeFilterLogger.
        
        Args:
            logger (Optional[logging.Logger]): Custom logger. 
                If None, creates a default logger.
            filters (Optional[List[str]]): List of filter keywords 
                to exclude from logging.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.filters = filters or []
    
    def is_joke_safe(self, joke: str) -> bool:
        """
        Check if a joke is safe to log based on filter criteria.
        
        Args:
            joke (str): The joke text to evaluate.
        
        Returns:
            bool: True if the joke passes all filters, False otherwise.
        """
        # Convert joke to lowercase for case-insensitive filtering
        joke_lower = joke.lower()
        
        # Check if any filter matches the joke
        for filter_keyword in self.filters:
            if filter_keyword.lower() in joke_lower:
                return False
        
        return True
    
    def log_joke(
        self, 
        joke: str, 
        log_level: int = logging.INFO, 
        log_safe_only: bool = True
    ) -> None:
        """
        Log a joke with optional filtering.
        
        Args:
            joke (str): The joke to log.
            log_level (int): Logging level (default: logging.INFO)
            log_safe_only (bool): Only log jokes that pass filters 
                (default: True)
        
        Raises:
            ValueError: If log_safe_only is True and joke fails filtering.
        """
        if log_safe_only and not self.is_joke_safe(joke):
            raise ValueError("Joke contains filtered content.")
        
        self.logger.log(log_level, joke)
    
    def add_filter(self, filter_keyword: str) -> None:
        """
        Add a new filter keyword.
        
        Args:
            filter_keyword (str): Keyword to filter against.
        """
        self.filters.append(filter_keyword)