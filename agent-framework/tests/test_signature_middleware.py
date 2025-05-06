"""Tests for Signature Validation Middleware."""

import json
import base58
import nacl.signing
import pytest
from prometheus_swarm.middleware.signature_validation import validate_signature

def generate_test_signature(payload_dict, sender_key=None):
    """Helper to generate a signed message for testing."""
    if sender_key is None:
        sender_key = nacl.signing.SigningKey.generate()
    
    message = json.dumps(payload_dict).encode('utf-8')
    signed_message = sender_key.sign(message)
    
    signed_message_b58 = base58.b58encode(signed_message).decode('utf-8')
    public_key_b58 = base58.b58encode(sender_key.verify_key.encode()).decode('utf-8')
    
    return signed_message_b58, public_key_b58

def test_signature_middleware_success():
    """Test successful signature validation."""
    payload = {"action": "test", "value": 42}
    signed_msg, public_key = generate_test_signature(payload)

    @validate_signature()
    def sample_function(decoded_payload):
        return decoded_payload

    result = sample_function(signed_msg, public_key)
    assert result == payload

def test_signature_middleware_with_expected_values():
    """Test signature validation with expected values."""
    payload = {"action": "test", "value": 42}
    signed_msg, public_key = generate_test_signature(payload)

    @validate_signature(expected_values={"action": "test"})
    def sample_function(decoded_payload):
        return decoded_payload

    result = sample_function(signed_msg, public_key)
    assert result == payload

def test_signature_middleware_with_custom_key_getter():
    """Test signature validation with a custom key getter."""
    payload = {"action": "test", "value": 42}
    signed_msg, public_key = generate_test_signature(payload)

    def key_getter(msg, custom_key):
        return custom_key

    @validate_signature(staking_key_getter=key_getter)
    def sample_function(msg, custom_key):
        return msg

    result = sample_function(signed_msg, public_key)
    assert result == payload

def test_signature_middleware_invalid_signature():
    """Test validation with an invalid signature."""
    payload = {"action": "test", "value": 42}
    signed_msg, _ = generate_test_signature(payload)
    wrong_key = base58.b58encode(nacl.signing.SigningKey.generate().verify_key.encode()).decode('utf-8')

    @validate_signature()
    def sample_function(decoded_payload):
        return decoded_payload

    with pytest.raises(ValueError, match="Verification failed"):
        sample_function(signed_msg, wrong_key)

def test_signature_middleware_unexpected_payload():
    """Test validation with mismatched expected values."""
    payload = {"action": "test", "value": 42}
    signed_msg, public_key = generate_test_signature(payload)

    @validate_signature(expected_values={"value": 100})
    def sample_function(decoded_payload):
        return decoded_payload

    with pytest.raises(ValueError, match="Invalid payload"):
        sample_function(signed_msg, public_key)