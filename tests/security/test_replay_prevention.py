import time
import pytest
from src.security.replay_prevention import ReplayAttackPrevention

def test_replay_attack_prevention_basic():
    """Test basic replay attack prevention"""
    prevention = ReplayAttackPrevention()
    
    # First transaction should be valid
    assert prevention.validate_transaction('nonce1') == True
    
    # Same nonce should be rejected
    assert prevention.validate_transaction('nonce1') == False

def test_replay_attack_prevention_timestamp():
    """Test timestamp drift prevention"""
    prevention = ReplayAttackPrevention(max_timestamp_drift_seconds=1)
    
    # Transaction with current timestamp
    assert prevention.validate_transaction('nonce2', time.time()) == True
    
    # Transaction with timestamp far in the past
    assert prevention.validate_transaction('nonce3', time.time() - 120) == False

def test_replay_attack_prevention_decorator():
    """Test replay attack prevention decorator"""
    prevention = ReplayAttackPrevention()
    
    @prevention.transaction_decorator
    def sample_transaction(replay_nonce):
        return "Transaction successful"
    
    # First transaction should succeed
    assert sample_transaction(replay_nonce='nonce4') == "Transaction successful"
    
    # Same nonce should raise an exception
    with pytest.raises(ValueError, match="Potential replay attack detected"):
        sample_transaction(replay_nonce='nonce4')

def test_replay_attack_prevention_nonce_limit():
    """Test that nonce history is limited"""
    prevention = ReplayAttackPrevention(max_nonce_history=3)
    
    # Add more than max_nonce_history
    for i in range(5):
        assert prevention.validate_transaction(f'nonce{i}') == True
    
    # Check that only the last 3 nonces are remembered
    prevention_nonces = set(prevention._nonce_history.keys())
    assert len(prevention_nonces) == 3
    assert set(['nonce2', 'nonce3', 'nonce4']) == prevention_nonces

def test_replay_attack_prevention_decorator_no_nonce():
    """Test decorator raises error when no nonce is provided"""
    prevention = ReplayAttackPrevention()
    
    @prevention.transaction_decorator
    def sample_transaction():
        return "Transaction successful"
    
    # Should raise an error without a nonce
    with pytest.raises(ValueError, match="No nonce provided"):
        sample_transaction()