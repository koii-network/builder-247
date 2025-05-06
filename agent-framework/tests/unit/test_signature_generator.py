import pytest
from prometheus_swarm.signature_generator import ClientSignatureGenerator

def test_generate_uuid():
    """Test UUID generation"""
    uuid1 = ClientSignatureGenerator.generate_uuid()
    uuid2 = ClientSignatureGenerator.generate_uuid()
    
    assert uuid1 != uuid2
    assert len(uuid1) > 0

def test_hash_data():
    """Test data hashing"""
    data = {"key1": "value1", "key2": 42}
    
    # Test default SHA256 hashing
    hash_result = ClientSignatureGenerator.hash_data(data)
    assert len(hash_result) == 64  # SHA256 produces 64-character hex
    assert all(c in '0123456789abcdef' for c in hash_result)

def test_hash_data_with_different_algorithms():
    """Test hashing with different algorithms"""
    data = {"key1": "value1", "key2": 42}
    
    # Test SHA512
    try:
        hash_result_512 = ClientSignatureGenerator.hash_data(data, algorithm='sha512')
        assert len(hash_result_512) == 128
    except ValueError:
        pytest.fail("Failed to hash data with SHA512")

def test_hash_data_invalid_algorithm():
    """Test hashing with an invalid algorithm"""
    data = {"key1": "value1"}
    
    with pytest.raises(ValueError, match="Unsupported hashing algorithm"):
        ClientSignatureGenerator.hash_data(data, algorithm='invalid_algo')

def test_generate_hmac_signature():
    """Test HMAC signature generation"""
    data = {"key1": "value1", "key2": 42}
    secret_key = "test_secret_key"
    
    signature = ClientSignatureGenerator.generate_hmac_signature(data, secret_key)
    
    assert isinstance(signature, str)
    assert len(signature) > 0

def test_verify_signature():
    """Test signature verification"""
    data = {"key1": "value1", "key2": 42}
    secret_key = "test_secret_key"
    
    signature = ClientSignatureGenerator.generate_hmac_signature(data, secret_key)
    
    # Verification of the original signature should pass
    assert ClientSignatureGenerator.verify_signature(data, signature, secret_key)

def test_verify_signature_failure():
    """Test signature verification with incorrect data or key"""
    data = {"key1": "value1", "key2": 42}
    modified_data = {"key1": "value1", "key2": 43}
    secret_key = "test_secret_key"
    wrong_key = "wrong_secret_key"
    
    signature = ClientSignatureGenerator.generate_hmac_signature(data, secret_key)
    
    # Verification should fail with modified data
    assert not ClientSignatureGenerator.verify_signature(modified_data, signature, secret_key)
    
    # Verification should fail with wrong key
    assert not ClientSignatureGenerator.verify_signature(data, signature, wrong_key)

def test_hmac_signature_different_data_order():
    """Ensure signature is consistent regardless of dictionary key order"""
    data1 = {"key1": "value1", "key2": 42}
    data2 = {"key2": 42, "key1": "value1"}
    secret_key = "test_secret_key"
    
    signature1 = ClientSignatureGenerator.generate_hmac_signature(data1, secret_key)
    signature2 = ClientSignatureGenerator.generate_hmac_signature(data2, secret_key)
    
    assert signature1 == signature2