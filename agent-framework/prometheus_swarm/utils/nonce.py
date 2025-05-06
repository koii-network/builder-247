import os
import time
import hashlib
import base64

class NonceError(Exception):
    """Custom exception for nonce-related errors."""
    pass

def generate_nonce(ttl: int = 3600) -> str:
    """
    Generate a secure, time-limited nonce.

    Args:
        ttl (int, optional): Time-to-live in seconds. Defaults to 1 hour.

    Returns:
        str: Base64 encoded nonce string
    """
    # Use os.urandom for cryptographically secure random bytes
    random_bytes = os.urandom(32)
    
    # Include current timestamp to enable time-based validation
    timestamp = int(time.time())
    
    # Create a nonce by combining random bytes and timestamp
    nonce_data = random_bytes + timestamp.to_bytes(8, byteorder='big')
    
    # Hash the nonce data for additional security
    hashed_nonce = hashlib.sha256(nonce_data).digest()
    
    # Base64 encode for safe transmission
    return base64.b64encode(hashed_nonce + timestamp.to_bytes(8, byteorder='big')).decode('utf-8')

def validate_nonce(nonce: str, max_ttl: int = 3600) -> bool:
    """
    Validate a nonce based on its timestamp and max time-to-live.

    Args:
        nonce (str): Base64 encoded nonce to validate
        max_ttl (int, optional): Maximum allowed time-to-live in seconds. Defaults to 1 hour.

    Returns:
        bool: True if nonce is valid, False otherwise

    Raises:
        NonceError: If nonce is malformed or invalid
    """
    try:
        # Validate nonce is base64 and of minimum expected length
        if not nonce or len(nonce) < 44:  # Minimum base64 encoded length
            raise NonceError("Invalid nonce length")
        
        # Decode base64 nonce
        decoded_nonce = base64.b64decode(nonce)
        
        # Validate decoded nonce has enough bytes
        if len(decoded_nonce) < 40:  # hash (32) + timestamp (8)
            raise NonceError("Nonce too short after decoding")
        
        # Extract timestamp (last 8 bytes)
        timestamp_bytes = decoded_nonce[-8:]
        timestamp = int.from_bytes(timestamp_bytes, byteorder='big')
        
        # Check timestamp validity
        current_time = int(time.time())
        if current_time - timestamp > max_ttl:
            return False
        
        return True
    
    except (ValueError, TypeError, base64.binascii.Error) as e:
        raise NonceError(f"Invalid nonce format: {e}")