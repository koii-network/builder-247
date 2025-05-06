import hashlib
import json
from typing import Any, Dict, Union

def generate_signature(data: Union[Dict[str, Any], str], secret_key: str = '') -> str:
    """
    Generate a cryptographic signature for a given data object.

    Args:
        data (Union[Dict[str, Any], str]): The data to be signed. Can be a dictionary or a JSON-serializable string.
        secret_key (str, optional): A secret key to enhance signature security. Defaults to an empty string.

    Returns:
        str: A hexadecimal SHA-256 signature of the data.

    Raises:
        TypeError: If the input data is not a dictionary or string.
        ValueError: If the input data cannot be serialized to JSON.
    """
    # Validate input type
    if not isinstance(data, (dict, str)):
        raise TypeError("Input data must be a dictionary or a string")

    try:
        # Convert dictionary to sorted JSON string or use the string directly
        if isinstance(data, dict):
            # Use sorting to ensure consistent representation
            serialized_data = json.dumps(data, sort_keys=True)
        else:
            serialized_data = data

        # Combine data with optional secret key
        combined_data = f"{serialized_data}{secret_key}"

        # Generate SHA-256 hash
        signature = hashlib.sha256(combined_data.encode('utf-8')).hexdigest()
        return signature

    except (TypeError, json.JSONDecodeError) as e:
        raise ValueError(f"Unable to serialize data: {e}")

def verify_signature(data: Union[Dict[str, Any], str], signature: str, secret_key: str = '') -> bool:
    """
    Verify the signature of given data.

    Args:
        data (Union[Dict[str, Any], str]): The original data to verify.
        signature (str): The signature to check against.
        secret_key (str, optional): A secret key used during signature generation. Defaults to an empty string.

    Returns:
        bool: True if the signature is valid, False otherwise.
    """
    try:
        generated_signature = generate_signature(data, secret_key)
        return generated_signature == signature
    except Exception:
        return False