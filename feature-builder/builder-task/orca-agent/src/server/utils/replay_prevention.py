import time
import logging
from functools import wraps
from typing import Dict, Any
from flask import request, abort

# Configure logging to prevent sensitive info exposure
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ReplayPreventionError(Exception):
    """Custom exception for replay prevention failures."""
    pass

class ReplayPreventionManager:
    """
    Manages replay prevention for server routes.
    Uses a combination of nonce and timestamp to prevent replay attacks.
    """
    def __init__(self, max_request_age_seconds: int = 300):
        """
        Initialize the replay prevention manager.
        
        :param max_request_age_seconds: Maximum age of a valid request in seconds
        """
        self._used_nonces: Dict[str, float] = {}
        self._max_request_age = max_request_age_seconds

    def validate_request(self, nonce: str, timestamp: float) -> bool:
        """
        Validate a request to prevent replay attacks.
        
        :param nonce: Unique identifier for the request
        :param timestamp: Timestamp of the request
        :return: True if the request is valid, False otherwise
        :raises ReplayPreventionError: If the request is invalid
        """
        current_time = time.time()

        # Log rejection with minimal sensitive information
        def log_rejection(reason: str):
            logger.warning(f"Replay prevention: {reason} | Nonce length: {len(nonce)}")

        # Check timestamp is not too old
        if current_time - timestamp > self._max_request_age:
            log_rejection("Request timestamp is too old")
            raise ReplayPreventionError("Request timestamp is too old")

        # Check if nonce has been used before
        if nonce in self._used_nonces:
            log_rejection("Duplicate request detected")
            raise ReplayPreventionError("Duplicate request detected")

        # Store the nonce
        self._used_nonces[nonce] = current_time

        # Optionally, clean up old nonces
        self._cleanup_nonces(current_time)

        return True

    def _cleanup_nonces(self, current_time: float):
        """
        Remove nonces older than max_request_age.
        
        :param current_time: Current timestamp
        """
        self._used_nonces = {
            k: v for k, v in self._used_nonces.items() 
            if current_time - v <= self._max_request_age
        }

def replay_prevention(max_request_age: int = 300):
    """
    Decorator to add replay prevention to routes.
    
    :param max_request_age: Maximum age of a valid request in seconds
    """
    replay_manager = ReplayPreventionManager(max_request_age)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Require nonce and timestamp in request
            nonce = request.headers.get('X-Request-Nonce')
            timestamp = request.headers.get('X-Request-Timestamp')

            if not nonce or not timestamp:
                logger.warning("Replay prevention: Missing headers")
                abort(400, description="Missing replay prevention headers")

            try:
                timestamp = float(timestamp)
                replay_manager.validate_request(nonce, timestamp)
            except (ValueError, ReplayPreventionError) as e:
                logger.warning(f"Replay prevention violation: {str(e)}")
                abort(403, description=str(e))

            return func(*args, **kwargs)
        return wrapper
    return decorator