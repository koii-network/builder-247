import pytest
import json
import ecdsa
import base64
from prometheus_swarm.utils.client_signature import (
    generate_client_signature, 
    verify_client_signature, 
    ClientSignatureError
)

@pytest.fixture
def test_keypair():
    """Generate a test ECDSA key pair."""
    private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    public_key = private_key.get_verifying_key()
    
    return {
        'private_key': private_key.to_pem().decode('utf-8'),
        'public_key': public_key.to_pem().decode('utf-8')
    }

def test_signature_generation_with_dict(test_keypair):
    """Test signature generation with a dictionary payload."""
    payload = {'key1': 'value1', 'key2': 'value2'}
    signature = generate_client_signature(payload, test_keypair['private_key'])
    
    assert signature is not None
    assert isinstance(signature, str)
    assert len(signature) > 0

def test_signature_verification_with_dict(test_keypair):
    """Test signature verification with a dictionary payload."""
    payload = {'key1': 'value1', 'key2': 'value2'}
    signature = generate_client_signature(payload, test_keypair['private_key'])
    
    assert verify_client_signature(payload, signature, test_keypair['public_key']) is True

def test_signature_verification_with_json_string(test_keypair):
    """Test signature verification with a JSON string payload."""
    payload_str = json.dumps({'key1': 'value1', 'key2': 'value2'}, sort_keys=True)
    signature = generate_client_signature(payload_str, test_keypair['private_key'])
    
    assert verify_client_signature(payload_str, signature, test_keypair['public_key']) is True

def test_signature_verification_fails_with_modified_payload(test_keypair):
    """Test that signature verification fails with a modified payload."""
    payload = {'key1': 'value1', 'key2': 'value2'}
    signature = generate_client_signature(payload, test_keypair['private_key'])
    
    modified_payload = {'key1': 'modified_value', 'key2': 'value2'}
    assert verify_client_signature(modified_payload, signature, test_keypair['public_key']) is False

def test_invalid_payload_types():
    """Test handling of invalid payload types."""
    with pytest.raises(ClientSignatureError):
        generate_client_signature(123, 'dummy_private_key')

def test_invalid_json_payload():
    """Test handling of invalid JSON payload."""
    with pytest.raises(ClientSignatureError):
        generate_client_signature('invalid json', 'dummy_private_key')

def test_signature_verification_with_invalid_signature(test_keypair):
    """Test signature verification with an invalid signature."""
    payload = {'key1': 'value1', 'key2': 'value2'}
    assert verify_client_signature(payload, 'invalid_signature', test_keypair['public_key']) is False

def test_signature_verification_with_wrong_public_key(test_keypair):
    """Test signature verification with a wrong public key."""
    payload = {'key1': 'value1', 'key2': 'value2'}
    signature = generate_client_signature(payload, test_keypair['private_key'])
    
    # Generate a different key pair
    wrong_private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    wrong_public_key = wrong_private_key.get_verifying_key()
    
    assert verify_client_signature(payload, signature, wrong_public_key.to_pem().decode('utf-8')) is False