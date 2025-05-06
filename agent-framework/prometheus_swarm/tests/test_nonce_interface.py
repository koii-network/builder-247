import time
import pytest
from prometheus_swarm.nonce_interface import NonceRequestInterface

def test_generate_nonce():
    """Test nonce generation creates unique nonces."""
    nonce_interface = NonceRequestInterface()
    
    nonce1 = nonce_interface.generate_nonce()
    nonce2 = nonce_interface.generate_nonce()
    
    assert nonce1 != nonce2, "Generated nonces should be unique"

def test_nonce_validation():
    """Test basic nonce validation."""
    nonce_interface = NonceRequestInterface()
    
    nonce = nonce_interface.generate_nonce()
    assert nonce_interface.validate_nonce(nonce), "Valid nonce should be validated"
    
    # Second validation should fail (nonce can only be used once)
    assert not nonce_interface.validate_nonce(nonce), "Used nonce should not be revalidated"

def test_nonce_context():
    """Test nonce validation with context."""
    nonce_interface = NonceRequestInterface()
    
    nonce1 = nonce_interface.generate_nonce(context='login')
    nonce2 = nonce_interface.generate_nonce(context='signup')
    
    # Validate with correct context
    assert nonce_interface.validate_nonce(nonce1, context='login'), "Nonce with matching context should validate"
    assert nonce_interface.validate_nonce(nonce2, context='signup'), "Nonce with matching context should validate"
    
    # Validate with incorrect context
    assert not nonce_interface.validate_nonce(nonce1, context='signup'), "Nonce with mismatched context should not validate"

def test_nonce_expiry():
    """Test nonce expiration."""
    nonce_interface = NonceRequestInterface(nonce_expiry_seconds=1)
    
    nonce = nonce_interface.generate_nonce()
    
    # Wait for nonce to expire
    time.sleep(2)
    
    assert not nonce_interface.validate_nonce(nonce), "Expired nonce should not validate"

def test_nonce_store_cleanup():
    """Test automatic cleanup of expired and used nonces."""
    nonce_interface = NonceRequestInterface(nonce_expiry_seconds=1)
    
    # Generate multiple nonces
    nonces = [nonce_interface.generate_nonce() for _ in range(5)]
    
    # Use and validate some nonces
    nonce_interface.validate_nonce(nonces[0])
    nonce_interface.validate_nonce(nonces[1])
    
    # Wait for expiry
    time.sleep(2)
    
    # Trigger internal cleanup
    nonce = nonce_interface.generate_nonce()
    
    # Check that the nonce store has been cleaned
    assert len(nonce_interface._nonce_store) <= 1, "Nonce store should be cleaned up after expiry"

def test_invalid_nonce():
    """Test validation of non-existent nonce."""
    nonce_interface = NonceRequestInterface()
    
    invalid_nonce = 'non-existent-nonce'
    assert not nonce_interface.validate_nonce(invalid_nonce), "Non-existent nonce should not validate"