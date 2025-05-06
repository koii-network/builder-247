import logging
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional


class NonceEventLogger:
    """
    A comprehensive logger for tracking nonce events with detailed metadata.
    
    This logger provides a structured way to log nonce-related events,
    capturing key details such as event type, timestamp, unique identifier,
    and optional contextual information.
    """

    def __init__(self, logger_name: str = 'nonce_event_logger'):
        """
        Initialize the NonceEventLogger with a specific logger name.
        
        Args:
            logger_name (str, optional): Name of the logger. Defaults to 'nonce_event_logger'.
        """
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)

    def log_event(
        self, 
        event_type: str, 
        metadata: Optional[Dict[str, Any]] = None, 
        level: int = logging.INFO
    ) -> str:
        """
        Log a comprehensive nonce event with structured information.
        
        Args:
            event_type (str): Type of nonce event (e.g., 'generation', 'validation', 'rotation')
            metadata (dict, optional): Additional contextual information about the event
            level (int, optional): Logging level. Defaults to logging.INFO
        
        Returns:
            str: Unique event identifier (nonce)
        
        Raises:
            ValueError: If event_type is empty or invalid
        """
        if not event_type or not isinstance(event_type, str):
            raise ValueError("Event type must be a non-empty string")

        # Generate unique nonce for the event
        nonce = str(uuid.uuid4())

        # Prepare event log dictionary
        event_log = {
            'nonce': nonce,
            'event_type': event_type,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metadata': metadata or {}
        }

        # Log the event as a JSON string
        log_message = json.dumps(event_log)
        self.logger.log(level, log_message)

        return nonce

    def validate_event(self, nonce: str) -> bool:
        """
        Basic nonce validation method to check format and structure.
        
        Args:
            nonce (str): Nonce to validate
        
        Returns:
            bool: Whether the nonce is valid
        """
        try:
            # Attempt to parse the nonce as a UUID
            uuid.UUID(str(nonce))
            return True
        except ValueError:
            return False