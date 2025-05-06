import time
import pytest
from prometheus_swarm.utils.replay_attack_detector import ReplayAttackDetector

def test_replay_attack_detector_basic_functionality():
    """
    Test basic replay attack detection with a unique nonce.
    """
    detector = ReplayAttackDetector()
    nonce = "unique_request_1"
    
    # First request with nonce should return False (not a replay)
    assert detector.detect_replay(nonce) is False
    
    # Second request with same nonce should return True (potential replay)
    assert detector.detect_replay(nonce) is True

def test_replay_attack_detector_time_window():
    """
    Test replay attack detection within and outside time window.
    """
    # Create a detector with a small time window for testing
    detector = ReplayAttackDetector(max_time_window=1)
    nonce = "timed_request"
    
    # First request
    assert detector.detect_replay(nonce) is False
    
    # Wait a bit
    time.sleep(0.5)
    
    # Request within time window should still be considered a replay
    assert detector.detect_replay(nonce) is True
    
    # Wait beyond time window
    time.sleep(1)
    
    # Now it should allow the nonce again (time window expired)
    assert detector.detect_replay(nonce) is False

def test_replay_attack_detector_custom_timestamp():
    """
    Test replay attack detection with custom timestamps.
    """
    detector = ReplayAttackDetector(max_time_window=5)
    nonce = "custom_timestamp_request"
    
    # Use a specific past timestamp
    past_timestamp = time.time() - 10
    
    # Request with an old timestamp should be considered a replay
    assert detector.detect_replay(nonce, timestamp=past_timestamp) is True
    
    # Future timestamp
    future_timestamp = time.time() + 10
    
    # Request with a future timestamp should also be considered a replay
    assert detector.detect_replay(nonce, timestamp=future_timestamp) is True

def test_replay_attack_detector_cache_size_limit():
    """
    Test that the detector limits its cache size.
    """
    # Create a detector with a very small max cache size
    detector = ReplayAttackDetector(max_nonce_cache_size=3)
    
    # Add more nonces than the cache limit
    nonces = [f"nonce_{i}" for i in range(5)]
    
    for nonce in nonces:
        assert detector.detect_replay(nonce) is False
    
    # Verify that the oldest nonces are removed when cache is full
    assert detector.detect_replay(nonces[0]) is True
    assert detector.detect_replay(nonces[1]) is True
    assert detector.detect_replay(nonces[2]) is True
    assert detector.detect_replay(nonces[3]) is False
    assert detector.detect_replay(nonces[4]) is False

def test_replay_attack_detector_input_validation():
    """
    Test input validation and edge cases.
    """
    detector = ReplayAttackDetector()
    
    # Test with empty nonce
    with pytest.raises(TypeError):
        detector.detect_replay(None)
    
    # Test with non-string nonce
    with pytest.raises(TypeError):
        detector.detect_replay(123)

def test_replay_attack_detector_multiple_requests():
    """
    Test handling multiple unique and repeated requests.
    """
    detector = ReplayAttackDetector()
    
    # Multiple unique requests
    unique_nonces = ["req1", "req2", "req3"]
    for nonce in unique_nonces:
        assert detector.detect_replay(nonce) is False
    
    # Repeat the requests and verify they are now considered replays
    for nonce in unique_nonces:
        assert detector.detect_replay(nonce) is True