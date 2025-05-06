import pytest
from prometheus_swarm.utils.signatures import generate_signature, verify_signature

def test_generate_signature_dict():
    """Test signature generation with a dictionary."""
    data = {"key1": "value1", "key2": 2}
    signature = generate_signature(data)
    assert isinstance(signature, str)
    assert len(signature) == 64  # SHA-256 signature length

def test_generate_signature_string():
    """Test signature generation with a string."""
    data = "test string"
    signature = generate_signature(data)
    assert isinstance(signature, str)
    assert len(signature) == 64  # SHA-256 signature length

def test_generate_signature_with_secret_key():
    """Test signature generation with a secret key."""
    data = {"key1": "value1"}
    signature_without_key = generate_signature(data)
    signature_with_key = generate_signature(data, secret_key="mysecret")
    assert signature_without_key != signature_with_key

def test_generate_signature_invalid_input():
    """Test signature generation with invalid input types."""
    with pytest.raises(TypeError):
        generate_signature(123)
    
    with pytest.raises(TypeError):
        generate_signature(None)

def test_verify_signature_valid():
    """Test successful signature verification."""
    data = {"key1": "value1", "key2": 2}
    signature = generate_signature(data)
    assert verify_signature(data, signature) is True

def test_verify_signature_with_secret_key():
    """Test signature verification with a secret key."""
    data = {"key1": "value1"}
    secret_key = "mysecret"
    signature = generate_signature(data, secret_key)
    assert verify_signature(data, signature, secret_key) is True
    assert verify_signature(data, signature) is False
    assert verify_signature(data, signature, "wrong_key") is False

def test_verify_signature_invalid():
    """Test signature verification with modified data."""
    data = {"key1": "value1"}
    signature = generate_signature(data)
    modified_data = {"key1": "value2"}
    assert verify_signature(modified_data, signature) is False

def test_consistent_signature():
    """Test consistent signature generation for the same input."""
    data = {"key1": "value1", "key2": 2}
    signature1 = generate_signature(data)
    signature2 = generate_signature(data)
    assert signature1 == signature2

def test_different_input_order():
    """Test signature consistency with different dictionary key orders."""
    data1 = {"key1": "value1", "key2": 2}
    data2 = {"key2": 2, "key1": "value1"}
    signature1 = generate_signature(data1)
    signature2 = generate_signature(data2)
    assert signature1 == signature2