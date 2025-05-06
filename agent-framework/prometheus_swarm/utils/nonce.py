import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class NonceError(Exception):
    """Custom exception for nonce-related errors."""
    pass

class NonceManager:
    """
    Manages nonce tracking and validation to prevent replay attacks and ensure request uniqueness.
    
    Attributes:
        _nonce_cache (Dict[str, Dict[str, Any]]): Stores nonce information
        _max_nonce_age (timedelta): Maximum allowed age for a nonce
        _logger (logging.Logger): Logger for nonce-related events
    """
    
    def __init__(self, max_nonce_age_seconds: int = 300):
        """
        Initialize the NonceManager.
        
        Args:
            max_nonce_age_seconds (int, optional): Maximum time a nonce is considered valid. Defaults to 5 minutes.
        """
        self._nonce_cache: Dict[str, Dict[str, Any]] = {}
        self._max_nonce_age = timedelta(seconds=max_nonce_age_seconds)
        self._logger = logging.getLogger(__name__)
    
    def validate_nonce(self, nonce: str, client_id: Optional[str] = None) -> bool:
        """
        Validate a nonce, checking for uniqueness and freshness.
        
        Args:
            nonce (str): The nonce to validate
            client_id (Optional[str], optional): Identifier for the client. Defaults to None.
        
        Raises:
            NonceError: If nonce is invalid or has been used before
        
        Returns:
            bool: True if nonce is valid
        """
        current_time = datetime.now()
        
        # Remove expired nonces
        self._cleanup_expired_nonces(current_time)
        
        # Check if nonce already exists
        if nonce in self._nonce_cache:
            existing_entry = self._nonce_cache[nonce]
            
            # Additional client ID check if provided
            if client_id is not None and existing_entry.get('client_id') != client_id:
                self._logger.warning(f"Nonce mismatch for client. Nonce: {nonce}")
                raise NonceError("Nonce already used by a different client")
            
            self._logger.warning(f"Duplicate nonce detected: {nonce}")
            raise NonceError("Nonce has already been used")
        
        # Store the new nonce
        self._nonce_cache[nonce] = {
            'timestamp': current_time,
            'client_id': client_id
        }
        
        self._logger.info(f"Nonce validated: {nonce}")
        return True
    
    def _cleanup_expired_nonces(self, current_time: datetime) -> None:
        """
        Remove nonces that have exceeded the maximum age.
        
        Args:
            current_time (datetime): Current timestamp
        """
        expired_nonces = [
            nonce for nonce, entry in self._nonce_cache.items()
            if current_time - entry['timestamp'] > self._max_nonce_age
        ]
        
        for nonce in expired_nonces:
            del self._nonce_cache[nonce]
            self._logger.debug(f"Removed expired nonce: {nonce}")