import pytest
from prometheus_swarm.utils.client_signature import ClientSignatureGenerator


def test_signature_generation():
    """Test basic signature generation."""
    generator = ClientSignatureGenerator()
    payload = {"user": "test", "action": "login"}
    
    # Generate signature
    signature = generator.generate_signature(payload)
    assert signature is not None
    assert isinstance(signature, str)
    assert len(signature) > 0


def test_signature_verification():
    """Test signature verification."""
    generator = ClientSignatureGenerator()
    payload = {"user": "test", "action": "login"}
    
    # Generate signature
    signature = generator.generate_signature(payload)
    
    # Verify signature
    assert generator.verify_signature(payload, signature) is True


def test_signature_verification_different_payload():
    """Test signature fails for different payload."""
    generator = ClientSignatureGenerator()
    payload1 = {"user": "test", "action": "login"}
    payload2 = {"user": "test", "action": "logout"}
    
    # Generate signature for first payload
    signature = generator.generate_signature(payload1)
    
    # Verify signature fails for second payload
    assert generator.verify_signature(payload2, signature) is False


def test_signature_methods():
    """Test different signature methods."""
    generator = ClientSignatureGenerator()
    payload = {"user": "test", "action": "login"}
    
    # Test HMAC-SHA256 (default)
    hmac_sig = generator.generate_signature(payload, method='hmac-sha256')
    assert generator.verify_signature(payload, hmac_sig, method='hmac-sha256') is True
    
    # Test SHA256
    sha_sig = generator.generate_signature(payload, method='sha256')
    assert generator.verify_signature(payload, sha_sig, method='sha256') is True


def test_signature_unsupported_method():
    """Test unsupported signature method raises ValueError."""
    generator = ClientSignatureGenerator()
    payload = {"user": "test", "action": "login"}
    
    with pytest.raises(ValueError, match="Unsupported signature method"):
        generator.generate_signature(payload, method='unsupported-method')


def test_signature_payload_order_invariance():
    """Test signature is consistent regardless of dictionary key order."""
    generator = ClientSignatureGenerator()
    payload1 = {"a": 1, "b": 2}
    payload2 = {"b": 2, "a": 1}
    
    # Generate signatures for both payloads
    sig1 = generator.generate_signature(payload1)
    sig2 = generator.generate_signature(payload2)
    
    assert sig1 == sig2


def test_custom_secret_key():
    """Test signature generation with a custom secret key."""
    custom_key = 'my_super_secret_key'
    generator = ClientSignatureGenerator(secret_key=custom_key)
    payload = {"user": "test", "action": "login"}
    
    signature = generator.generate_signature(payload)
    assert signature is not None
    assert generator.verify_signature(payload, signature) is True