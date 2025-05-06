import json
import hashlib
import base64
import ecdsa
from typing import Dict, Any, Union

class ClientSignatureError(Exception):
    """Custom exception for client signature errors."""
    pass

def generate_client_signature(
    payload: Union[Dict[str, Any], str], 
    private_key: str
) -> str:
    """
    Generate a client-side digital signature for a given payload.

    Args:
        payload (Union[Dict[str, Any], str]): The payload to sign. 
            Can be a dictionary or a JSON string.
        private_key (str): Private key for signing in PEM format.

    Returns:
        str: Base64 encoded signature

    Raises:
        ClientSignatureError: If there are issues with payload or signing
    """
    try:
        # Normalize payload to a canonical JSON string
        if isinstance(payload, dict):
            payload_str = json.dumps(payload, sort_keys=True)
        elif isinstance(payload, str):
            # Validate if it's a valid JSON string
            json.loads(payload)
            payload_str = payload
        else:
            raise ClientSignatureError("Payload must be a dictionary or JSON string")

        # Hash the payload
        payload_hash = hashlib.sha256(payload_str.encode('utf-8')).digest()

        # Validate private key
        try:
            signing_key = ecdsa.SigningKey.from_pem(private_key.encode('utf-8'))
        except Exception as e:
            raise ClientSignatureError(f"Invalid private key: {str(e)}")

        # Sign the hash
        signature = signing_key.sign(payload_hash)

        # Encode signature to base64
        return base64.b64encode(signature).decode('utf-8')

    except json.JSONDecodeError:
        raise ClientSignatureError("Invalid JSON payload")
    except Exception as e:
        raise ClientSignatureError(f"Signature generation failed: {str(e)}")

def verify_client_signature(
    payload: Union[Dict[str, Any], str], 
    signature: str, 
    public_key: str
) -> bool:
    """
    Verify a client-side digital signature.

    Args:
        payload (Union[Dict[str, Any], str]): The original payload.
        signature (str): Base64 encoded signature.
        public_key (str): Public key for verification in PEM format.

    Returns:
        bool: True if signature is valid, False otherwise
    """
    try:
        # Normalize payload to a canonical JSON string
        if isinstance(payload, dict):
            payload_str = json.dumps(payload, sort_keys=True)
        elif isinstance(payload, str):
            # Validate if it's a valid JSON string
            json.loads(payload)
            payload_str = payload
        else:
            return False

        # Hash the payload
        payload_hash = hashlib.sha256(payload_str.encode('utf-8')).digest()

        # Decode signature
        try:
            signature_bytes = base64.b64decode(signature)
        except Exception:
            return False

        # Validate public key and verify signature
        try:
            verifying_key = ecdsa.VerifyingKey.from_pem(public_key.encode('utf-8'))
            return verifying_key.verify(signature_bytes, payload_hash)
        except Exception:
            return False

    except (json.JSONDecodeError, Exception):
        return False