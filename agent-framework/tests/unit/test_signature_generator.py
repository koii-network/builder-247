"""Unit tests for the SignatureGenerator library."""

import json
import base58
import pytest
import nacl.signing
from prometheus_swarm.utils.signature_generator import SignatureGenerator
from prometheus_swarm.utils.signatures import verify_signature, verify_and_parse_signature


class TestSignatureGenerator:
    def test_initialization_with_default_key(self):
        """Test initializing SignatureGenerator without a specific key."""
        sg = SignatureGenerator()
        assert isinstance(sg.signing_key, nacl.signing.SigningKey)
        assert sg.get_public_key() is not None

    def test_initialization_with_existing_key(self):
        """Test initializing SignatureGenerator with an existing base58 encoded key."""
        # Generate a key and get its base58 representation
        temp_signing_key = nacl.signing.SigningKey.generate()
        base58_key = base58.b58encode(bytes(temp_signing_key)).decode('utf-8')

        sg = SignatureGenerator(base58_key)
        assert isinstance(sg.signing_key, nacl.signing.SigningKey)

    def test_get_public_key(self):
        """Test retrieving the public key in base58 encoding."""
        sg = SignatureGenerator()
        public_key = sg.get_public_key()
        assert isinstance(public_key, str)
        # Ensure it's a valid base58 string that decodes successfully
        assert len(base58.b58decode(public_key)) > 0

    def test_sign_message_string(self):
        """Test signing a string message."""
        sg = SignatureGenerator()
        message = "Hello, world!"
        signature = sg.sign_message(message)
        
        # Verify the signature
        verification = verify_signature(signature, sg.get_public_key())
        assert 'data' in verification
        assert verification['data'] == message

    def test_sign_message_dict(self):
        """Test signing a dictionary message."""
        sg = SignatureGenerator()
        message_dict = {"key": "value", "number": 42}
        signature = sg.sign_message(message_dict)
        
        # Verify the signature
        verification = verify_and_parse_signature(signature, sg.get_public_key())
        assert 'data' in verification
        assert verification['data'] == message_dict

    def test_unsupported_encoding(self):
        """Test that unsupported encoding raises an error."""
        sg = SignatureGenerator()
        with pytest.raises(ValueError):
            sg.sign_message("Test", encoding='unsupported')

    def test_different_instances_have_different_keys(self):
        """Ensure different SignatureGenerator instances have unique keys."""
        sg1 = SignatureGenerator()
        sg2 = SignatureGenerator()
        assert sg1.get_public_key() != sg2.get_public_key()

    def test_verify_signed_message(self):
        """Comprehensive test of signing and verification."""
        sg = SignatureGenerator()
        message = {"task": "example", "value": 100}
        
        # Sign the message
        signature = sg.sign_message(message)
        
        # Verify the signature
        result = verify_and_parse_signature(signature, sg.get_public_key())
        
        assert 'data' in result
        assert result['data'] == message