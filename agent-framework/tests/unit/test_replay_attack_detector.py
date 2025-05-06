import time
import pytest
from prometheus_swarm.security.replay_attack_detector import ReplayAttackDetector

def test_replay_attack_detector_basic():
    """Test basic replay attack detection functionality."""
    detector = ReplayAttackDetector(window_seconds=10)
    
    # Test request
    test_request = {"action": "login", "user": "test_user"}
    signature = detector.get_signature(test_request)
    
    # First time should return False (not a replay)
    assert not detector.is_replay_attack(signature)
    
    # Second time should return True (replay detected)
    assert detector.is_replay_attack(signature)

def test_replay_attack_detector_timeout():
    """Test that old signatures expire after the time window."""
    detector = ReplayAttackDetector(window_seconds=1)
    
    test_request = {"action": "transaction", "amount": 100}
    signature = detector.get_signature(test_request)
    
    # First time should return False
    assert not detector.is_replay_attack(signature)
    
    # Wait for timeout
    time.sleep(1.1)
    
    # After timeout, should return False again
    assert not detector.is_replay_attack(signature)

def test_different_requests():
    """Test that different requests are not considered replays."""
    detector = ReplayAttackDetector()
    
    request1 = {"action": "login", "user": "user1"}
    request2 = {"action": "login", "user": "user2"}
    
    signature1 = detector.get_signature(request1)
    signature2 = detector.get_signature(request2)
    
    assert not detector.is_replay_attack(signature1)
    assert not detector.is_replay_attack(signature2)

def test_max_unique_requests():
    """Test maximum unique requests limit."""
    detector = ReplayAttackDetector(max_unique_requests=2)
    
    request1 = {"action": "test1"}
    request2 = {"action": "test2"}
    request3 = {"action": "test3"}
    
    sig1 = detector.get_signature(request1)
    sig2 = detector.get_signature(request2)
    sig3 = detector.get_signature(request3)
    
    detector.is_replay_attack(sig1)
    detector.is_replay_attack(sig2)
    detector.is_replay_attack(sig3)
    
    # Only last two signatures should be remembered
    assert len(detector._request_signatures) == 2

def test_empty_signature():
    """Test handling of empty signatures."""
    detector = ReplayAttackDetector()
    
    assert not detector.is_replay_attack("")
    assert not detector.is_replay_attack(None)  # type: ignore

def test_signature_generation_consistency():
    """Test that identical requests generate the same signature."""
    detector = ReplayAttackDetector()
    
    request = {"user": "test", "action": "login", "timestamp": 12345}
    signature1 = detector.get_signature(request)
    signature2 = detector.get_signature(request)
    
    assert signature1 == signature2