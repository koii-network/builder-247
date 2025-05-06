import pytest
from src.signature_generator import generate_signature, verify_signature

def test_generate_signature_basic():
    data = {"name": "John", "age": 30}
    signature = generate_signature(data)
    assert isinstance(signature, str)
    assert len(signature) == 64  # SHA-256 hexadecimal representation

def test_generate_signature_same_data_produces_same_signature():
    data1 = {"name": "John", "age": 30}
    data2 = {"name": "John", "age": 30}
    signature1 = generate_signature(data1)
    signature2 = generate_signature(data2)
    assert signature1 == signature2

def test_generate_signature_different_data_produces_different_signatures():
    data1 = {"name": "John", "age": 30}
    data2 = {"name": "Jane", "age": 25}
    signature1 = generate_signature(data1)
    signature2 = generate_signature(data2)
    assert signature1 != signature2

def test_generate_signature_with_secret_key():
    data = {"name": "John", "age": 30}
    signature1 = generate_signature(data)
    signature2 = generate_signature(data, secret_key="mysecret")
    assert signature1 != signature2

def test_verify_signature_success():
    data = {"name": "John", "age": 30}
    signature = generate_signature(data)
    assert verify_signature(data, signature) is True

def test_verify_signature_with_secret_key():
    data = {"name": "John", "age": 30}
    secret_key = "mysecret"
    signature = generate_signature(data, secret_key)
    assert verify_signature(data, signature, secret_key) is True
    assert verify_signature(data, signature) is False

def test_generate_signature_invalid_input():
    with pytest.raises(TypeError):
        generate_signature("not a dictionary")
    
    with pytest.raises(ValueError):
        generate_signature({})

def test_verify_signature_invalid_input():
    data = {"name": "John", "age": 30}
    invalid_signature = "invalid_signature"
    
    assert verify_signature(data, invalid_signature) is False
    assert verify_signature("not a dictionary", "signature") is False