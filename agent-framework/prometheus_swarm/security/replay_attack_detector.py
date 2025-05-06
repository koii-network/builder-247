import time
from typing import Dict, Any

class ReplayAttackDetector:
    """
    A mechanism to detect potential replay attacks by tracking request signatures.
    
    Replay attacks involve malicious actors intercepting and retransmitting 
    valid data transmissions to either replay or delay/replay the original transmission.
    """
    
    def __init__(self, window_seconds: int = 300, max_unique_requests: int = 1000):
        """
        Initialize the replay attack detector.
        
        Args:
            window_seconds (int): Time window for tracking request signatures (default 5 minutes)
            max_unique_requests (int): Maximum number of unique requests to track (prevents memory issues)
        """
        self._request_signatures: Dict[str, float] = {}
        self._window_seconds = window_seconds
        self._max_unique_requests = max_unique_requests
    
    def is_replay_attack(self, signature: str) -> bool:
        """
        Check if a given request signature indicates a potential replay attack.
        
        Args:
            signature (str): A unique identifier for the request
        
        Returns:
            bool: True if likely a replay attack, False otherwise
        """
        if not signature:
            return False
        
        # Clean up old signatures first
        current_time = time.time()
        self._clean_old_signatures(current_time)
        
        # Check if signature already exists within the time window
        if signature in self._request_signatures:
            return True
        
        # Add new signature and prune if necessary
        self._request_signatures[signature] = current_time
        if len(self._request_signatures) > self._max_unique_requests:
            oldest_signature = min(self._request_signatures, key=self._request_signatures.get)
            del self._request_signatures[oldest_signature]
        
        return False
    
    def _clean_old_signatures(self, current_time: float):
        """
        Remove signatures older than the specified time window.
        
        Args:
            current_time (float): Current timestamp
        """
        self._request_signatures = {
            sig: timestamp for sig, timestamp in self._request_signatures.items()
            if current_time - timestamp <= self._window_seconds
        }
    
    def get_signature(self, request: Dict[str, Any]) -> str:
        """
        Generate a unique signature for a request to detect replay attacks.
        
        Args:
            request (Dict[str, Any]): Request data
        
        Returns:
            str: Unique signature for the request
        """
        import hashlib
        import json
        
        # Normalize the request to ensure consistent signatures
        normalized_request = json.dumps(request, sort_keys=True)
        return hashlib.sha256(normalized_request.encode()).hexdigest()