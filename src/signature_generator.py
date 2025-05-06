import hashlib
import json
import base64
import hmac
import os
from typing import Dict, Any, Optional

class ClientSignatureGenerator:
    """
    A utility class for generating client-side signatures with various options
    for different signature generation methods.
    """

    @staticmethod
    def generate_hmac_signature(
        payload: Dict[str, Any], 
        secret_key: str, 
        hash_algo: str = 'sha256'
    ) -> str:
        """
        Generate an HMAC signature for a given payload.

        Args:
            payload (Dict[str, Any]): The payload to sign
            secret_key (str): The secret key for HMAC signing
            hash_algo (str, optional): Hash algorithm to use. Defaults to 'sha256'.

        Returns:
            str: Base64 encoded HMAC signature

        Raises:
            ValueError: If payload is None or secret key is empty
        """
        if payload is None:
            raise ValueError("Payload cannot be None")
        
        if not secret_key:
            raise ValueError("Secret key cannot be empty")
        
        # Sort and canonicalize the payload to ensure consistent signature
        sorted_payload = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        
        # Select hash algorithm
        if hash_algo == 'sha256':
            digest = hashlib.sha256
        elif hash_algo == 'sha512':
            digest = hashlib.sha512
        else:
            raise ValueError(f"Unsupported hash algorithm: {hash_algo}")
        
        # Generate HMAC signature
        signature = hmac.new(
            key=secret_key.encode('utf-8'), 
            msg=sorted_payload.encode('utf-8'), 
            digestmod=digest
        )
        
        return base64.b64encode(signature.digest()).decode('utf-8')

    @staticmethod
    def verify_signature(
        payload: Dict[str, Any], 
        signature: str, 
        secret_key: str, 
        hash_algo: str = 'sha256'
    ) -> bool:
        """
        Verify a given signature against a payload.

        Args:
            payload (Dict[str, Any]): The payload to verify
            signature (str): The signature to verify
            secret_key (str): The secret key for HMAC verification
            hash_algo (str, optional): Hash algorithm to use. Defaults to 'sha256'.

        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            generated_signature = ClientSignatureGenerator.generate_hmac_signature(
                payload, secret_key, hash_algo
            )
            return hmac.compare_digest(generated_signature, signature)
        except Exception:
            return False

    @staticmethod
    def generate_random_secret(length: int = 32) -> str:
        """
        Generate a cryptographically secure random secret.

        Args:
            length (int, optional): Length of the secret. Defaults to 32.

        Returns:
            str: Base64 encoded random secret
        """
        return base64.b64encode(os.urandom(length)).decode('utf-8')