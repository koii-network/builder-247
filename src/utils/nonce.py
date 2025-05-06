import secrets
import time
import hashlib
import base64

def generate_nonce(length: int = 43, include_timestamp: bool = True) -> str:
    """
    Generate a cryptographically secure nonce.

    Args:
        length (int, optional): Length of the nonce. Defaults to 43.
        include_timestamp (bool, optional): Whether to include a timestamp. Defaults to True.

    Returns:
        str: A cryptographically secure nonce as a base64-encoded string.

    Raises:
        ValueError: If length is less than 16 or greater than 128.
    """
    if length < 16 or length > 128:
        raise ValueError("Nonce length must be between 16 and 128 bytes")

    # Calculate raw bytes needed (accounts for base64 encoding)
    raw_length = int(length * 3 / 4)

    # Generate random bytes
    random_bytes = secrets.token_bytes(raw_length)

    # Optionally include timestamp
    if include_timestamp:
        timestamp = str(int(time.time())).encode('utf-8')
        random_bytes += timestamp

    # Hash the bytes to ensure uniformity and prevent timing attacks
    sha256_hash = hashlib.sha256(random_bytes).digest()

    # Base64 encode, remove padding, ensure exact length
    encoded = base64.urlsafe_b64encode(sha256_hash).decode('utf-8').rstrip('=')
    
    # Truncate or pad to match the requested length
    if len(encoded) > length:
        return encoded[:length]
    
    return encoded + '=' * (length - len(encoded))