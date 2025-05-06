import time
import pytest
from datetime import datetime, timedelta
from agent_framework.prometheus_swarm.utils.nonce import NonceManager, NonceError, nonce_protected

def test_nonce_generation():
    """Test nonce generation and basic properties."""
    nonce_manager = NonceManager()
    nonce = nonce_manager.generate_nonce()
    
    assert isinstance(nonce, str)
    assert len(nonce) > 0
    assert nonce in nonce_manager._used_nonces

def test_nonce_validation_success():
    """Test successful nonce validation."""
    nonce_manager = NonceManager()
    nonce = nonce_manager.generate_nonce()
    
    assert nonce_manager.validate_nonce(nonce) is True
    assert nonce_manager._used_nonces[nonce]['usage_count'] == 1

def test_nonce_max_usage():
    """Test nonce maximum usage limit."""
    nonce_manager = NonceManager(max_nonce_usage=2)
    nonce = nonce_manager.generate_nonce()
    
    assert nonce_manager.validate_nonce(nonce) is True
    assert nonce_manager.validate_nonce(nonce) is True
    
    with pytest.raises(NonceError):
        nonce_manager.validate_nonce(nonce)

def test_nonce_expiration():
    """Test nonce expiration mechanism."""
    nonce_manager = NonceManager(max_nonce_age=1)
    nonce = nonce_manager.generate_nonce()
    
    # Mock older nonce
    nonce_manager._used_nonces[nonce]['created_at'] = datetime.now() - timedelta(seconds=2)
    
    with pytest.raises(NonceError):
        nonce_manager.validate_nonce(nonce)

def test_nonce_cleanup():
    """Test nonce cleanup mechanism."""
    nonce_manager = NonceManager(max_nonce_age=1)
    
    # Generate multiple nonces
    nonces = [nonce_manager.generate_nonce() for _ in range(5)]
    
    # Mock older nonces
    for nonce in nonces:
        nonce_manager._used_nonces[nonce]['created_at'] = datetime.now() - timedelta(seconds=2)
    
    cleaned_nonces = nonce_manager.cleanup_expired_nonces()
    assert cleaned_nonces == 5
    assert len(nonce_manager._used_nonces) == 0

def test_nonce_decorator():
    """Test nonce decorator functionality."""
    nonce_manager = NonceManager()
    
    @nonce_protected(nonce_manager)
    def protected_function(nonce):
        return "Success"
    
    nonce = nonce_manager.generate_nonce()
    result = protected_function(nonce=nonce)
    assert result == "Success"
    
    with pytest.raises(NonceError):
        # Reuse same nonce should fail
        protected_function(nonce=nonce)
    
    with pytest.raises(NonceError):
        # Missing nonce should fail
        protected_function()

def test_nonce_multiple_managers():
    """Test multiple nonce managers do not interfere."""
    manager1 = NonceManager()
    manager2 = NonceManager()
    
    nonce1 = manager1.generate_nonce()
    nonce2 = manager2.generate_nonce()
    
    assert manager1.validate_nonce(nonce1) is True
    assert manager2.validate_nonce(nonce2) is True
    
    with pytest.raises(NonceError):
        manager1.validate_nonce(nonce2)
    with pytest.raises(NonceError):
        manager2.validate_nonce(nonce1)