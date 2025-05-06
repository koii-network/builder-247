import time
import pytest
from prometheus_swarm.utils.replay_attack import ReplayAttackDetector

def test_replay_attack_detector_basic():
    """Test basic replay attack detection."""
    detector = ReplayAttackDetector(max_window_seconds=5)
    
    # First request should return False (not a replay)
    assert not detector.detect_replay("unique_request_1")
    
    # Same request within window should return True (replay)
    assert detector.detect_replay("unique_request_1")

def test_replay_attack_detector_different_requests():
    """Test different requests are treated independently."""
    detector = ReplayAttackDetector(max_window_seconds=5)
    
    # Different requests should be unique
    assert not detector.detect_replay("request_1")
    assert not detector.detect_replay("request_2")
    assert detector.detect_replay("request_1")

def test_replay_attack_detector_time_expiry():
    """Test requests expire after the time window."""
    detector = ReplayAttackDetector(max_window_seconds=1)
    
    # First request
    assert not detector.detect_replay("request_1")
    
    # Wait for expiry
    time.sleep(1.1)
    
    # Request should be considered new again
    assert not detector.detect_replay("request_1")

def test_replay_attack_detector_empty_request_id():
    """Test empty request ID raises an error."""
    detector = ReplayAttackDetector()
    
    with pytest.raises(ValueError, match="Request ID cannot be empty"):
        detector.detect_replay("")
    
    with pytest.raises(ValueError, match="Request ID cannot be empty"):
        detector.detect_replay(None)  # type: ignore

def test_replay_attack_detector_large_number_of_requests():
    """Test handling a large number of unique requests."""
    detector = ReplayAttackDetector(max_window_seconds=5)
    
    # Generate and test 1000 unique requests
    for i in range(1000):
        request_id = f"request_{i}"
        assert not detector.detect_replay(request_id)
        assert detector.detect_replay(request_id)  # Immediate replay check