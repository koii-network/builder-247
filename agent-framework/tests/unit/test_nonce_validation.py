"""Unit tests for nonce validation."""

import time
import pytest
from prometheus_swarm.utils.signatures import (
    validate_nonce, 
    NonceError, 
    verify_signature_with_nonce
)

def test_validate_nonce_success():
    """Test successful nonce validation."""
    current_time = int(time.time())
    assert validate_nonce(current_time) is True

def test_validate_nonce_expired():
    """Test nonce validation for an expired nonce."""
    old_nonce = int(time.time()) - 500  # 500 seconds old (well beyond max age)
    with pytest.raises(NonceError) as exc_info:
        validate_nonce(old_nonce)
    
    assert "Nonce is too old" in str(exc_info.value)
    assert exc_info.value.nonce_type == "age_expired"

def test_validate_nonce_invalid_format():
    """Test nonce validation with invalid format."""
    with pytest.raises(NonceError) as exc_info:
        validate_nonce("not_a_number")
    
    assert "Invalid nonce format" in str(exc_info.value)
    assert exc_info.value.nonce_type == "format_error"

def test_verify_signature_with_nonce_mocked(mocker):
    """Test signature verification with mocked nonce."""
    # Mock dependencies
    mock_verify_signature = mocker.patch(
        'prometheus_swarm.utils.signatures.verify_signature',
        return_value={
            "data": json.dumps({"nonce": int(time.time()), "payload": "test"})
        }
    )
    
    mock_base58_decode = mocker.patch('base58.b58decode')
    
    result = verify_signature_with_nonce(
        "mock_signed_message", 
        "mock_staking_key"
    )
    
    assert "data" in result
    assert mock_verify_signature.called
    assert mock_base58_decode.called

def test_verify_signature_with_nonce_expired(mocker):
    """Test signature verification with an expired nonce."""
    old_time = int(time.time()) - 500  # 500 seconds ago
    
    mock_verify_signature = mocker.patch(
        'prometheus_swarm.utils.signatures.verify_signature',
        return_value={
            "data": json.dumps({"nonce": old_time, "payload": "test"})
        }
    )
    
    result = verify_signature_with_nonce(
        "mock_signed_message", 
        "mock_staking_key"
    )
    
    assert "error" in result
    assert "Nonce is too old" in result["error"]