import hashlib
import json
from typing import Any, Dict, Union

def generate_signature(data: Union[Dict[str, Any], str], secret_key: str = '') -> str:
    """
    Generate a cryptographic signature for a given data payload.

    Args:
        data (Union[Dict[str, Any], str]): The data to sign. 
                Can be a dictionary or a string.
        secret_key (str, optional): A secret key for additional security. 
                Defaults to an empty string.

    Returns:
        str: A hexadecimal signature string.

    Raises:
        TypeError: If data is not a dictionary or string.
    """
    # Validate input type
    if not isinstance(data, (dict, str)):
        raise TypeError("Data must be a dictionary or a string")

    # Normalize data to a consistent string representation
    if isinstance(data, dict):
        # Sort the dictionary to ensure consistent string representation
        sorted_data = json.dumps(data, sort_keys=True)
    else:
        sorted_data = str(data)

    # Combine data with secret key
    payload = f"{sorted_data}{secret_key}"

    # Generate SHA-256 hash
    signature = hashlib.sha256(payload.encode('utf-8')).hexdigest()

    return signature

def verify_signature(data: Union[Dict[str, Any], str], 
                     signature: str, 
                     secret_key: str = '') -> bool:
    """
    Verify the signature of a given data payload.

    Args:
        data (Union[Dict[str, Any], str]): The original data.
        signature (str): The signature to verify.
        secret_key (str, optional): The secret key used for signing. 
                Defaults to an empty string.

    Returns:
        bool: True if signature is valid, False otherwise.
    """
    try:
        # Regenerate signature and compare
        generated_signature = generate_signature(data, secret_key)
        return generated_signature == signature
    except Exception:
        return False