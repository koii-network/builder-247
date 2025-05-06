import uuid
from typing import Dict, Any
from collections import defaultdict
import threading
import time

class NonceTracker:
    """
    A thread-safe nonce tracking mechanism to prevent replay attacks and ensure unique request processing.
    
    The tracker maintains a record of nonces with configurable expiration and cleanup intervals.
    """
    
    def __init__(self, expiration_time: int = 3600, cleanup_interval: int = 600):
        """
        Initialize the NonceTracker.
        
        :param expiration_time: Time in seconds after which a nonce expires (default: 1 hour)
        :param cleanup_interval: Interval in seconds to clean up expired nonces (default: 10 minutes)
        """
        self._nonces: Dict[str, float] = {}
        self._lock = threading.Lock()
        self._expiration_time = expiration_time
        self._cleanup_interval = cleanup_interval
        self._last_cleanup = time.time()
        
        # Start a background thread for periodic cleanup
        self._cleanup_thread = threading.Thread(target=self._periodic_cleanup, daemon=True)
        self._cleanup_thread.start()
    
    def generate_nonce(self) -> str:
        """
        Generate a unique nonce.
        
        :return: A unique nonce string
        """
        return str(uuid.uuid4())
    
    def track_nonce(self, nonce: str) -> bool:
        """
        Track a nonce and check if it has been used before.
        
        :param nonce: The nonce to track
        :return: True if the nonce is new and can be used, False if already used
        """
        with self._lock:
            # Periodically clean up expired nonces
            current_time = time.time()
            if current_time - self._last_cleanup >= self._cleanup_interval:
                self._cleanup_nonces()
            
            # Check if nonce exists and is not expired
            if nonce in self._nonces:
                return False
            
            # Add new nonce with current timestamp
            self._nonces[nonce] = current_time
            return True
    
    def _cleanup_nonces(self):
        """
        Remove expired nonces from the tracking dictionary.
        """
        current_time = time.time()
        expired_nonces = [
            n for n, timestamp in self._nonces.items() 
            if current_time - timestamp > self._expiration_time
        ]
        
        for nonce in expired_nonces:
            del self._nonces[nonce]
        
        self._last_cleanup = current_time
    
    def _periodic_cleanup(self):
        """
        Background thread for periodic nonce cleanup.
        """
        while True:
            time.sleep(self._cleanup_interval)
            with self._lock:
                self._cleanup_nonces()

# Global singleton instance for easy access
nonce_tracker = NonceTracker()