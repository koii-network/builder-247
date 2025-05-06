import pytest
import json
import base64
import hmac
import hashlib
from src.signature_generator import ClientSignatureGenerator

class TestClientSignatureGenerator:
    def test_generate_hmac_signature_basic(self):
        """Test basic HMAC signature generation"""
        payload = {"key": "value", "number": 42}
        secret_key = "test_secret"
        
        signature = ClientSignatureGenerator.generate_hmac_signature(payload, secret_key)
        
        assert isinstance(signature, str)
        assert len(signature) > 0

    def test_generate_hmac_signature_payload_order(self):
        """Ensure signature is consistent regardless of payload dict order"""
        payload1 = {"a": 1, "b": 2}
        payload2 = {"b": 2, "a": 1}
        secret_key = "test_secret"
        
        sig1 = ClientSignatureGenerator.generate_hmac_signature(payload1, secret_key)
        sig2 = ClientSignatureGenerator.generate_hmac_signature(payload2, secret_key)
        
        assert sig1 == sig2

    def test_generate_hmac_signature_different_algo(self):
        """Test different hash algorithms"""
        payload = {"key": "value"}
        secret_key = "test_secret"
        
        # Test SHA256
        sig_sha256 = ClientSignatureGenerator.generate_hmac_signature(payload, secret_key, 'sha256')
        assert isinstance(sig_sha256, str)
        
        # Test SHA512
        sig_sha512 = ClientSignatureGenerator.generate_hmac_signature(payload, secret_key, 'sha512')
        assert isinstance(sig_sha512, str)
        assert sig_sha256 != sig_sha512

    def test_generate_hmac_signature_invalid_inputs(self):
        """Test error handling for invalid inputs"""
        with pytest.raises(ValueError, match="Payload cannot be None"):
            ClientSignatureGenerator.generate_hmac_signature(None, "secret")
        
        with pytest.raises(ValueError, match="Secret key cannot be empty"):
            ClientSignatureGenerator.generate_hmac_signature({"key": "value"}, "")

        with pytest.raises(ValueError, match="Unsupported hash algorithm"):
            ClientSignatureGenerator.generate_hmac_signature({"key": "value"}, "secret", "invalid_algo")

    def test_verify_signature_valid(self):
        """Test successful signature verification"""
        payload = {"key": "value", "number": 42}
        secret_key = "test_secret"
        
        signature = ClientSignatureGenerator.generate_hmac_signature(payload, secret_key)
        
        # Verify the signature
        is_valid = ClientSignatureGenerator.verify_signature(payload, signature, secret_key)
        assert is_valid

    def test_verify_signature_invalid(self):
        """Test signature verification with tampered payload"""
        payload = {"key": "value", "number": 42}
        tampered_payload = {"key": "value", "number": 43}
        secret_key = "test_secret"
        
        signature = ClientSignatureGenerator.generate_hmac_signature(payload, secret_key)
        
        # Verify with tampered payload should fail
        is_valid = ClientSignatureGenerator.verify_signature(tampered_payload, signature, secret_key)
        assert not is_valid

    def test_generate_random_secret(self):
        """Test random secret generation"""
        secret1 = ClientSignatureGenerator.generate_random_secret()
        secret2 = ClientSignatureGenerator.generate_random_secret()
        
        # Verify base64 encoding and randomness
        assert isinstance(secret1, str)
        assert len(secret1) > 0
        assert secret1 != secret2

        # Optional: test custom length
        custom_length_secret = ClientSignatureGenerator.generate_random_secret(16)
        assert len(base64.b64decode(custom_length_secret)) == 16