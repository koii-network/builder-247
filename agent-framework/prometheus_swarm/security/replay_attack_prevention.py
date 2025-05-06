"""
Replay Attack Prevention Configuration Module

This module provides utilities for configuring and managing 
replay attack prevention settings to enhance system security.
"""

import time
from typing import Dict, Any, Optional

class ReplayAttackPreventionConfig:
    def __init__(self, 
                 window_size: int = 300,  # Default 5-minute window
                 max_nonce_cache_size: int = 1000):
        """
        Initialize replay attack prevention configuration.

        Args:
            window_size (int): Time window in seconds for nonce validation
            max_nonce_cache_size (int): Maximum number of nonces to cache
        """
        self._window_size = window_size
        self._max_nonce_cache_size = max_nonce_cache_size
        self._nonce_cache: Dict[str, float] = {}

    def validate_nonce(self, nonce: str) -> bool:
        """
        Validate a nonce to prevent replay attacks.

        Args:
            nonce (str): Unique nonce to validate

        Returns:
            bool: True if nonce is valid, False otherwise
        """
        current_time = time.time()

        # Remove expired nonces
        self._clean_nonce_cache(current_time)

        # Check if nonce already exists
        if nonce in self._nonce_cache:
            return False

        # Add new nonce with current timestamp
        self._add_nonce(nonce, current_time)
        return True

    def _clean_nonce_cache(self, current_time: float) -> None:
        """
        Remove nonces outside the time window.

        Args:
            current_time (float): Current timestamp
        """
        self._nonce_cache = {
            n: timestamp for n, timestamp in self._nonce_cache.items()
            if current_time - timestamp <= self._window_size
        }

    def _add_nonce(self, nonce: str, timestamp: float) -> None:
        """
        Add a nonce to the cache, managing cache size.

        Args:
            nonce (str): Nonce to add
            timestamp (float): Timestamp of nonce
        """
        if len(self._nonce_cache) >= self._max_nonce_cache_size:
            # Remove oldest nonce if cache is full
            oldest_nonce = min(self._nonce_cache, key=self._nonce_cache.get)
            del self._nonce_cache[oldest_nonce]

        self._nonce_cache[nonce] = timestamp

    def get_config(self) -> Dict[str, Any]:
        """
        Retrieve current replay attack prevention configuration.

        Returns:
            Dict[str, Any]: Configuration settings
        """
        return {
            "window_size": self._window_size,
            "max_nonce_cache_size": self._max_nonce_cache_size,
            "current_nonce_count": len(self._nonce_cache)
        }

    def set_window_size(self, window_size: int) -> None:
        """
        Set the time window for nonce validation.

        Args:
            window_size (int): Time window in seconds
        """
        if window_size <= 0:
            raise ValueError("Window size must be a positive integer")
        self._window_size = window_size

    def set_max_nonce_cache_size(self, max_size: int) -> None:
        """
        Set the maximum number of nonces to cache.

        Args:
            max_size (int): Maximum number of nonces
        """
        if max_size <= 0:
            raise ValueError("Cache size must be a positive integer")
        self._max_nonce_cache_size = max_size