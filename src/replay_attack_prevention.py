import hashlib
import time
from typing import Dict, Any, Optional


class ReplayAttackPreventionLogger:
    """
    A class to prevent replay attacks by tracking and logging unique request signatures.
    
    This class maintains a record of recent request signatures and their timestamps 
    to detect and prevent replay attacks by rejecting duplicate requests within a 
    specified time window.
    """
    
    def __init__(self, max_history_size: int = 1000, time_window: int = 300):
        """
        Initialize the Replay Attack Prevention Logger.
        
        Args:
            max_history_size (int, optional): Maximum number of request signatures to keep. 
                Defaults to 1000.
            time_window (int, optional): Time window in seconds where a request is considered 
                a potential replay attack. Defaults to 300 (5 minutes).
        """
        self._request_history: Dict[str, float] = {}
        self._max_history_size = max_history_size
        self._time_window = time_window
    
    def _generate_signature(self, request_data: Dict[Any, Any]) -> str:
        """
        Generate a unique signature for a request.
        
        Args:
            request_data (Dict[Any, Any]): The request data to be hashed.
        
        Returns:
            str: A unique hash signature of the request.
        """
        # Sort the dictionary to ensure consistent hashing
        sorted_data = str(sorted(request_data.items()))
        return hashlib.sha256(sorted_data.encode()).hexdigest()
    
    def is_replay_attack(self, request_data: Dict[Any, Any]) -> bool:
        """
        Check if the current request is a potential replay attack.
        
        Args:
            request_data (Dict[Any, Any]): The request data to check.
        
        Returns:
            bool: True if the request is a potential replay attack, False otherwise.
        """
        current_time = time.time()
        signature = self._generate_signature(request_data)
        
        # Clean up old entries
        self._clean_history(current_time)
        
        # Check if signature exists and is within time window
        if signature in self._request_history:
            if current_time - self._request_history[signature] < self._time_window:
                return True
        
        # Store the new request signature
        self._request_history[signature] = current_time
        return False
    
    def _clean_history(self, current_time: float) -> None:
        """
        Remove old entries from the request history.
        
        Args:
            current_time (float): Current timestamp.
        """
        # Remove entries older than time window
        self._request_history = {
            k: v for k, v in self._request_history.items() 
            if current_time - v < self._time_window
        }
        
        # Trim history if it exceeds max size
        if len(self._request_history) > self._max_history_size:
            sorted_entries = sorted(
                self._request_history.items(), 
                key=lambda x: x[1]
            )
            excess = len(self._request_history) - self._max_history_size
            for signature, _ in sorted_entries[:excess]:
                del self._request_history[signature]