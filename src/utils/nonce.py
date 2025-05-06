import secrets
import time
import hashlib
import base64

def generate_nonce(length: int = 32, include_timestamp: bool = True) -> str:
    """
    Generate a cryptographically secure nonce.

    Args:
        length (int, optional): Length of the nonce. Defaults to 32.
        include_timestamp (bool, optional): Whether to include a timestamp. Defaults to True.

    Returns:
        str: A cryptographically secure nonce as a base64-encoded string.

    Raises:
        ValueError: If length is less than 16 or greater than 128.
    """
    if length < 16 or length > 128:
        raise ValueError("Nonce length must be between 16 and 128 bytes")

    # Generate random bytes
    random_bytes = secrets.token_bytes(length // 2)

    # Optionally include timestamp
    if include_timestamp:
        timestamp = str(int(time.time())).encode('utf-8')
        random_bytes += timestamp

    # Hash the bytes to ensure uniformity and prevent timing attacks
    sha256_hash = hashlib.sha256(random_bytes).digest()

    # Base64 encode for URL-safe representation
    return base64.urlsafe_b64encode(sha256_hash[:length]).decode('utf-8').rstrip('=')