import hashlib
import time
from typing import Dict, Any, Optional

class ReplayAttackLogger:
    """
    A service to detect and log potential replay attacks by tracking request signatures.
    
    Replay attacks involve malicious actors repeating a valid data transmission,
    potentially causing unauthorized actions or system abuse.
    """
    
    def __init__(self, max_cache_size: int = 1000, expiration_time: int = 300):
        """
        Initialize the Replay Attack Logger.
        
        Args:
            max_cache_size (int): Maximum number of recent requests to track
            expiration_time (int): Time in seconds after which a request signature expires
        """
        self._request_cache: Dict[str, float] = {}
        self._max_cache_size = max_cache_size
        self._expiration_time = expiration_time
    
    def _generate_signature(self, request_data: Dict[Any, Any]) -> str:
        """
        Generate a unique signature for a request to detect potential replays.
        
        Args:
            request_data (Dict[Any, Any]): The request data to create a signature for
        
        Returns:
            str: A cryptographic hash of the request data
        """
        # Convert request data to a sorted, consistent string representation
        data_str = str(sorted(request_data.items()))
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def is_replay(self, request_data: Dict[Any, Any]) -> bool:
        """
        Check if the current request appears to be a replay of a recent request.
        
        Args:
            request_data (Dict[Any, Any]): The request data to check
        
        Returns:
            bool: True if the request is a potential replay, False otherwise
        """
        current_time = time.time()
        signature = self._generate_signature(request_data)
        
        # Clean up expired entries
        self._clean_expired_entries(current_time)
        
        # Check if signature exists in recent requests
        if signature in self._request_cache:
            return True
        
        # Store the new signature
        self._add_signature(signature, current_time)
        return False
    
    def _clean_expired_entries(self, current_time: float) -> None:
        """
        Remove entries from the cache that have expired.
        
        Args:
            current_time (float): Current timestamp
        """
        expired_keys = [
            key for key, timestamp in self._request_cache.items()
            if current_time - timestamp > self._expiration_time
        ]
        
        for key in expired_keys:
            del self._request_cache[key]
    
    def _add_signature(self, signature: str, timestamp: float) -> None:
        """
        Add a signature to the request cache, managing cache size.
        
        Args:
            signature (str): Request signature
            timestamp (float): Timestamp of the request
        """
        # Remove oldest entry if cache is full
        if len(self._request_cache) >= self._max_cache_size:
            oldest_key = min(self._request_cache, key=self._request_cache.get)
            del self._request_cache[oldest_key]
        
        self._request_cache[signature] = timestamp
    
    def get_cache_size(self) -> int:
        """
        Get the current number of cached request signatures.
        
        Returns:
            int: Number of cached request signatures
        """
        return len(self._request_cache)