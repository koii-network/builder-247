"""Tests for signature generation and verification utilities."""

import pytest
import json
import nacl.signing
import base58
from prometheus_swarm.utils.signatures import generate_signature, verify_signature, verify_and_parse_signature


@pytest.fixture
def signing_keypair():
    """Generate a new signing key pair for testing."""
    signing_key = nacl.signing.SigningKey.generate()
    verify_key = signing_key.verify_key
    
    # Encode keys in base58
    signing_key_str = base58.b58encode(bytes(signing_key)).decode('utf-8')
    verify_key_str = base58.b58encode(bytes(verify_key)).decode('utf-8')
    
    return {
        'signing_key': signing_key_str,
        'verify_key': verify_key_str
    }


def test_generate_signature_with_dict(signing_keypair):
    """Test signature generation with a dictionary payload."""
    payload = {"action": "test", "value": 42}
    signature = generate_signature(payload, signing_keypair['signing_key'])
    
    # Verify the signature
    result = verify_signature(signature, signing_keypair['verify_key'])
    assert 'error' not in result
    
    # Parse the result
    parsed_payload = json.loads(result['data'])
    assert parsed_payload == payload


def test_generate_signature_with_string(signing_keypair):
    """Test signature generation with a string payload."""
    payload = "Hello, world!"
    signature = generate_signature(payload, signing_keypair['signing_key'])
    
    # Verify the signature
    result = verify_signature(signature, signing_keypair['verify_key'])
    assert 'error' not in result
    assert result['data'] == payload


def test_generate_signature_invalid_payload(signing_keypair):
    """Test signature generation with an invalid payload."""
    with pytest.raises(ValueError):
        generate_signature(42, signing_keypair['signing_key'])


def test_verify_signature_invalid_signature(signing_keypair):
    """Test verification of an invalid or tampered signature."""
    payload = {"action": "test", "value": 42}
    signature = generate_signature(payload, signing_keypair['signing_key'])
    
    # Use a different key for verification
    different_keypair = nacl.signing.SigningKey.generate()
    different_verify_key_str = base58.b58encode(bytes(different_keypair.verify_key)).decode('utf-8')
    
    result = verify_signature(signature, different_verify_key_str)
    assert 'error' in result


def test_verify_and_parse_signature_with_expected_values(signing_keypair):
    """Test signature verification with expected values."""
    payload = {"action": "test", "value": 42}
    signature = generate_signature(payload, signing_keypair['signing_key'])
    
    result = verify_and_parse_signature(
        signature, 
        signing_keypair['verify_key'], 
        expected_values={"action": "test"}
    )
    
    assert 'error' not in result
    assert result['data'] == payload


def test_verify_and_parse_signature_with_invalid_expected_values(signing_keypair):
    """Test signature verification with invalid expected values."""
    payload = {"action": "test", "value": 42}
    signature = generate_signature(payload, signing_keypair['signing_key'])
    
    result = verify_and_parse_signature(
        signature, 
        signing_keypair['verify_key'], 
        expected_values={"action": "wrong"}
    )
    
    assert 'error' in result