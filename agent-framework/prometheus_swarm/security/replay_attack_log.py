import time
import hashlib
import threading
from typing import Dict, Any

class ReplayAttackLogger:
    """
    A logging model to prevent replay attacks by tracking and validating request uniqueness.
    
    This class provides mechanisms to:
    - Track unique request signatures
    - Prevent replay of previously seen requests
    - Automatically clean up old request records
    - Thread-safe request tracking
    """
    
    def __init__(self, retention_time: int = 300, cleanup_interval: int = 60):
        """
        Initialize the Replay Attack Logger.
        
        Args:
            retention_time (int): Time in seconds to keep request records. Defaults to 5 minutes.
            cleanup_interval (int): Interval between cleanup operations. Defaults to 1 minute.
        """
        self._request_log: Dict[str, float] = {}
        self._lock = threading.Lock()
        self._retention_time = retention_time
        self._cleanup_interval = cleanup_interval
        self._start_cleanup_thread()
    
    def _generate_signature(self, request: Dict[Any, Any]) -> str:
        """
        Generate a unique signature for a request.
        
        Args:
            request (Dict): The request data to generate a signature for.
        
        Returns:
            str: A cryptographic hash representing the request.
        """
        # Convert request to a sorted, consistent string representation
        request_str = str(sorted(request.items()))
        return hashlib.sha256(request_str.encode()).hexdigest()
    
    def log_request(self, request: Dict[Any, Any]) -> bool:
        """
        Log a request and check for potential replay attack.
        
        Args:
            request (Dict): The request to log and validate.
        
        Returns:
            bool: True if request is unique and not a replay, False otherwise.
        """
        signature = self._generate_signature(request)
        current_time = time.time()
        
        with self._lock:
            # Check if request signature exists and is within retention time
            if signature in self._request_log:
                return False
            
            self._request_log[signature] = current_time
            return True
    
    def _cleanup_old_requests(self):
        """
        Remove request signatures older than the retention time.
        This method is thread-safe and runs periodically.
        """
        current_time = time.time()
        with self._lock:
            # Create a new dict with only recent requests
            self._request_log = {
                sig: timestamp 
                for sig, timestamp in self._request_log.items() 
                if current_time - timestamp <= self._retention_time
            }
    
    def _start_cleanup_thread(self):
        """
        Start a background thread to periodically clean up old request records.
        """
        def cleanup_thread():
            while True:
                time.sleep(self._cleanup_interval)
                self._cleanup_old_requests()
        
        thread = threading.Thread(target=cleanup_thread, daemon=True)
        thread.start()