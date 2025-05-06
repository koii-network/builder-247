import pytest
import time
from datetime import datetime, timedelta

from prometheus_swarm.utils.nonce import NonceManager, NonceError

def test_nonce_validation_basic():
    """Test basic nonce validation functionality."""
    nonce_manager = NonceManager()
    nonce = "unique_nonce_123"
    
    # First use of nonce should be valid
    assert nonce_manager.validate_nonce(nonce) is True
    
    # Second use of same nonce should raise NonceError
    with pytest.raises(NonceError, match="Nonce has already been used"):
        nonce_manager.validate_nonce(nonce)

def test_nonce_validation_with_client_id():
    """Test nonce validation with client ID."""
    nonce_manager = NonceManager()
    nonce = "client_specific_nonce"
    client_id_1 = "client1"
    client_id_2 = "client2"
    
    # First use with client ID should be valid
    assert nonce_manager.validate_nonce(nonce, client_id_1) is True
    
    # Same nonce with different client ID should raise error
    with pytest.raises(NonceError, match="Nonce already used by a different client"):
        nonce_manager.validate_nonce(nonce, client_id_2)

def test_nonce_expiration():
    """Test nonce expiration mechanism."""
    # Set very short nonce expiration for testing
    nonce_manager = NonceManager(max_nonce_age_seconds=1)
    nonce = "expiring_nonce"
    
    # First use of nonce
    assert nonce_manager.validate_nonce(nonce) is True
    
    # Wait for nonce to expire
    time.sleep(2)
    
    # Nonce should be valid again after expiration
    assert nonce_manager.validate_nonce(nonce) is True

def test_nonce_concurrent_validation():
    """Test concurrent nonce validation scenarios."""
    nonce_manager = NonceManager()
    nonce = "multiple_validation_nonce"
    
    # First use of nonce
    assert nonce_manager.validate_nonce(nonce) is True
    
    # Subsequent use within same session should fail
    with pytest.raises(NonceError):
        nonce_manager.validate_nonce(nonce)

def test_nonce_edge_cases():
    """Test edge cases for nonce validation."""
    nonce_manager = NonceManager()
    
    # Empty nonce
    with pytest.raises(TypeError):
        nonce_manager.validate_nonce("")
    
    # None nonce 
    with pytest.raises(TypeError):
        nonce_manager.validate_nonce(None)