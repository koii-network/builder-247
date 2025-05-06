import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone

class NonceEventLogger:
    """
    A comprehensive logging utility for tracking nonce events with detailed metadata.
    
    This logger provides a standardized way to log nonce-related events with 
    contextual information, supporting traceability and audit purposes.
    """
    
    def __init__(self, logger_name: str = 'nonce_event_logger'):
        """
        Initialize the NonceEventLogger.
        
        Args:
            logger_name (str, optional): Name of the logger. Defaults to 'nonce_event_logger'.
        """
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
    
    def log_nonce_event(
        self, 
        event_type: str, 
        nonce: Optional[str] = None, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log a comprehensive nonce event with detailed metadata.
        
        Args:
            event_type (str): Type of nonce event (e.g., 'generation', 'validation', 'consumption')
            nonce (str, optional): The nonce value. If not provided, a new UUID will be generated.
            context (Dict[str, Any], optional): Additional context for the event.
        
        Returns:
            str: The logged nonce value
        """
        # Generate nonce if not provided
        if nonce is None:
            nonce = str(uuid.uuid4())
        
        # Prepare event metadata
        event_metadata = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type,
            'nonce': nonce
        }
        
        # Add optional context
        if context:
            event_metadata['context'] = context
        
        # Log the event
        self.logger.info(f"Nonce Event: {event_metadata}")
        
        return nonce
    
    def validate_nonce(
        self, 
        nonce: str, 
        validation_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Validate a nonce, logging the validation attempt.
        
        Args:
            nonce (str): The nonce to validate
            validation_context (Dict[str, Any], optional): Context for validation
        
        Returns:
            bool: Whether the nonce is considered valid
        """
        # Basic validation: check if nonce is a valid UUID
        try:
            uuid.UUID(str(nonce))
            
            # Log validation event
            self.log_nonce_event(
                event_type='validation', 
                nonce=nonce, 
                context={
                    'validation_status': 'valid',
                    **(validation_context or {})
                }
            )
            
            return True
        except ValueError:
            # Log invalid nonce
            self.log_nonce_event(
                event_type='validation', 
                nonce=nonce, 
                context={
                    'validation_status': 'invalid',
                    **(validation_context or {})
                }
            )
            
            return False