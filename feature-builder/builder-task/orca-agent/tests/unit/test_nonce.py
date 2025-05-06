import time
import pytest
from src.utils.nonce import NonceManager, NonceError

def test_nonce_generation():
    """Test that nonce generation creates unique values."""
    nonce_manager = NonceManager()
    
    # Generate multiple nonces and ensure they are unique
    nonces = [nonce_manager.generate_nonce() for _ in range(10)]
    assert len(set(nonces)) == 10

def test_nonce_validation_success():
    """Test successful nonce validation."""
    nonce_manager = NonceManager()
    
    # Generate and validate nonce
    nonce = nonce_manager.generate_nonce()
    assert nonce_manager.validate_nonce(nonce) is True

def test_nonce_reuse_prevention():
    """Test that a nonce cannot be reused."""
    nonce_manager = NonceManager()
    
    # Generate and first-time validate
    nonce = nonce_manager.generate_nonce()
    assert nonce_manager.validate_nonce(nonce) is True
    
    # Try to reuse the same nonce
    with pytest.raises(NonceError, match="Nonce has already been used"):
        nonce_manager.validate_nonce(nonce)

def test_empty_nonce():
    """Test validation of an empty nonce."""
    nonce_manager = NonceManager()
    
    with pytest.raises(NonceError, match="Empty nonce provided"):
        nonce_manager.validate_nonce(None)
    
    with pytest.raises(NonceError, match="Empty nonce provided"):
        nonce_manager.validate_nonce("")

def test_nonce_decorator():
    """Test the nonce_required decorator."""
    nonce_manager = NonceManager()
    
    @nonce_manager.nonce_required
    def test_function(nonce=None):
        return "Success"
    
    # Successful case
    nonce = nonce_manager.generate_nonce()
    assert test_function(nonce=nonce) == "Success"
    
    # Reusing nonce should fail
    with pytest.raises(NonceError):
        test_function(nonce=nonce)