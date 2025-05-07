import time
import pytest
from src.web_client_nonce import WebClientNonceManager

def test_nonce_generation():
    """Test nonce generation creates unique values."""
    nonce_manager = WebClientNonceManager()
    client_id = 'test_client'
    
    nonce1 = nonce_manager.generate_nonce(client_id)
    nonce2 = nonce_manager.generate_nonce(client_id)
    
    assert nonce1 != nonce2, "Nonces should be unique"

def test_nonce_validation():
    """Test nonce validation works correctly."""
    nonce_manager = WebClientNonceManager()
    client_id = 'test_client'
    
    nonce = nonce_manager.generate_nonce(client_id)
    
    assert nonce_manager.validate_nonce(nonce, client_id), "Nonce should be valid"
    assert not nonce_manager.validate_nonce(nonce, client_id), "Nonce should be invalidated after first use"

def test_nonce_expiry():
    """Test nonce expiry mechanism."""
    nonce_manager = WebClientNonceManager(nonce_expiry_seconds=1)
    client_id = 'test_client'
    
    nonce = nonce_manager.generate_nonce(client_id)
    
    time.sleep(2)  # Wait for nonce to expire
    
    assert not nonce_manager.validate_nonce(nonce, client_id), "Expired nonce should be invalid"

def test_nonce_client_mismatch():
    """Test that nonces cannot be used with different client IDs."""
    nonce_manager = WebClientNonceManager()
    client_id1 = 'client1'
    client_id2 = 'client2'
    
    nonce = nonce_manager.generate_nonce(client_id1)
    
    assert not nonce_manager.validate_nonce(nonce, client_id2), "Nonce should not be valid for different client"

def test_invalid_nonce():
    """Test that invalid nonces are rejected."""
    nonce_manager = WebClientNonceManager()
    client_id = 'test_client'
    
    assert not nonce_manager.validate_nonce('fake_nonce', client_id), "Invalid nonce should not be validated"