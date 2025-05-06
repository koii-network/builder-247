import pytest
import time
from src.replay_attack_prevention import ReplayAttackPreventionLogger


def test_replay_attack_prevention_basic():
    """
    Test basic replay attack prevention functionality.
    """
    logger = ReplayAttackPreventionLogger(time_window=5)
    
    # First request should be allowed
    request1 = {"user_id": 123, "action": "login"}
    assert not logger.is_replay_attack(request1)
    
    # Same request within time window should be detected as a replay attack
    assert logger.is_replay_attack(request1)


def test_replay_attack_prevention_with_different_requests():
    """
    Test that different requests are not considered replay attacks.
    """
    logger = ReplayAttackPreventionLogger(time_window=5)
    
    request1 = {"user_id": 123, "action": "login"}
    request2 = {"user_id": 123, "action": "logout"}
    
    assert not logger.is_replay_attack(request1)
    assert not logger.is_replay_attack(request2)


def test_replay_attack_prevention_time_window():
    """
    Test that requests outside the time window are not considered replay attacks.
    """
    logger = ReplayAttackPreventionLogger(time_window=1)
    
    request = {"user_id": 123, "action": "login"}
    
    assert not logger.is_replay_attack(request)
    
    # Simulate time passing
    time.sleep(1.5)
    
    # Request should now be allowed
    assert not logger.is_replay_attack(request)


def test_replay_attack_prevention_max_history_size():
    """
    Test that the logger caps the number of stored requests.
    """
    logger = ReplayAttackPreventionLogger(
        time_window=10, 
        max_history_size=3
    )
    
    requests = [
        {"user_id": i, "action": "login"} 
        for i in range(5)
    ]
    
    # First three requests should be tracked
    for req in requests[:3]:
        assert not logger.is_replay_attack(req)
    
    # First request should now be pushed out of history
    assert not logger.is_replay_attack(requests[3])
    
    # First request should now be allowed again
    assert not logger.is_replay_attack(requests[0])


def test_replay_attack_prevention_edge_cases():
    """
    Test various edge cases for the replay attack prevention.
    """
    logger = ReplayAttackPreventionLogger()
    
    # Empty request
    empty_request = {}
    assert not logger.is_replay_attack(empty_request)
    assert logger.is_replay_attack(empty_request)
    
    # Request with complex data structure
    complex_request = {
        "user": {
            "id": 123,
            "roles": ["admin", "user"]
        },
        "action": "update"
    }
    assert not logger.is_replay_attack(complex_request)
    assert logger.is_replay_attack(complex_request)


def test_replay_attack_prevention_time_order():
    """
    Test replay attack prevention with requests coming at different times.
    """
    logger = ReplayAttackPreventionLogger(time_window=2)
    
    request = {"user_id": 123, "action": "login"}
    
    assert not logger.is_replay_attack(request)
    
    # Simulate a short time pass
    time.sleep(1)
    
    # Same request should be considered a replay attack
    assert logger.is_replay_attack(request)
    
    # Wait beyond time window
    time.sleep(2)
    
    # Request should now be allowed again
    assert not logger.is_replay_attack(request)