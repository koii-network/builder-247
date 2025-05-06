import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone

class NonceEventLogger:
    """
    A comprehensive logging utility for tracking nonce-based events
    with detailed contextual information.
    """

    def __init__(self, logger_name: str = 'nonce_event_logger'):
        """
        Initialize the NonceEventLogger with a specific logger.

        Args:
            logger_name (str, optional): Name of the logger. Defaults to 'nonce_event_logger'.
        """
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)

    def log_event(
        self, 
        event_type: str, 
        nonce: Optional[str] = None, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log a comprehensive event with a unique nonce.

        Args:
            event_type (str): Type of event being logged.
            nonce (str, optional): Existing nonce. If not provided, a new one is generated.
            context (dict, optional): Additional context for the event.

        Returns:
            str: The nonce associated with the event.
        """
        if nonce is None:
            nonce = str(uuid.uuid4())

        event_data = {
            'nonce': nonce,
            'event_type': event_type,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'context': context or {}
        }

        self.logger.info(f"Nonce Event: {event_data}")
        return nonce

    def validate_nonce(self, nonce: str) -> bool:
        """
        Validate the format of a nonce.

        Args:
            nonce (str): Nonce to validate.

        Returns:
            bool: Whether the nonce is valid.
        """
        try:
            uuid.UUID(str(nonce))
            return True
        except ValueError:
            return False