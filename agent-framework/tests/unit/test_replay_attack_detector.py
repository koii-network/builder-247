import time
import pytest
from prometheus_swarm.security.replay_attack_detector import ReplayAttackDetector


def test_replay_attack_detector_basic():
    """Test basic replay attack detection functionality."""
    detector = ReplayAttackDetector(window_size=300)
    
    # First time nonce is used, should return False
    assert not detector.is_replay_attack("nonce1")
    
    # Same nonce used again, should return True
    assert detector.is_replay_attack("nonce1")


def test_replay_attack_detector_different_nonces():
    """Test that different nonces are allowed."""
    detector = ReplayAttackDetector(window_size=300)
    
    assert not detector.is_replay_attack("nonce1")
    assert not detector.is_replay_attack("nonce2")
    assert not detector.is_replay_attack("nonce3")
    
    # Only nonce1 is now a replay attack
    assert detector.is_replay_attack("nonce1")


def test_replay_attack_detector_time_window(monkeypatch):
    """Test that nonces expire after the time window."""
    times = [0]
    def mock_time():
        return times[0]
    
    monkeypatch.setattr(time, 'time', mock_time)
    
    detector = ReplayAttackDetector(window_size=5)
    
    # Add initial nonce
    times[0] = 0
    assert not detector.is_replay_attack("nonce1")
    
    # Still a replay attack before window expires
    times[0] = 4
    assert detector.is_replay_attack("nonce1")
    
    # No longer a replay attack after window expires
    times[0] = 6
    assert not detector.is_replay_attack("nonce1")


def test_replay_attack_detector_max_nonces():
    """Test that the detector limits the number of stored nonces."""
    detector = ReplayAttackDetector(window_size=300, max_nonces=3)
    
    # Add more nonces than max_nonces
    assert not detector.is_replay_attack("nonce1")
    assert not detector.is_replay_attack("nonce2")
    assert not detector.is_replay_attack("nonce3")
    assert not detector.is_replay_attack("nonce4")
    
    # First nonce should no longer be tracked as a replay attack
    assert not detector.is_replay_attack("nonce1")
    assert not detector.is_replay_attack("nonce5")
    
    # Since all nonces are added again, the most recent nonces should be tracked
    # but the oldest ones will be discarded to maintain max limit
    assert detector.is_replay_attack("nonce4")
    assert detector.is_replay_attack("nonce5")
    assert detector.is_replay_attack("nonce3")  # Most recently added of the first batch