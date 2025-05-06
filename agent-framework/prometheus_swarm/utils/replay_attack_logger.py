import time
import threading
from typing import Dict, Any, Optional

class ReplayAttackLogger:
    """
    A thread-safe utility for detecting and logging potential replay attacks.
    
    This class maintains a record of recent request signatures to prevent replay attacks
    by tracking and rejecting duplicate requests within a specified time window.
    """
    
    def __init__(self, expiration_time: int = 300, max_entries: int = 1000):
        """
        Initialize the Replay Attack Logger.
        
        Args:
            expiration_time (int): Time in seconds after which a request signature expires. Defaults to 5 minutes.
            max_entries (int): Maximum number of entries to keep in the log before pruning. Defaults to 1000.
        """
        self._request_log: Dict[str, float] = {}
        self._lock = threading.Lock()
        self._expiration_time = expiration_time
        self._max_entries = max_entries
    
    def log_request(self, request_signature: str) -> bool:
        """
        Log a request and check if it's a potential replay attack.
        
        Args:
            request_signature (str): A unique signature for the request (e.g., hash of request details)
        
        Returns:
            bool: True if the request is new and can be processed, False if it's a potential replay attack
        
        Raises:
            TypeError: If request_signature is None
        """
        # Explicitly check for None
        if request_signature is None:
            raise TypeError("Request signature cannot be None")
        
        # Convert to string to handle empty strings
        request_signature = str(request_signature)
        
        current_time = time.time()
        
        with self._lock:
            # Prune expired entries
            self._prune_expired_entries(current_time)
            
            # Check if the request signature already exists
            if request_signature in self._request_log:
                return False
            
            # Add new request signature
            self._request_log[request_signature] = current_time
            
            # Ensure we don't exceed max_entries
            if len(self._request_log) > self._max_entries:
                # Remove the oldest entry
                oldest_sig = min(self._request_log, key=self._request_log.get)
                del self._request_log[oldest_sig]
            
            return True
    
    def _prune_expired_entries(self, current_time: float) -> None:
        """
        Remove entries that have expired.
        
        Args:
            current_time (float): Current timestamp
        """
        expired_signatures = [
            sig for sig, timestamp in self._request_log.items() 
            if current_time - timestamp > self._expiration_time
        ]
        
        for sig in expired_signatures:
            del self._request_log[sig]
    
    def clear_log(self) -> None:
        """
        Manually clear the entire request log.
        """
        with self._lock:
            self._request_log.clear()
    
    def get_log_size(self) -> int:
        """
        Get the current number of entries in the log.
        
        Returns:
            int: Number of entries in the log
        """
        with self._lock:
            return len(self._request_log)