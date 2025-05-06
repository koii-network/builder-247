import pytest
import json
from src.signature_generator import SignatureGenerator

class TestSignatureGenerator:
    def test_generate_signature_with_dict(self):
        """Test signature generation with a dictionary payload"""
        payload = {"key1": "value1", "key2": "value2"}
        secret_key = "test_secret"
        signature = SignatureGenerator.generate_signature(payload, secret_key)
        
        assert signature is not None
        assert isinstance(signature, str)
        assert len(signature) > 0
    
    def test_generate_signature_with_string(self):
        """Test signature generation with a string payload"""
        payload = "test payload"
        secret_key = "test_secret"
        signature = SignatureGenerator.generate_signature(payload, secret_key)
        
        assert signature is not None
        assert isinstance(signature, str)
        assert len(signature) > 0
    
    def test_signature_verification_success(self):
        """Test successful signature verification"""
        payload = {"key1": "value1", "key2": "value2"}
        secret_key = "test_secret"
        signature = SignatureGenerator.generate_signature(payload, secret_key)
        
        is_valid = SignatureGenerator.verify_signature(payload, secret_key, signature)
        assert is_valid is True
    
    def test_signature_verification_failure(self):
        """Test signature verification failure"""
        payload = {"key1": "value1", "key2": "value2"}
        secret_key = "test_secret"
        wrong_key = "wrong_secret"
        signature = SignatureGenerator.generate_signature(payload, secret_key)
        
        is_valid = SignatureGenerator.verify_signature(payload, wrong_key, signature)
        assert is_valid is False
    
    def test_signature_order_independence(self):
        """Test that signature is independent of dictionary key order"""
        payload1 = {"key1": "value1", "key2": "value2"}
        payload2 = {"key2": "value2", "key1": "value1"}
        secret_key = "test_secret"
        
        signature1 = SignatureGenerator.generate_signature(payload1, secret_key)
        signature2 = SignatureGenerator.generate_signature(payload2, secret_key)
        
        assert signature1 == signature2
    
    def test_empty_secret_key_raises_error(self):
        """Test that empty secret key raises a ValueError"""
        payload = {"key": "value"}
        with pytest.raises(ValueError, match="Secret key cannot be empty"):
            SignatureGenerator.generate_signature(payload, "")
    
    def test_invalid_payload_type_raises_error(self):
        """Test that invalid payload type raises a TypeError"""
        secret_key = "test_secret"
        with pytest.raises(TypeError, match="Payload must be a dictionary or string"):
            SignatureGenerator.generate_signature(123, secret_key)