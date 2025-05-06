import time
import hashlib
import threading
from typing import Dict, Optional, Any

class ReplayAttackLogger:
    """
    A utility class to prevent replay attacks by tracking unique request signatures.
    
    This logger maintains a cache of recent request signatures and their timestamps
    to detect and prevent potential replay attacks.
    """
    
    def __init__(self, 
                 cache_size: int = 1000, 
                 expiration_time: int = 300):
        """
        Initialize the replay attack logger.
        
        Args:
            cache_size (int): Maximum number of signatures to store. Defaults to 1000.
            expiration_time (int): Time in seconds after which a signature expires. Defaults to 300 (5 minutes).
        """
        self._cache: Dict[str, float] = {}
        self._cache_lock = threading.Lock()
        self._cache_size = cache_size
        self._expiration_time = expiration_time
    
    def _generate_signature(self, request_data: Any) -> str:
        """
        Generate a unique signature for the request data.
        
        Args:
            request_data (Any): The request data to generate a signature for.
        
        Returns:
            str: A unique hash signature for the request.
        """
        # Convert request_data to a hashable representation
        str_data = str(request_data)
        # Include timestamp to make signature time-dependent
        timestamp = str(int(time.time()))
        
        return hashlib.sha256(f"{str_data}:{timestamp}".encode()).hexdigest()
    
    def log_request(self, request_data: Any) -> str:
        """
        Log a request and check for potential replay attacks.
        
        Args:
            request_data (Any): The request data to log.
        
        Returns:
            str: A unique signature for the request.
        
        Raises:
            ValueError: If the request appears to be a replay attack.
        """
        signature = self._generate_signature(request_data)
        current_time = time.time()
        
        with self._cache_lock:
            # Remove expired signatures
            self._cache = {
                sig: timestamp for sig, timestamp in self._cache.items()
                if current_time - timestamp <= self._expiration_time
            }
            
            # Check if signature exists (potential replay)
            if signature in self._cache:
                raise ValueError("Potential replay attack detected")
            
            # Add new signature
            self._cache[signature] = current_time
            
            # Maintain cache size
            if len(self._cache) > self._cache_size:
                # Remove oldest entries
                oldest_keys = sorted(self._cache, key=self._cache.get)[:len(self._cache) - self._cache_size]
                for key in oldest_keys:
                    del self._cache[key]
            
            return signature
    
    def clear_cache(self):
        """
        Clear the entire signature cache.
        """
        with self._cache_lock:
            self._cache.clear()