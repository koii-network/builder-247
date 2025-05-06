"""
Replay Attack Logging Service

This module provides functionality to log and detect potential replay attacks
by tracking unique request signatures and their timestamps.
"""

from typing import Dict, Any
from datetime import datetime, timedelta
import hashlib
import threading

class ReplayAttackLogger:
    """
    A thread-safe service for tracking and preventing replay attacks.

    Attributes:
        _request_cache (Dict[str, Dict[str, Any]]): Cache of recent requests
        _cache_lock (threading.Lock): Lock for thread-safe operations
        _cache_expiration (timedelta): Duration for which request signatures are stored
    """

    def __init__(self, expiration_minutes: int = 5):
        """
        Initialize the Replay Attack Logger.

        Args:
            expiration_minutes (int, optional): How long to keep request signatures. Defaults to 5.
        """
        self._request_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_lock = threading.Lock()
        self._cache_expiration = timedelta(minutes=expiration_minutes)

    def _generate_signature(self, request_data: Dict[str, Any]) -> str:
        """
        Generate a unique signature for a request.

        Args:
            request_data (Dict[str, Any]): Request data to generate signature for.

        Returns:
            str: A unique hash signature for the request.
        """
        # Deterministically sort the dictionary to ensure consistent hashing
        sorted_data = str(sorted(request_data.items()))
        return hashlib.sha256(sorted_data.encode()).hexdigest()

    def log_request(self, request_data: Dict[str, Any]) -> bool:
        """
        Log a request and check if it's a potential replay attack.

        Args:
            request_data (Dict[str, Any]): Request data to log.

        Returns:
            bool: False if request appears to be a replay attack, True otherwise.
        """
        signature = self._generate_signature(request_data)
        current_time = datetime.now()

        with self._cache_lock:
            # Clean up expired entries
            self._request_cache = {
                sig: entry for sig, entry in self._request_cache.items()
                if current_time - entry['timestamp'] < self._cache_expiration
            }

            # Check if signature already exists
            if signature in self._request_cache:
                return False

            # Log the new request
            self._request_cache[signature] = {
                'timestamp': current_time,
                'data': request_data
            }

            return True

    def get_request_log(self) -> Dict[str, Any]:
        """
        Retrieve the current request log.

        Returns:
            Dict[str, Any]: A copy of the current request cache.
        """
        with self._cache_lock:
            return dict(self._request_cache)

    def clear_cache(self):
        """
        Manually clear the request cache.
        """
        with self._cache_lock:
            self._request_cache.clear()