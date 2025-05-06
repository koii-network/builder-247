import hashlib
import json
import base64
import hmac
from typing import Dict, Any, Optional

class ClientSignatureGenerator:
    """
    A client-side signature generation library for secure data signing and verification.
    
    This library provides methods to generate signatures for JSON payloads using 
    different algorithms and secret keys.
    """
    
    @staticmethod
    def generate_signature(payload: Dict[Any, Any], 
                            secret_key: str, 
                            algorithm: str = 'sha256') -> str:
        """
        Generate a signature for a given payload using HMAC.
        
        Args:
            payload (Dict[Any, Any]): The data to be signed
            secret_key (str): The secret key used for signing
            algorithm (str, optional): The hash algorithm to use. Defaults to 'sha256'.
        
        Returns:
            str: Base64 encoded signature
        
        Raises:
            ValueError: If payload is not a dictionary or secret key is empty
        """
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a dictionary")
        
        if not secret_key:
            raise ValueError("Secret key cannot be empty")
        
        # Sort the payload to ensure consistent signing
        sorted_payload = json.dumps(payload, sort_keys=True)
        
        # Select hash algorithm
        if algorithm == 'sha256':
            hasher = hashlib.sha256
        elif algorithm == 'sha512':
            hasher = hashlib.sha512
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        
        # Generate signature
        signature = hmac.new(
            key=secret_key.encode('utf-8'), 
            msg=sorted_payload.encode('utf-8'), 
            digestmod=hasher
        )
        
        return base64.b64encode(signature.digest()).decode('utf-8')
    
    @staticmethod
    def verify_signature(payload: Dict[Any, Any], 
                          signature: str, 
                          secret_key: str, 
                          algorithm: str = 'sha256') -> bool:
        """
        Verify the signature of a given payload.
        
        Args:
            payload (Dict[Any, Any]): The data to verify
            signature (str): The signature to verify
            secret_key (str): The secret key used for verification
            algorithm (str, optional): The hash algorithm to use. Defaults to 'sha256'.
        
        Returns:
            bool: True if signature is valid, False otherwise
        
        Raises:
            ValueError: If payload is not a dictionary or inputs are invalid
        """
        try:
            generated_signature = ClientSignatureGenerator.generate_signature(
                payload, secret_key, algorithm
            )
            return hmac.compare_digest(generated_signature, signature)
        except Exception:
            return False