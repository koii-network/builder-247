import time
import hashlib
from typing import Dict, Any, Optional

class ReplayAttackLogger:
    """
    A utility class to prevent replay attacks by tracking and validating unique request signatures.
    
    This class maintains a record of recent request signatures and their timestamps to detect
    and prevent replay attacks by rejecting duplicate or stale requests.
    """
    
    def __init__(self, 
                 max_cache_size: int = 1000, 
                 expiration_time: int = 300):
        """
        Initialize the Replay Attack Logger.
        
        Args:
            max_cache_size (int): Maximum number of unique signatures to store. Defaults to 1000.
            expiration_time (int): Time in seconds after which a signature is considered expired. Defaults to 300 (5 minutes).
        """
        self._signature_cache: Dict[str, float] = {}
        self._max_cache_size = max_cache_size
        self._expiration_time = expiration_time
    
    def generate_signature(self, request_data: Dict[Any, Any]) -> str:
        """
        Generate a unique signature for a given request.
        
        Args:
            request_data (Dict[Any, Any]): Dictionary containing request details.
        
        Returns:
            str: A unique signature hash.
        """
        # Normalize the request data and create a deterministic string representation
        sorted_data = sorted(str(item) for item in request_data.items())
        data_string = "|".join(sorted_data)
        
        # Include current timestamp to make even duplicate requests unique
        current_time = str(time.time())
        signature_input = f"{data_string}|{current_time}"
        
        return hashlib.sha256(signature_input.encode()).hexdigest()
    
    def is_request_unique(self, signature: str) -> bool:
        """
        Check if a request signature is unique and not expired.
        
        Args:
            signature (str): Request signature to validate.
        
        Returns:
            bool: True if the signature is unique and valid, False otherwise.
        """
        current_time = time.time()
        
        # Clean up expired signatures
        self._cleanup_expired_signatures(current_time)
        
        # Check if signature exists and is valid
        if signature in self._signature_cache:
            return False
        
        # Add new signature
        self._add_signature(signature, current_time)
        return True
    
    def _cleanup_expired_signatures(self, current_time: float) -> None:
        """
        Remove signatures that have expired.
        
        Args:
            current_time (float): Current timestamp.
        """
        expired_signatures = [
            sig for sig, timestamp in self._signature_cache.items()
            if current_time - timestamp > self._expiration_time
        ]
        
        for sig in expired_signatures:
            del self._signature_cache[sig]
    
    def _add_signature(self, signature: str, timestamp: Optional[float] = None) -> None:
        """
        Add a new signature to the cache, managing cache size.
        
        Args:
            signature (str): Signature to add.
            timestamp (Optional[float]): Timestamp for the signature. Defaults to current time.
        """
        if timestamp is None:
            timestamp = time.time()
        
        # If cache is full, remove the oldest signature
        if len(self._signature_cache) >= self._max_cache_size:
            oldest_signature = min(self._signature_cache, key=self._signature_cache.get)
            del self._signature_cache[oldest_signature]
        
        self._signature_cache[signature] = timestamp