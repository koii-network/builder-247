"""Dad Joke Integration Logging Module.

This module provides specialized logging for Dad Joke related operations.
"""

from ..utils.logging import logger, log_section, log_key_value, log_error
from typing import Optional, Dict, Any
import time
from datetime import datetime

class DadJokeLogger:
    """Specialized logger for Dad Joke related operations."""

    @staticmethod
    def log_joke_retrieval(
        joke: str,
        source: str,
        retrieval_method: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log details of a joke retrieval.

        Args:
            joke (str): The retrieved joke text
            source (str): Source of the joke (API, database, etc.)
            retrieval_method (str): Method used to retrieve the joke
            metadata (Optional[Dict[str, Any]]): Additional metadata about the joke
        """
        log_section("DAD JOKE RETRIEVAL")
        log_key_value("Timestamp", datetime.now().isoformat())
        log_key_value("Source", source)
        log_key_value("Retrieval Method", retrieval_method)
        log_key_value("Joke Length", len(joke))
        log_key_value("Joke Preview", joke[:50] + "..." if len(joke) > 50 else joke)

        if metadata:
            log_section("JOKE METADATA")
            for key, value in metadata.items():
                log_key_value(key, value)

    @staticmethod
    def log_joke_interaction(
        interaction_type: str,
        joke: str,
        user_response: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log user interaction with a joke.

        Args:
            interaction_type (str): Type of interaction (laugh, share, etc.)
            joke (str): The joke being interacted with
            user_response (Optional[Dict[str, Any]]): User's response details
        """
        log_section("DAD JOKE INTERACTION")
        log_key_value("Interaction Type", interaction_type)
        log_key_value("Joke Length", len(joke))
        log_key_value("Joke Preview", joke[:50] + "..." if len(joke) > 50 else joke)

        if user_response:
            log_section("USER RESPONSE")
            for key, value in user_response.items():
                log_key_value(key, value)

    @staticmethod
    def log_joke_error(
        error: Exception,
        context: str = "Dad Joke Operation",
        joke_details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log errors related to Dad Joke operations.

        Args:
            error (Exception): The exception that occurred
            context (str): Context of the error
            joke_details (Optional[Dict[str, Any]]): Details about the joke when error occurred
        """
        log_error(error, context=context)

        if joke_details:
            log_section("JOKE DETAILS")
            for key, value in joke_details.items():
                log_key_value(key, value)

# Optional: Performance tracking decorator for joke-related functions
def track_joke_performance(func):
    """Decorator to track performance of joke-related functions."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Joke Function {func.__name__} executed in {execution_time:.4f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Joke Function {func.__name__} failed after {execution_time:.4f} seconds")
            raise
    return wrapper