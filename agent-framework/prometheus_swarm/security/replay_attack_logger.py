import time
import hashlib
import threading
from typing import Dict, Any, Optional

class ReplayAttackLogger:
    """
    A thread-safe logging model to prevent replay attacks by tracking 
    and validating unique request signatures.
    """
    def __init__(self, ttl: int = 300, max_entries: int = 1000):
        """
        Initialize the Replay Attack Logger.

        Args:
            ttl (int): Time-to-live for each log entry in seconds. Defaults to 5 minutes.
            max_entries (int): Maximum number of entries to store before pruning. Defaults to 1000.
        """
        self._log: Dict[str, float] = {}
        self._lock = threading.Lock()
        self._ttl = ttl
        self._max_entries = max_entries

    def _generate_signature(self, data: Any) -> str:
        """
        Generate a unique signature for the given data.

        Args:
            data (Any): The data to generate a signature for.

        Returns:
            str: A unique hash signature.
        """
        # Convert data to a string representation
        data_str = str(data)
        
        # Generate a hash using SHA-256
        return hashlib.sha256(data_str.encode()).hexdigest()

    def log_and_validate(self, data: Any) -> bool:
        """
        Log and validate a request to prevent replay attacks.

        Args:
            data (Any): The data to validate.

        Returns:
            bool: True if the request is unique and valid, False if it's a potential replay attack.
        """
        current_time = time.time()
        signature = self._generate_signature(data)

        with self._lock:
            # Remove expired entries
            self._prune_expired_entries(current_time)

            # Check if signature already exists and is not too old
            if signature in self._log and current_time - self._log[signature] <= self._ttl:
                return False

            # Store the new signature with current timestamp
            self._log[signature] = current_time

            # Enforce max entries limit by removing oldest entries
            while len(self._log) > self._max_entries:
                oldest_key = min(self._log, key=self._log.get)
                del self._log[oldest_key]

            return True

    def _prune_expired_entries(self, current_time: float) -> None:
        """
        Remove entries that have exceeded the time-to-live.

        Args:
            current_time (float): Current timestamp.
        """
        expired_keys = [
            key for key, timestamp in self._log.items() 
            if current_time - timestamp > self._ttl
        ]
        
        for key in expired_keys:
            del self._log[key]

    def clear_logs(self) -> None:
        """
        Clear all logged signatures.
        """
        with self._lock:
            self._log.clear()