import time
import pytest
from src.server.middleware.replay_prevention import ReplayPreventionMiddleware, ReplayPreventionError

def test_replay_prevention_basic():
    """Test basic replay prevention functionality."""
    middleware = ReplayPreventionMiddleware(window_seconds=5)
    
    # First request should be allowed
    request_signature = "test-request-1"
    assert not middleware.is_replay_request(request_signature)
    
    # Same request within window should be considered a replay
    assert middleware.is_replay_request(request_signature)

def test_replay_prevention_window():
    """Test that requests are allowed after the time window."""
    middleware = ReplayPreventionMiddleware(window_seconds=1)
    
    request_signature = "timed-request"
    assert not middleware.is_replay_request(request_signature)
    
    # Wait for the window to expire
    time.sleep(1.1)
    
    # Now the request should be allowed again
    assert not middleware.is_replay_request(request_signature)

def test_replay_prevention_max_cache():
    """Test that the cache size is limited."""
    middleware = ReplayPreventionMiddleware(max_cache_size=3)
    
    # Add more requests than max cache size
    for i in range(5):
        request_signature = f"request-{i}"
        assert not middleware.is_replay_request(request_signature)
    
    # Check if only the last 3 requests are in the cache
    # (by attempting to replay the first two)
    assert not middleware.is_replay_request("request-0")
    assert not middleware.is_replay_request("request-1")

def test_replay_prevention_complex_signature():
    """Test replay prevention with complex request signatures."""
    middleware = ReplayPreventionMiddleware()
    
    # Simulate requests with different but similar signatures
    request1 = {"user_id": 123, "action": "create"}
    request2 = {"user_id": 123, "action": "create"}
    
    signature1 = f"{hash(frozenset(request1.items()))}"
    signature2 = f"{hash(frozenset(request2.items()))}"
    
    # Identical request data should be considered a replay
    assert not middleware.is_replay_request(signature1)
    assert middleware.is_replay_request(signature1)
    
    # Slight variation in timestamp prevents replay detection
    time.sleep(0.01)
    assert not middleware.is_replay_request(signature2)

def test_route_replay_prevention(client):
    """Test replay prevention on an actual route."""
    task_data = {"task_name": "test_task", "priority": "high"}
    
    # First request should succeed
    response1 = client.post('/submit_task', json=task_data)
    assert response1.status_code == 200
    
    # Immediate replay should be rejected
    response2 = client.post('/submit_task', json=task_data)
    assert response2.status_code == 400
    assert "Potential replay attack detected" in response2.get_json()['message']