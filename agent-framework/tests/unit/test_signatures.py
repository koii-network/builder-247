import pytest
import time
from prometheus_swarm.utils.signatures import generate_signature, verify_signature

def test_generate_signature_basic():
    """Test basic signature generation"""
    payload = {'key': 'value'}
    signature = generate_signature(payload)
    
    assert 'signature' in signature
    assert 'id' in signature
    assert 'timestamp' in signature
    assert len(signature['signature']) > 0
    assert len(signature['id']) > 0

def test_generate_signature_with_secret_key():
    """Test signature generation with a secret key"""
    payload = {'key': 'value'}
    secret_key = 'test_secret'
    signature = generate_signature(payload, secret_key)
    
    assert 'signature' in signature
    assert 'id' in signature
    assert 'timestamp' in signature

def test_verify_signature_success():
    """Test successful signature verification"""
    payload = {'key': 'value'}
    signature = generate_signature(payload)
    
    assert verify_signature(payload, signature) is True

def test_verify_signature_with_secret_key():
    """Test signature verification with a secret key"""
    payload = {'key': 'value'}
    secret_key = 'test_secret'
    signature = generate_signature(payload, secret_key)
    
    assert verify_signature(payload, signature, secret_key) is True

def test_verify_signature_failure():
    """Test signature verification failure"""
    payload = {'key': 'value'}
    different_payload = {'key': 'different_value'}
    signature = generate_signature(payload)
    
    assert verify_signature(different_payload, signature) is False

def test_generate_signature_invalid_input():
    """Test signature generation with invalid inputs"""
    with pytest.raises(TypeError):
        generate_signature([])  # List instead of dict
    
    with pytest.raises(ValueError):
        generate_signature({})  # Empty dict

def test_signature_reproducibility():
    """Test that identical payloads generate identical signatures"""
    payload = {'key': 'value'}
    sig1 = generate_signature(payload)
    sig2 = generate_signature(payload)
    
    assert sig1['signature'] == sig2['signature']
    assert sig1['id'] != sig2['id']  # ID should be unique each time

def test_signature_with_complex_payload():
    """Test signature generation with complex payload"""
    payload = {
        'nested': {
            'dict': 'value'
        },
        'list': [1, 2, 3],
        'bool': True
    }
    signature = generate_signature(payload)
    
    assert verify_signature(payload, signature) is True