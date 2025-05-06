"""Client-Side Signature Generation Library.

This module provides utilities for generating cryptographically signed messages
using PyNaCl's signing capabilities.
"""

import base58
import json
import nacl.signing
from typing import Dict, Any, Optional, Union


class SignatureGenerator:
    """A utility class for generating and managing cryptographic signatures."""

    def __init__(self, private_key: Optional[str] = None):
        """
        Initialize a SignatureGenerator with an optional private key.

        Args:
            private_key (str, optional): Base58 encoded private key. 
                If not provided, a new key pair will be generated.
        """
        if private_key:
            # Decode the base58 private key
            private_key_bytes = base58.b58decode(private_key)
            self.signing_key = nacl.signing.SigningKey(private_key_bytes)
        else:
            # Generate a new key pair
            self.signing_key = nacl.signing.SigningKey.generate()

        # Get the corresponding public key
        self.verify_key = self.signing_key.verify_key

    def get_public_key(self, encoding: str = 'base58') -> str:
        """
        Retrieve the public key associated with the signing key.

        Args:
            encoding (str, optional): Encoding format for the public key. 
                Currently supports 'base58'. Defaults to 'base58'.

        Returns:
            str: The public key in the specified encoding
        """
        if encoding == 'base58':
            return base58.b58encode(bytes(self.verify_key)).decode('utf-8')
        else:
            raise ValueError(f"Unsupported encoding: {encoding}")

    def sign_message(self, message: Union[str, Dict[Any, Any]], encoding: str = 'base58') -> str:
        """
        Generate a signed message with the current signing key.

        Args:
            message (str or dict): The message to sign. If a dict, will be JSON serialized.
            encoding (str, optional): Encoding for the signed message. Defaults to 'base58'.

        Returns:
            str: The signed message in the specified encoding
        """
        # Convert dict to JSON string if needed
        if isinstance(message, dict):
            message = json.dumps(message)

        # Convert message to bytes
        message_bytes = message.encode('utf-8')

        # Sign the message
        signed_message = self.signing_key.sign(message_bytes)

        # Encode based on encoding parameter
        if encoding == 'base58':
            return base58.b58encode(bytes(signed_message)).decode('utf-8')
        else:
            raise ValueError(f"Unsupported encoding: {encoding}")