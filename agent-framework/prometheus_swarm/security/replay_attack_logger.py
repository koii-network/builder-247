"""
Replay Attack Logging Service

This module provides functionality to detect and log potential replay attacks 
by tracking and validating request signatures and timestamps.
"""

import time
import hashlib
from typing import Dict, Any, Optional
from threading import Lock


class ReplayAttackLogger:
    """
    A thread-safe logger for detecting and preventing replay attacks.
    
    The logger maintains a cache of recently seen request signatures to 
    detect duplicate or replayed requests.
    """
    
    def __init__(self, 
                 max_cache_size: int = 1000, 
                 max_request_age: int = 300):
        """
        Initialize the Replay Attack Logger.
        
        Args:
            max_cache_size (int): Maximum number of unique request signatures to cache.
                Defaults to 1000.
            max_request_age (int): Maximum age of a request signature in seconds.
                Requests older than this will be considered invalid. Defaults to 300 seconds (5 minutes).
        """
        self._request_cache: Dict[str, float] = {}
        self._max_cache_size = max_cache_size
        self._max_request_age = max_request_age
        self._lock = Lock()
    
    def generate_signature(self, request_data: Dict[str, Any]) -> str:
        """
        Generate a unique signature for a request.
        
        Args:
            request_data (Dict[str, Any]): The request data to generate a signature for.
        
        Returns:
            str: A unique signature for the request.
        """
        # Sort the request data and create a consistent string representation
        sorted_data = sorted(str(item) for item in request_data.items())
        signature_str = '|'.join(sorted_data)
        
        # Use SHA-256 to create a unique hash
        return hashlib.sha256(signature_str.encode()).hexdigest()
    
    def log_request(self, request_data: Dict[str, Any]) -> bool:
        """
        Log a request and check for potential replay attacks.
        
        Args:
            request_data (Dict[str, Any]): The request data to log.
        
        Returns:
            bool: True if the request is unique and not a replay, False otherwise.
        """
        current_time = time.time()
        request_signature = self.generate_signature(request_data)
        
        with self._lock:
            # Clean up expired signatures
            self._cleanup_expired_signatures(current_time)
            
            # Check if the signature already exists
            if request_signature in self._request_cache:
                return False
            
            # Add the new signature
            self._request_cache[request_signature] = current_time
            
            # Enforce max cache size
            if len(self._request_cache) > self._max_cache_size:
                oldest_signature = min(
                    self._request_cache, 
                    key=lambda k: self._request_cache[k]
                )
                del self._request_cache[oldest_signature]
            
            return True
    
    def _cleanup_expired_signatures(self, current_time: float) -> None:
        """
        Remove signatures that are older than max_request_age.
        
        Args:
            current_time (float): The current timestamp.
        """
        expired_signatures = [
            sig for sig, timestamp in self._request_cache.items() 
            if current_time - timestamp > self._max_request_age
        ]
        
        for sig in expired_signatures:
            del self._request_cache[sig]