"""Tests for signature generation and verification utilities."""

import pytest
import nacl.signing
import base58
import json
from prometheus_swarm.utils.signatures import (
    generate_signature, 
    verify_signature, 
    verify_and_parse_signature
)

@pytest.fixture
def generate_key_pair():
    """Generate a signing key pair for testing."""
    signing_key = nacl.signing.SigningKey.generate()
    verify_key = signing_key.verify_key

    # Convert keys to base58
    signing_key_b58 = base58.b58encode(bytes(signing_key)).decode('utf-8')
    verify_key_b58 = base58.b58encode(bytes(verify_key)).decode('utf-8')

    return {
        'signing_key': signing_key_b58,
        'verify_key': verify_key_b58
    }

def test_generate_signature_string(generate_key_pair):
    """Test generating a signature for a string message."""
    message = "Hello, world!"
    result = generate_signature(message, generate_key_pair['signing_key'])
    
    assert 'signature' in result
    assert isinstance(result['signature'], str)

def test_generate_signature_dict(generate_key_pair):
    """Test generating a signature for a dictionary message."""
    message = {"task": "test", "value": 42}
    result = generate_signature(message, generate_key_pair['signing_key'])
    
    assert 'signature' in result
    assert isinstance(result['signature'], str)

def test_signature_verification_flow(generate_key_pair):
    """Test the full signature generation and verification flow."""
    # Message to sign
    message = {"task": "verification", "nonce": 12345}

    # Generate signature
    gen_result = generate_signature(message, generate_key_pair['signing_key'])
    signature = gen_result['signature']

    # Verify signature
    verify_result = verify_signature(signature, generate_key_pair['verify_key'])
    
    assert 'data' in verify_result
    assert json.loads(verify_result['data']) == message

def test_signature_generation_error():
    """Test signature generation with an invalid key."""
    result = generate_signature("test", "invalid_key")
    
    assert 'error' in result
    assert 'Signature generation failed' in result['error']

def test_parse_signed_signature(generate_key_pair):
    """Test generating, signing, and parsing a signature with expected values."""
    message = {"task": "test", "status": "active"}
    
    # Generate signature
    gen_result = generate_signature(message, generate_key_pair['signing_key'])
    signature = gen_result['signature']

    # Verify and parse with expected values
    result = verify_and_parse_signature(
        signature, 
        generate_key_pair['verify_key'], 
        expected_values={'task': 'test'}
    )

    assert 'data' in result
    assert result['data'] == message

def test_parse_signature_invalid_expectation(generate_key_pair):
    """Test parsing a signature with invalid expected values."""
    message = {"task": "test", "status": "active"}
    
    # Generate signature
    gen_result = generate_signature(message, generate_key_pair['signing_key'])
    signature = gen_result['signature']

    # Verify and parse with incorrect expected value
    result = verify_and_parse_signature(
        signature, 
        generate_key_pair['verify_key'], 
        expected_values={'task': 'wrong'}
    )

    assert 'error' in result
    assert 'Invalid payload' in result['error']