import pytest
import time
from src.server.utils.replay_prevention import (
    ReplayPreventionManager, 
    ReplayPreventionError
)

def test_replay_prevention_manager_basic():
    """Test basic replay prevention functionality."""
    rpm = ReplayPreventionManager()
    current_time = time.time()
    
    # First request should be valid
    assert rpm.validate_request('nonce1', current_time) is True
    
    # Same nonce should raise an error
    with pytest.raises(ReplayPreventionError, match="Duplicate request detected"):
        rpm.validate_request('nonce1', current_time)

def test_replay_prevention_manager_timestamp():
    """Test timestamp validation in replay prevention."""
    rpm = ReplayPreventionManager(max_request_age_seconds=10)
    current_time = time.time()
    
    # Request with recent timestamp should be valid
    assert rpm.validate_request('nonce1', current_time) is True
    
    # Request with very old timestamp should fail
    with pytest.raises(ReplayPreventionError, match="Request timestamp is too old"):
        rpm.validate_request('nonce2', current_time - 20)

def test_replay_prevention_manager_cleanup():
    """Test nonce cleanup mechanism."""
    rpm = ReplayPreventionManager(max_request_age_seconds=10)
    current_time = time.time()
    
    # Add multiple nonces at different times
    rpm.validate_request('nonce1', current_time)
    rpm.validate_request('nonce2', current_time - 5)
    rpm.validate_request('nonce3', current_time - 15)
    
    # Manual cleanup
    rpm._cleanup_nonces(current_time)
    
    # Check that old nonces are removed
    assert len(rpm._used_nonces) == 2
    assert 'nonce1' in rpm._used_nonces
    assert 'nonce2' in rpm._used_nonces
    assert 'nonce3' not in rpm._used_nonces

def test_replay_prevention_edge_cases():
    """Test edge cases in replay prevention."""
    rpm = ReplayPreventionManager()
    current_time = time.time()
    
    # Test multiple different nonces
    assert rpm.validate_request('nonce1', current_time) is True
    assert rpm.validate_request('nonce2', current_time) is True
    
    # Repeat tests with slightly different timestamps
    assert rpm.validate_request('nonce3', current_time + 0.001) is True
    assert rpm.validate_request('nonce4', current_time - 0.001) is True