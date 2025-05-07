import secrets
import time
from typing import Dict, Any

class WebClientNonceManager:
    """
    A class to manage nonce generation and validation for web clients.
    
    This class provides methods to generate unique, time-limited nonces
    that can be used for security purposes such as preventing replay attacks.
    """
    
    def __init__(self, nonce_expiry_seconds: int = 300):
        """
        Initialize the WebClientNonceManager.
        
        Args:
            nonce_expiry_seconds (int, optional): Time in seconds after which 
                                                  a nonce becomes invalid. 
                                                  Defaults to 300 seconds (5 minutes).
        """
        self._nonce_store: Dict[str, Dict[str, Any]] = {}
        self._nonce_expiry = nonce_expiry_seconds
    
    def generate_nonce(self, client_id: str) -> str:
        """
        Generate a unique nonce for a given client.
        
        Args:
            client_id (str): Unique identifier for the client.
        
        Returns:
            str: A unique nonce string.
        """
        # Generate a cryptographically secure random nonce
        nonce = secrets.token_urlsafe(32)
        
        # Store nonce with timestamp
        self._nonce_store[nonce] = {
            'client_id': client_id,
            'timestamp': time.time()
        }
        
        # Clean up expired nonces
        self._cleanup_expired_nonces()
        
        return nonce
    
    def validate_nonce(self, nonce: str, client_id: str) -> bool:
        """
        Validate a nonce for a specific client.
        
        Args:
            nonce (str): The nonce to validate.
            client_id (str): The client ID associated with the nonce.
        
        Returns:
            bool: True if nonce is valid, False otherwise.
        """
        # Check if nonce exists and belongs to the client
        if nonce not in self._nonce_store:
            return False
        
        stored_nonce_data = self._nonce_store[nonce]
        
        # Check client ID match
        if stored_nonce_data['client_id'] != client_id:
            return False
        
        # Check nonce age
        current_time = time.time()
        nonce_age = current_time - stored_nonce_data['timestamp']
        
        if nonce_age > self._nonce_expiry:
            # Remove expired nonce
            del self._nonce_store[nonce]
            return False
        
        # Remove used nonce to prevent replay attacks
        del self._nonce_store[nonce]
        
        return True
    
    def _cleanup_expired_nonces(self) -> None:
        """
        Remove expired nonces from the storage.
        
        Nonces older than the configured expiry time are removed.
        """
        current_time = time.time()
        expired_nonces = [
            nonce for nonce, data in self._nonce_store.items()
            if current_time - data['timestamp'] > self._nonce_expiry
        ]
        
        for nonce in expired_nonces:
            del self._nonce_store[nonce]