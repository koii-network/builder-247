import secrets
import time
import base64
import hashlib

def generate_nonce(length=32, include_timestamp=True):
    """
    Generate a cryptographically secure nonce (number used once).
    
    Args:
        length (int, optional): Length of the random bytes. Defaults to 32.
        include_timestamp (bool, optional): Whether to include a timestamp. Defaults to True.
    
    Returns:
        str: A base64 encoded nonce string
    
    Raises:
        ValueError: If length is less than 16 or greater than 64
    """
    # Validate input length
    if length < 16 or length > 64:
        raise ValueError("Nonce length must be between 16 and 64 bytes")
    
    # Generate cryptographically secure random bytes
    random_bytes = secrets.token_bytes(length)
    
    # Optionally include timestamp
    if include_timestamp:
        timestamp = int(time.time()).to_bytes(8, byteorder='big')
        random_bytes = timestamp + random_bytes
    
    # Hash the bytes for additional security
    hashed_nonce = hashlib.sha256(random_bytes).digest()
    
    # Encode as base64 for URL-safe representation
    return base64.urlsafe_b64encode(hashed_nonce).decode('utf-8').rstrip('=')