import logging
import time
from typing import Dict, Any, Optional

class DadJokeLogger:
    """
    A specialized logger for tracking Dad Joke interactions and metrics.
    
    This class provides methods to log various events and metrics related to 
    Dad Joke integration, including joke retrieval, generation, and performance.
    """
    
    def __init__(self, logger_name: str = 'dad_joke_logger'):
        """
        Initialize the Dad Joke logger.
        
        Args:
            logger_name (str, optional): Name of the logger. Defaults to 'dad_joke_logger'.
        """
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
        
        # Create console handler if no handlers exist
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # Metrics tracking
        self.metrics: Dict[str, Any] = {
            'total_jokes_retrieved': 0,
            'total_jokes_generated': 0,
            'last_joke_retrieval_time': None,
            'total_retrieval_errors': 0
        }
    
    def log_joke_retrieval(self, joke: Optional[str] = None, source: str = 'default') -> None:
        """
        Log the retrieval of a Dad Joke.
        
        Args:
            joke (str, optional): The retrieved joke. Defaults to None.
            source (str, optional): Source of the joke. Defaults to 'default'.
        """
        self.metrics['total_jokes_retrieved'] += 1
        self.metrics['last_joke_retrieval_time'] = time.time()
        
        if joke:
            self.logger.info(f"Dad Joke retrieved from {source}: {joke}")
        else:
            self.logger.info(f"Dad Joke retrieved from {source}")
    
    def log_joke_generation(self, joke: str, model: str) -> None:
        """
        Log the generation of a Dad Joke.
        
        Args:
            joke (str): The generated joke.
            model (str): The model used for joke generation.
        """
        self.metrics['total_jokes_generated'] += 1
        self.logger.info(f"Dad Joke generated using {model}: {joke}")
    
    def log_retrieval_error(self, error_message: str) -> None:
        """
        Log an error during joke retrieval.
        
        Args:
            error_message (str): Description of the error.
        """
        self.metrics['total_retrieval_errors'] += 1
        self.logger.error(f"Dad Joke Retrieval Error: {error_message}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics for Dad Joke interactions.
        
        Returns:
            Dict[str, Any]: A dictionary of current metrics.
        """
        return self.metrics.copy()
    
    def reset_metrics(self) -> None:
        """
        Reset all metrics to their initial state.
        """
        self.metrics = {
            'total_jokes_retrieved': 0,
            'total_jokes_generated': 0,
            'last_joke_retrieval_time': None,
            'total_retrieval_errors': 0
        }

# Global logger instance
dad_joke_logger = DadJokeLogger()