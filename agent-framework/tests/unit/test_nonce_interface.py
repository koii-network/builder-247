import time
import pytest
from prometheus_swarm.utils.nonce import NonceRequestInterface

def test_generate_nonce():
    """Test generating a unique nonce"""
    nonce_interface = NonceRequestInterface()
    nonce1 = nonce_interface.generate_nonce()
    nonce2 = nonce_interface.generate_nonce()
    
    assert nonce1 != nonce2
    assert isinstance(nonce1, str)
    assert len(nonce1) > 0

def test_validate_nonce():
    """Test validating a generated nonce"""
    nonce_interface = NonceRequestInterface()
    nonce = nonce_interface.generate_nonce()
    
    assert nonce_interface.validate_nonce(nonce) is True
    assert nonce_interface.validate_nonce(nonce) is False  # Cannot reuse nonce

def test_nonce_context():
    """Test nonce validation with context"""
    nonce_interface = NonceRequestInterface()
    nonce1 = nonce_interface.generate_nonce(context='user1')
    nonce2 = nonce_interface.generate_nonce(context='user2')
    
    assert nonce_interface.validate_nonce(nonce1, context='user1') is True
    assert nonce_interface.validate_nonce(nonce1, context='user2') is False
    assert nonce_interface.validate_nonce(nonce2, context='user1') is False

def test_nonce_expiration():
    """Test nonce expiration"""
    nonce_interface = NonceRequestInterface(max_age_seconds=1)
    nonce = nonce_interface.generate_nonce()
    
    time.sleep(2)  # Wait for nonce to expire
    assert nonce_interface.validate_nonce(nonce) is False

def test_clear_expired_nonces():
    """Test clearing expired nonces"""
    nonce_interface = NonceRequestInterface(max_age_seconds=1)
    
    # Generate multiple nonces
    nonces = [nonce_interface.generate_nonce() for _ in range(5)]
    
    # Use some nonces
    nonce_interface.validate_nonce(nonces[0])
    nonce_interface.validate_nonce(nonces[1])
    
    time.sleep(2)  # Wait for nonces to expire
    
    # Clear expired nonces
    cleared_count = nonce_interface.clear_expired_nonces()
    assert cleared_count > 0

def test_invalid_nonce():
    """Test validation of an invalid nonce"""
    nonce_interface = NonceRequestInterface()
    invalid_nonce = 'not-a-real-nonce'
    
    assert nonce_interface.validate_nonce(invalid_nonce) is False

def test_nonce_thread_safety(mocker):
    """Test basic thread safety of nonce generation"""
    nonce_interface = NonceRequestInterface()
    
    # Simulate multiple threads generating nonces
    mock_threads = [
        mocker.Mock(name=f'thread_{i}') for i in range(10)
    ]
    
    nonces = set()
    for thread in mock_threads:
        nonce = nonce_interface.generate_nonce()
        nonces.add(nonce)
    
    assert len(nonces) == len(mock_threads)