import secrets
import time
import base64
import hashlib
import struct

class NonceService:
    """
    A service for generating secure and unique nonces.
    
    Nonces are one-time tokens used to prevent replay attacks and ensure 
    request uniqueness. This implementation provides cryptographically 
    secure nonce generation with optional expiration.
    """
    
    @staticmethod
    def generate_nonce(length: int = 32, timestamp: float = None) -> str:
        """
        Generate a cryptographically secure nonce.
        
        Args:
            length (int, optional): Length of the nonce in bytes. Defaults to 32.
            timestamp (float, optional): Timestamp to include in nonce. Defaults to current time.
        
        Returns:
            str: Base64 encoded nonce string
        
        Raises:
            ValueError: If length is less than 16 or greater than 64
        """
        if length < 16 or length > 64:
            raise ValueError("Nonce length must be between 16 and 64 bytes")
        
        # Use secrets module for cryptographic randomness
        random_bytes = secrets.token_bytes(length)
        
        # Include timestamp for additional uniqueness
        timestamp = timestamp or time.time()
        # Convert timestamp to bytes
        timestamp_bytes = struct.pack('d', timestamp)
        
        # Create a combined hash for increased entropy
        combined = random_bytes + timestamp_bytes
        nonce_hash = hashlib.sha256(combined).digest()
        
        # Base64 encode for safe string representation
        return base64.urlsafe_b64encode(nonce_hash).decode('utf-8').rstrip('=')
    
    @staticmethod
    def validate_nonce(nonce: str, max_age: float = 3600) -> bool:
        """
        Validate a nonce's integrity and check for expiration.
        
        Args:
            nonce (str): Nonce to validate
            max_age (float, optional): Maximum age of nonce in seconds. Defaults to 1 hour.
        
        Returns:
            bool: True if nonce is valid and not expired, False otherwise
        """
        try:
            # Pad the base64 string if needed
            nonce += '=' * (4 - len(nonce) % 4)
            decoded_nonce = base64.urlsafe_b64decode(nonce.encode('utf-8'))
            
            # Extract timestamp from the end of the decoded nonce
            timestamp_bytes = decoded_nonce[-8:]
            nonce_timestamp = struct.unpack('d', timestamp_bytes)[0]
            
            # Check timestamp
            current_time = time.time()
            return (current_time - nonce_timestamp) <= max_age
        
        except (ValueError, TypeError, struct.error):
            return False