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


def test_replay_attack_detector_time_window():
    """Test that nonces expire after the time window."""
    class MockTimeReplayAttackDetector(ReplayAttackDetector):
        def __init__(self, window_size=300, max_nonces=1000):
            super().__init__(window_size, max_nonces)
            self._mock_time = 0
        
        def _get_current_time(self):
            return self._mock_time
        
        def is_replay_attack(self, nonce):
            current_time = time.time()
            self._mock_time = current_time
            return super().is_replay_attack(nonce)
        
        def set_mock_time(self, time_val):
            self._mock_time = time_val

    detector = MockTimeReplayAttackDetector(window_size=5)
    
    # Add initial nonce
    assert not detector.is_replay_attack("nonce1")
    
    # Set time just before expiration
    detector.set_mock_time(time.time() + 4)
    assert detector.is_replay_attack("nonce1")
    
    # Set time just after expiration
    detector.set_mock_time(time.time() + 6)
    assert not detector.is_replay_attack("nonce1")


def test_replay_attack_detector_max_nonces():
    """Test that the detector limits the number of stored nonces."""
    detector = ReplayAttackDetector(window_size=300, max_nonces=3)
    
    # Add more nonces than max_nonces
    assert not detector.is_replay_attack("nonce1")
    assert not detector.is_replay_attack("nonce2")
    assert not detector.is_replay_attack("nonce3")
    assert not detector.is_replay_attack("nonce4")
    
    # First nonce should no longer be tracked
    assert not detector.is_replay_attack("nonce1")
    
    # Other nonces still tracked
    assert detector.is_replay_attack("nonce2")
    assert detector.is_replay_attack("nonce3")
    assert detector.is_replay_attack("nonce4")