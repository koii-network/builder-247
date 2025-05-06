import time
import hashlib
import threading
from typing import Dict, Any, Optional

class ReplayAttackLogger:
    """
    A thread-safe logging model to prevent replay attacks by tracking 
    and detecting duplicate request signatures.
    
    The logger maintains a cache of recent request signatures and their 
    timestamps to prevent the same request from being processed multiple times.
    """
    
    def __init__(self, max_cache_size: int = 1000, expire_time: int = 300):
        """
        Initialize the Replay Attack Logger.
        
        Args:
            max_cache_size (int): Maximum number of unique signatures to store. 
                                  Defaults to 1000.
            expire_time (int): Time in seconds after which a signature expires. 
                               Defaults to 300 seconds (5 minutes).
        """
        self._signature_cache: Dict[str, float] = {}
        self._max_cache_size = max_cache_size
        self._expire_time = expire_time
        self._lock = threading.Lock()
    
    def _clean_expired_signatures(self):
        """
        Remove expired signatures from the cache.
        Caller must hold the lock.
        """
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self._signature_cache.items() 
            if current_time - timestamp > self._expire_time
        ]
        
        for key in expired_keys:
            del self._signature_cache[key]
    
    def generate_signature(self, request_data: Dict[str, Any]) -> str:
        """
        Generate a unique signature for a request to detect duplicates.
        
        Args:
            request_data (Dict[str, Any]): The request data to generate signature for.
        
        Returns:
            str: A unique cryptographic hash of the request data.
        """
        # Sort dictionary to ensure consistent hashing
        sorted_data = str(sorted(request_data.items()))
        return hashlib.sha256(sorted_data.encode()).hexdigest()
    
    def log_and_check_request(self, request_data: Dict[str, Any]) -> bool:
        """
        Log a request and check if it's a potential replay attack.
        
        Args:
            request_data (Dict[str, Any]): The request data to check.
        
        Returns:
            bool: False if the request looks like a replay attack, True otherwise.
        """
        signature = self.generate_signature(request_data)
        current_time = time.time()
        
        with self._lock:
            # Clean expired signatures
            self._clean_expired_signatures()
            
            # Check if signature exists and is recent
            if signature in self._signature_cache:
                return False
            
            # If cache is full, remove oldest entries
            if len(self._signature_cache) >= self._max_cache_size:
                oldest_key = min(self._signature_cache, key=self._signature_cache.get)
                del self._signature_cache[oldest_key]
            
            # Add new signature
            self._signature_cache[signature] = current_time
            
        return True