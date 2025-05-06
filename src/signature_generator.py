import hashlib
import json
import hmac
import base64
from typing import Dict, Any, Union

class SignatureGenerator:
    """
    A client-side signature generation library for creating secure signatures.
    
    Supports:
    - JSON payload signing
    - HMAC-SHA256 signature generation
    - Base64 encoding of signatures
    """
    
    @staticmethod
    def generate_signature(payload: Union[Dict[Any, Any], str], secret_key: str) -> str:
        """
        Generate a cryptographic signature for a given payload.
        
        Args:
            payload (dict or str): The data to be signed
            secret_key (str): A secret key used for signature generation
        
        Returns:
            str: Base64 encoded signature
        
        Raises:
            TypeError: If payload is not a dictionary or string
            ValueError: If secret key is empty
        """
        if not secret_key:
            raise ValueError("Secret key cannot be empty")
        
        # Normalize payload to a JSON-serialized string
        if isinstance(payload, dict):
            payload_str = json.dumps(payload, sort_keys=True)
        elif isinstance(payload, str):
            payload_str = payload
        else:
            raise TypeError("Payload must be a dictionary or string")
        
        # Create HMAC signature using SHA-256
        signature = hmac.new(
            key=secret_key.encode('utf-8'),
            msg=payload_str.encode('utf-8'),
            digestmod=hashlib.sha256
        )
        
        # Base64 encode the signature
        return base64.b64encode(signature.digest()).decode('utf-8')
    
    @staticmethod
    def verify_signature(payload: Union[Dict[Any, Any], str], 
                          secret_key: str, 
                          expected_signature: str) -> bool:
        """
        Verify the signature of a payload.
        
        Args:
            payload (dict or str): The original data
            secret_key (str): The secret key used for signature generation
            expected_signature (str): The signature to verify against
        
        Returns:
            bool: Whether the signature is valid
        """
        generated_signature = SignatureGenerator.generate_signature(payload, secret_key)
        return hmac.compare_digest(generated_signature, expected_signature)