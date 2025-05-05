import logging
from typing import Dict, Any, Optional

class DadJokeLogger:
    """
    A specialized logger for tracking Dad Joke interactions and performance.
    
    Provides methods to log different stages and details of Dad Joke retrieval,
    generation, and usage across the system.
    """
    
    def __init__(self, logger_name: str = 'dad_joke_logger'):
        """
        Initialize a DadJokeLogger with a specific logger name.
        
        Args:
            logger_name (str, optional): Name of the logger. Defaults to 'dad_joke_logger'.
        """
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
        
        # Ensure a handler is added if not already present
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_joke_retrieval(self, source: str, joke_id: Optional[str] = None) -> None:
        """
        Log the retrieval of a Dad Joke.
        
        Args:
            source (str): Source of the joke (e.g., 'api', 'cache', 'generated')
            joke_id (str, optional): Unique identifier for the joke
        """
        log_details = {
            'event': 'joke_retrieval',
            'source': source
        }
        if joke_id:
            log_details['joke_id'] = joke_id
        
        self.logger.info(f"Dad Joke Retrieved: {log_details}")
    
    def log_joke_generation(self, method: str, generation_time: float) -> None:
        """
        Log the generation of a Dad Joke.
        
        Args:
            method (str): Method used for joke generation
            generation_time (float): Time taken to generate the joke in seconds
        """
        log_details = {
            'event': 'joke_generation',
            'method': method,
            'generation_time_seconds': generation_time
        }
        
        self.logger.info(f"Dad Joke Generated: {log_details}")
    
    def log_joke_usage(self, context: str, additional_info: Optional[Dict[str, Any]] = None) -> None:
        """
        Log the usage of a Dad Joke in a specific context.
        
        Args:
            context (str): Context where the joke was used
            additional_info (dict, optional): Additional metadata about the joke usage
        """
        log_details = {
            'event': 'joke_usage',
            'context': context
        }
        
        if additional_info:
            log_details.update(additional_info)
        
        self.logger.info(f"Dad Joke Used: {log_details}")
    
    def log_joke_error(self, error_type: str, error_message: str) -> None:
        """
        Log errors related to Dad Joke operations.
        
        Args:
            error_type (str): Type of error encountered
            error_message (str): Detailed error description
        """
        log_details = {
            'event': 'joke_error',
            'error_type': error_type,
            'error_message': error_message
        }
        
        self.logger.error(f"Dad Joke Error: {log_details}")