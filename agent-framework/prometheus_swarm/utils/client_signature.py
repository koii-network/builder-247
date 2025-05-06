import hashlib
import json
import base64
import hmac
import secrets
from typing import Dict, Any, Optional


class ClientSignatureGenerator:
    """
    A utility class for generating and verifying client-side signatures.
    
    This class provides methods to:
    - Generate a secure signature for a given payload
    - Verify an existing signature
    - Support different signature methods
    """

    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize the signature generator.
        
        Args:
            secret_key (Optional[str]): A secret key for signature generation. 
                                        If not provided, a secure random key is generated.
        """
        self.secret_key = secret_key or secrets.token_hex(32)

    def generate_signature(self, payload: Dict[Any, Any], method: str = 'hmac-sha256') -> str:
        """
        Generate a signature for the given payload.
        
        Args:
            payload (Dict[Any, Any]): The payload to sign
            method (str, optional): Signature method. Defaults to 'hmac-sha256'
        
        Returns:
            str: Base64 encoded signature
        
        Raises:
            ValueError: If an unsupported signature method is specified
        """
        # Sort and serialize the payload to ensure consistent representation
        sorted_payload = json.dumps(payload, sort_keys=True, separators=(',', ':'))

        if method == 'hmac-sha256':
            # Create HMAC signature using SHA256
            signature = hmac.new(
                key=self.secret_key.encode('utf-8'),
                msg=sorted_payload.encode('utf-8'),
                digestmod=hashlib.sha256
            ).digest()
            
            # Base64 encode the signature
            return base64.b64encode(signature).decode('utf-8')
        
        elif method == 'sha256':
            # Create a simple SHA256 hash
            signature = hashlib.sha256(sorted_payload.encode('utf-8')).digest()
            return base64.b64encode(signature).decode('utf-8')
        
        else:
            raise ValueError(f"Unsupported signature method: {method}")

    def verify_signature(self, payload: Dict[Any, Any], signature: str, method: str = 'hmac-sha256') -> bool:
        """
        Verify the signature for a given payload.
        
        Args:
            payload (Dict[Any, Any]): The payload to verify
            signature (str): The signature to check
            method (str, optional): Signature method. Defaults to 'hmac-sha256'
        
        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            # Regenerate the signature
            generated_signature = self.generate_signature(payload, method)
            
            # Compare signatures
            return secrets.compare_digest(generated_signature, signature)
        
        except Exception:
            return False