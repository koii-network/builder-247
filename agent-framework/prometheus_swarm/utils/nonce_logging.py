import threading
import time
import uuid
from typing import Dict, Any, Optional

class NonceEventLogger:
    """
    A thread-safe logger for tracking nonce events with comprehensive details.
    
    This class provides methods to log, track, and manage nonce events across 
    different operations with granular tracking and thread safety.
    """
    
    def __init__(self):
        """
        Initialize the NonceEventLogger with thread-safe storage and synchronization.
        """
        self._nonce_events: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def generate_nonce(self) -> str:
        """
        Generate a unique nonce identifier.
        
        Returns:
            str: A unique nonce identifier
        """
        return str(uuid.uuid4())
    
    def log_event(
        self, 
        nonce: str, 
        event_type: str, 
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an event associated with a specific nonce.
        
        Args:
            nonce (str): The unique nonce identifier
            event_type (str): The type of event being logged
            details (Optional[Dict[str, Any]], optional): Additional event details
        """
        with self._lock:
            if nonce not in self._nonce_events:
                self._nonce_events[nonce] = {
                    'events': [],
                    'created_at': time.time()
                }
            
            event_record = {
                'type': event_type,
                'timestamp': time.time(),
                'details': details or {}
            }
            
            self._nonce_events[nonce]['events'].append(event_record)
    
    def get_nonce_events(self, nonce: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve all events for a specific nonce.
        
        Args:
            nonce (str): The nonce identifier to retrieve events for
        
        Returns:
            Optional[Dict[str, Any]]: Nonce event details or None if not found
        """
        with self._lock:
            return self._nonce_events.get(nonce)
    
    def clear_nonce_events(self, nonce: str) -> bool:
        """
        Clear events for a specific nonce.
        
        Args:
            nonce (str): The nonce identifier to clear
        
        Returns:
            bool: True if nonce was found and cleared, False otherwise
        """
        with self._lock:
            if nonce in self._nonce_events:
                del self._nonce_events[nonce]
                return True
            return False
    
    def prune_old_events(self, max_age_seconds: int = 3600) -> int:
        """
        Remove nonce events older than the specified max age.
        
        Args:
            max_age_seconds (int, optional): Maximum age of events in seconds. Defaults to 1 hour.
        
        Returns:
            int: Number of nonce events pruned
        """
        current_time = time.time()
        with self._lock:
            old_nonces = [
                nonce for nonce, event_data in self._nonce_events.items()
                if current_time - event_data['created_at'] > max_age_seconds
            ]
            
            for nonce in old_nonces:
                del self._nonce_events[nonce]
            
            return len(old_nonces)

# Global singleton for easy access
nonce_event_logger = NonceEventLogger()