import hashlib
import json
import base64
import hmac
import uuid
from typing import Dict, Any, Optional

class ClientSignatureGenerator:
    """
    A client-side signature generation library for creating secure, verifiable signatures.
    
    This class provides methods to generate signatures for various data types,
    with support for different signature schemes and optional customization.
    """
    
    @staticmethod
    def generate_uuid() -> str:
        """
        Generate a unique identifier.
        
        Returns:
            str: A unique UUID as a string
        """
        return str(uuid.uuid4())
    
    @staticmethod
    def hash_data(data: Dict[str, Any], algorithm: str = 'sha256') -> str:
        """
        Hash the provided data using the specified algorithm.
        
        Args:
            data (Dict[str, Any]): Data to be hashed
            algorithm (str, optional): Hashing algorithm. Defaults to 'sha256'.
        
        Returns:
            str: Hashed data digest
        
        Raises:
            ValueError: If an unsupported hashing algorithm is provided
        """
        try:
            hash_func = getattr(hashlib, algorithm)
        except AttributeError:
            raise ValueError(f"Unsupported hashing algorithm: {algorithm}")
        
        # Sort the dictionary to ensure consistent serialization
        sorted_data = json.dumps(data, sort_keys=True)
        return hash_func(sorted_data.encode()).hexdigest()
    
    @staticmethod
    def generate_hmac_signature(
        data: Dict[str, Any], 
        secret_key: str, 
        algorithm: str = 'sha256'
    ) -> str:
        """
        Generate an HMAC signature for the provided data.
        
        Args:
            data (Dict[str, Any]): Data to be signed
            secret_key (str): Secret key for HMAC generation
            algorithm (str, optional): HMAC algorithm. Defaults to 'sha256'.
        
        Returns:
            str: Base64 encoded HMAC signature
        
        Raises:
            ValueError: If an unsupported HMAC algorithm is provided
        """
        try:
            hash_func = hashlib.sha256 if algorithm == 'sha256' else getattr(hashlib, f'sha{algorithm}')
        except AttributeError:
            raise ValueError(f"Unsupported HMAC algorithm: {algorithm}")
        
        # Sort the dictionary to ensure consistent serialization
        sorted_data = json.dumps(data, sort_keys=True)
        hmac_obj = hmac.new(secret_key.encode(), sorted_data.encode(), hash_func)
        return base64.b64encode(hmac_obj.digest()).decode()
    
    @staticmethod
    def verify_signature(
        data: Dict[str, Any], 
        signature: str, 
        secret_key: str, 
        algorithm: str = 'sha256'
    ) -> bool:
        """
        Verify the HMAC signature for the provided data.
        
        Args:
            data (Dict[str, Any]): Data to verify
            signature (str): Signature to verify
            secret_key (str): Secret key for signature verification
            algorithm (str, optional): HMAC algorithm. Defaults to 'sha256'.
        
        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            computed_signature = ClientSignatureGenerator.generate_hmac_signature(
                data, secret_key, algorithm
            )
            return hmac.compare_digest(computed_signature, signature)
        except Exception:
            return False