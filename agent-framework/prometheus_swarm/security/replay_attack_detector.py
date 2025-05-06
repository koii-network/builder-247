import time
from typing import Dict, Any, Optional
from collections import defaultdict


class ReplayAttackDetector:
    """
    A class to detect and prevent replay attacks by tracking request nonces.
    
    Replay attacks occur when a valid data transmission is maliciously repeated or delayed.
    This detector helps mitigate such attacks by tracking unique request identifiers.
    """

    def __init__(self, window_size: int = 300, max_nonces: int = 1000):
        """
        Initialize the Replay Attack Detector.
        
        Args:
            window_size (int): Time window in seconds for nonce validity. Defaults to 5 minutes.
            max_nonces (int): Maximum number of nonces to store before pruning. Defaults to 1000.
        """
        self._nonces: Dict[str, float] = {}
        self._window_size = window_size
        self._max_nonces = max_nonces

    def is_replay_attack(self, nonce: str) -> bool:
        """
        Check if a given nonce represents a replay attack.
        
        Args:
            nonce (str): Unique identifier for the request.
        
        Returns:
            bool: True if this is a replay attack, False otherwise.
        """
        current_time = time.time()
        
        # Prune old nonces first
        self._prune_nonces(current_time)
        
        # Check if nonce has been seen before within the time window
        if nonce in self._nonces:
            return True
        
        # Add the new nonce
        self._nonces[nonce] = current_time
        
        return False

    def _prune_nonces(self, current_time: float) -> None:
        """
        Remove nonces older than the time window and limit total number of nonces.
        
        Args:
            current_time (float): Current timestamp.
        """
        # Remove nonces outside the time window
        self._nonces = {
            nonce: timestamp for nonce, timestamp in self._nonces.items() 
            if current_time - timestamp <= self._window_size
        }
        
        # Limit total number of nonces to max_nonces
        if len(self._nonces) > self._max_nonces:
            # Get the most recent nonces
            sorted_nonces = sorted(
                self._nonces.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:self._max_nonces]
            
            self._nonces = dict(sorted_nonces)