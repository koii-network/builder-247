import logging
import re
from typing import List, Optional

class JokeFilterLogger:
    """
    A logger that filters out jokes and logs only serious messages.
    
    Attributes:
        logger (logging.Logger): The underlying logger instance
        joke_patterns (List[str]): List of regex patterns to identify jokes
    """
    
    def __init__(self, 
                 logger_name: str = 'joke_filter_logger', 
                 log_level: int = logging.INFO,
                 joke_patterns: Optional[List[str]] = None):
        """
        Initialize the JokeFilterLogger.
        
        Args:
            logger_name (str): Name of the logger
            log_level (int): Logging level (default: logging.INFO)
            joke_patterns (Optional[List[str]]): Custom joke identification patterns
        """
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(log_level)
        
        # Default joke patterns if none provided
        self.joke_patterns = joke_patterns or [
            r'\bjoke\b',
            r'\bhaha\b',
            r'\blol\b',
            r'\bfunny\b',
            r'[😂🤣]'  # Laughing emojis
        ]
    
    def _is_joke(self, message: str) -> bool:
        """
        Determine if a message is a joke based on predefined patterns.
        
        Args:
            message (str): The message to check
        
        Returns:
            bool: True if the message is identified as a joke, False otherwise
        """
        # Convert message to lowercase for case-insensitive matching
        lower_message = message.lower()
        
        # Check each joke pattern
        return any(re.search(pattern, lower_message) for pattern in self.joke_patterns)
    
    def log(self, level: int, message: str, *args, **kwargs):
        """
        Log a message after filtering out jokes.
        
        Args:
            level (int): Logging level (e.g., logging.INFO)
            message (str): Message to log
            *args: Additional logging arguments
            **kwargs: Additional logging keyword arguments
        """
        if not self._is_joke(message):
            self.logger.log(level, message, *args, **kwargs)
    
    def debug(self, message: str, *args, **kwargs):
        """Log a debug message after joke filtering."""
        self.log(logging.DEBUG, message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log an info message after joke filtering."""
        self.log(logging.INFO, message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log a warning message after joke filtering."""
        self.log(logging.WARNING, message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log an error message after joke filtering."""
        self.log(logging.ERROR, message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log a critical message after joke filtering."""
        self.log(logging.CRITICAL, message, *args, **kwargs)