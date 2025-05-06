import hashlib
import time
from typing import Dict, Any, Optional
from threading import Lock


class ReplayAttackLogger:
    """
    A class to prevent replay attacks by tracking and validating request uniqueness.
    
    This logger uses a combination of request hash, timestamp, and optional 
    time-to-live (TTL) to detect and prevent replay attacks.
    """
    
    def __init__(self, max_entries: int = 1000, ttl: float = 300.0):
        """
        Initialize the replay attack logger.
        
        Args:
            max_entries (int): Maximum number of entries to store in memory. 
                Defaults to 1000.
            ttl (float): Time-to-live for each entry in seconds. 
                Defaults to 300 seconds (5 minutes).
        """
        self._entries: Dict[str, float] = {}
        self._max_entries = max_entries
        self._ttl = ttl
        self._lock = Lock()
    
    def _generate_hash(self, request: Dict[str, Any]) -> str:
        """
        Generate a unique hash for a given request.
        
        Args:
            request (Dict[str, Any]): Request data to hash.
        
        Returns:
            str: A unique hash representation of the request.
        """
        # Sort dict to ensure consistent hashing
        sorted_request = str(sorted(request.items()))
        return hashlib.sha256(sorted_request.encode()).hexdigest()
    
    def check_and_log(self, request: Dict[str, Any]) -> bool:
        """
        Check if a request is a potential replay attack.
        
        Args:
            request (Dict[str, Any]): Request data to check.
        
        Returns:
            bool: False if the request is a potential replay attack, 
                  True if the request is unique and logged.
        """
        current_time = time.time()
        request_hash = self._generate_hash(request)
        
        with self._lock:
            # Clean up expired entries
            self._entries = {
                k: v for k, v in self._entries.items() 
                if current_time - v <= self._ttl
            }
            
            # Check if hash already exists
            if request_hash in self._entries:
                return False
            
            # Limit the number of entries
            if len(self._entries) >= self._max_entries:
                # Remove the oldest entry
                oldest_key = min(self._entries, key=self._entries.get)
                del self._entries[oldest_key]
            
            # Log the new request
            self._entries[request_hash] = current_time
            return True
    
    def get_entry_count(self) -> int:
        """
        Get the current number of entries in the logger.
        
        Returns:
            int: Number of current entries.
        """
        return len(self._entries)