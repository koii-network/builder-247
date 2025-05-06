import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid
import json

class NonceEventLogger:
    """
    A comprehensive logging utility for tracking and managing nonce-based events.
    
    This class provides robust logging mechanisms for tracking unique events
    with detailed contextual information and nonce tracking.
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
        context: Optional[Dict[str, Any]] = None, 
        severity: str = 'INFO'
    ) -> str:
        """
        Log a comprehensive event with a unique nonce and detailed context.
        
        Args:
            event_type (str): Type or category of the event
            context (dict, optional): Additional contextual information about the event
            severity (str, optional): Logging severity level. Defaults to 'INFO'
        
        Returns:
            str: Unique nonce identifier for the event
        """
        # Generate a unique nonce
        nonce = str(uuid.uuid4())
        
        # Prepare event details
        event_details = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'nonce': nonce,
            'event_type': event_type,
            'severity': severity,
            'context': context or {}
        }
        
        # Log the event based on severity
        log_method = getattr(self.logger, severity.lower(), self.logger.info)
        log_method(json.dumps(event_details))
        
        return nonce
    
    def verify_nonce(self, nonce: Optional[str]) -> bool:
        """
        Verify the format of a nonce.
        
        Args:
            nonce (str, optional): Nonce to verify
        
        Returns:
            bool: Whether the nonce is valid
        """
        if not nonce:
            return False
        
        try:
            uuid.UUID(str(nonce))
            return True
        except (ValueError, TypeError):
            return False