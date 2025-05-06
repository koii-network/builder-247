import pytest
from src.signature_generator import ClientSignatureGenerator

class TestClientSignatureGenerator:
    def test_generate_signature_basic(self):
        """Test basic signature generation"""
        payload = {"key": "value", "number": 42}
        secret_key = "test_secret"
        signature = ClientSignatureGenerator.generate_signature(payload, secret_key)
        assert signature is not None
        assert isinstance(signature, str)
    
    def test_verify_signature_valid(self):
        """Test signature verification with valid signature"""
        payload = {"key": "value", "number": 42}
        secret_key = "test_secret"
        signature = ClientSignatureGenerator.generate_signature(payload, secret_key)
        
        is_valid = ClientSignatureGenerator.verify_signature(payload, signature, secret_key)
        assert is_valid is True
    
    def test_verify_signature_invalid(self):
        """Test signature verification with invalid signature"""
        payload = {"key": "value", "number": 42}
        wrong_payload = {"key": "different_value"}
        secret_key = "test_secret"
        signature = ClientSignatureGenerator.generate_signature(payload, secret_key)
        
        is_valid = ClientSignatureGenerator.verify_signature(wrong_payload, signature, secret_key)
        assert is_valid is False
    
    def test_signature_different_algorithms(self):
        """Test signature generation with different hash algorithms"""
        payload = {"key": "value", "number": 42}
        secret_key = "test_secret"
        
        # Test SHA256
        signature_256 = ClientSignatureGenerator.generate_signature(
            payload, secret_key, algorithm='sha256'
        )
        assert signature_256 is not None
        
        # Test SHA512
        signature_512 = ClientSignatureGenerator.generate_signature(
            payload, secret_key, algorithm='sha512'
        )
        assert signature_512 is not None
        assert signature_256 != signature_512
    
    def test_invalid_inputs(self):
        """Test error handling for invalid inputs"""
        # Non-dict payload
        with pytest.raises(ValueError):
            ClientSignatureGenerator.generate_signature(
                "not a dict", "secret_key"
            )
        
        # Empty secret key
        with pytest.raises(ValueError):
            ClientSignatureGenerator.generate_signature(
                {"key": "value"}, ""
            )
        
        # Unsupported algorithm
        with pytest.raises(ValueError):
            ClientSignatureGenerator.generate_signature(
                {"key": "value"}, "secret_key", algorithm='md5'
            )
    
    def test_signature_stability(self):
        """Test signature stability for same inputs"""
        payload = {"key": "value", "number": 42}
        secret_key = "test_secret"
        
        signature1 = ClientSignatureGenerator.generate_signature(payload, secret_key)
        signature2 = ClientSignatureGenerator.generate_signature(payload, secret_key)
        
        assert signature1 == signature2
    
    def test_signature_payload_order_invariance(self):
        """Test signature generation is independent of dictionary key order"""
        payload1 = {"a": 1, "b": 2}
        payload2 = {"b": 2, "a": 1}
        secret_key = "test_secret"
        
        signature1 = ClientSignatureGenerator.generate_signature(payload1, secret_key)
        signature2 = ClientSignatureGenerator.generate_signature(payload2, secret_key)
        
        assert signature1 == signature2