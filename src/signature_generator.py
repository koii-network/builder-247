import hashlib
import json
from typing import Any, Dict, Optional

def generate_signature(data: Dict[str, Any], secret_key: Optional[str] = None) -> str:
    """
    Generate a secure signature for a given dictionary of data.

    Args:
        data (Dict[str, Any]): The input data dictionary to be signed
        secret_key (Optional[str], optional): An optional secret key for additional security. Defaults to None.

    Returns:
        str: A cryptographic signature of the data

    Raises:
        TypeError: If the data is not a dictionary
        ValueError: If the data dictionary is empty
    """
    # Validate input data
    if not isinstance(data, dict):
        raise TypeError("Input data must be a dictionary")
    
    if not data:
        raise ValueError("Input data dictionary cannot be empty")

    # Sort the dictionary to ensure consistent signature generation
    sorted_data = json.dumps(data, sort_keys=True)

    # Create a base signature using SHA-256
    base_signature = hashlib.sha256(sorted_data.encode('utf-8')).hexdigest()

    # If a secret key is provided, add an additional layer of security
    if secret_key:
        salted_signature = hashlib.sha256(
            (base_signature + secret_key).encode('utf-8')
        ).hexdigest()
        return salted_signature

    return base_signature

def verify_signature(data: Dict[str, Any], signature: str, secret_key: Optional[str] = None) -> bool:
    """
    Verify the signature of a given dictionary of data.

    Args:
        data (Dict[str, Any]): The input data dictionary to verify
        signature (str): The signature to validate
        secret_key (Optional[str], optional): An optional secret key used during signature generation

    Returns:
        bool: True if the signature is valid, False otherwise
    """
    try:
        generated_signature = generate_signature(data, secret_key)
        return generated_signature == signature
    except (TypeError, ValueError):
        return False