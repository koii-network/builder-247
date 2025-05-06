"""Logging utilities for Prometheus Swarm framework."""

import logging
import traceback
from typing import Optional, Any

from .errors import DuplicateEvidenceError

def setup_logger(name: str = 'prometheus_swarm', level: int = logging.INFO) -> logging.Logger:
    """
    Set up and configure a logger for the Prometheus Swarm framework.
    
    Args:
        name (str, optional): Name of the logger. Defaults to 'prometheus_swarm'.
        level (int, optional): Logging level. Defaults to logging.INFO.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger if not already added
    if not logger.handlers:
        logger.addHandler(console_handler)
    
    return logger

def log_duplicate_evidence(
    evidence_id: Optional[str] = None, 
    context: Optional[dict] = None
) -> None:
    """
    Log details about duplicate evidence with structured information.
    
    Args:
        evidence_id (str, optional): Unique identifier of the duplicate evidence
        context (dict, optional): Additional context about the duplicate evidence
    
    Raises:
        DuplicateEvidenceError: After logging the duplicate evidence details
    """
    logger = setup_logger()
    
    log_message = "Duplicate evidence detected"
    if evidence_id:
        log_message += f" (ID: {evidence_id})"
    
    logger.warning(log_message)
    
    if context:
        for key, value in context.items():
            logger.info(f"Context - {key}: {value}")
    
    # Raise the custom exception with detailed information
    raise DuplicateEvidenceError(
        message=log_message, 
        evidence_id=evidence_id
    )

def handle_evidence_logging(func):
    """
    Decorator to add logging and error handling for evidence processing.
    
    Args:
        func (callable): Function to be decorated
    
    Returns:
        callable: Decorated function with logging and error handling
    """
    def wrapper(*args, **kwargs):
        logger = setup_logger()
        try:
            return func(*args, **kwargs)
        except DuplicateEvidenceError as e:
            logger.error(f"Duplicate Evidence Error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during evidence processing: {e}")
            logger.error(traceback.format_exc())
            raise
    return wrapper