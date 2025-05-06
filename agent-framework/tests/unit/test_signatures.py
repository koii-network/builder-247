import pytest
from prometheus_swarm.utils.signatures import generate_signature, verify_signature

def test_generate_signature_dict():
    """Test signature generation with a dictionary"""
    data = {"key1": "value1", "key2": "value2"}
    signature = generate_signature(data)
    assert isinstance(signature, str)
    assert len(signature) == 64  # SHA-256 hex digest

def test_generate_signature_string():
    """Test signature generation with a string"""
    data = "test string"
    signature = generate_signature(data)
    assert isinstance(signature, str)
    assert len(signature) == 64  # SHA-256 hex digest

def test_generate_signature_with_secret():
    """Test signature generation with a secret key"""
    data = {"key1": "value1"}
    signature1 = generate_signature(data)
    signature2 = generate_signature(data, secret_key="mysecret")
    assert signature1 != signature2

def test_generate_signature_consistent():
    """Test that same data generates same signature"""
    data = {"key1": "value1", "key2": "value2"}
    signature1 = generate_signature(data)
    signature2 = generate_signature(data)
    assert signature1 == signature2

def test_signature_verification_success():
    """Test successful signature verification"""
    data = {"key1": "value1"}
    signature = generate_signature(data, secret_key="mysecret")
    assert verify_signature(data, signature, secret_key="mysecret") is True

def test_signature_verification_failure():
    """Test signature verification failure"""
    data = {"key1": "value1"}
    signature = generate_signature(data, secret_key="mysecret")
    assert verify_signature(data, signature, secret_key="wrongsecret") is False

def test_signature_verification_different_data():
    """Test signature verification fails with different data"""
    data1 = {"key1": "value1"}
    data2 = {"key1": "value2"}
    signature = generate_signature(data1, secret_key="mysecret")
    assert verify_signature(data2, signature, secret_key="mysecret") is False

def test_invalid_input_type():
    """Test raising TypeError for invalid input types"""
    with pytest.raises(TypeError):
        generate_signature(123)  # Invalid input type

def test_verify_signature_invalid_input():
    """Test verify_signature handles invalid inputs gracefully"""
    data = {"key1": "value1"}
    assert verify_signature(data, "invalid_signature") is False
    assert verify_signature(data, None) is False