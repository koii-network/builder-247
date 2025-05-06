import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone

class NonceEventLogger:
    """
    A comprehensive logging class for tracking nonce-based events with detailed metadata.
    
    This logger provides enhanced event tracking with unique identifiers, 
    timestamps, and flexible metadata logging.
    """
    
    def __init__(self, logger_name: str = 'nonce_event_logger'):
        """
        Initialize the NonceEventLogger.
        
        Args:
            logger_name (str, optional): Name of the logger. Defaults to 'nonce_event_logger'.
        """
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
    
    def log_event(
        self, 
        event_type: str, 
        description: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log a comprehensive event with a unique nonce.
        
        Args:
            event_type (str): Type of event being logged.
            description (str): Detailed description of the event.
            metadata (dict, optional): Additional event metadata.
        
        Returns:
            str: Unique nonce identifier for the logged event.
        """
        nonce = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        event_data = {
            'nonce': nonce,
            'timestamp': timestamp,
            'event_type': event_type,
            'description': description,
            'metadata': metadata or {}
        }
        
        # Log the event in a structured format
        self.logger.info(str(event_data))
        
        return nonce
    
    def log_error(
        self, 
        error_type: str, 
        error_message: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log an error event with a comprehensive error record.
        
        Args:
            error_type (str): Type of error encountered.
            error_message (str): Detailed error description.
            metadata (dict, optional): Additional error context.
        
        Returns:
            str: Unique nonce identifier for the logged error.
        """
        nonce = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        error_data = {
            'nonce': nonce,
            'timestamp': timestamp,
            'error_type': error_type,
            'error_message': error_message,
            'metadata': metadata or {}
        }
        
        # Log the error with error severity
        self.logger.error(str(error_data))
        
        return nonce

# Create a singleton instance for easy global access
nonce_logger = NonceEventLogger()