import pytest
import time
from flask import Flask
from src.server.utils.replay_prevention import generate_request_signature, prevent_replay
from src.utils.replay_utils import generate_replay_signature, add_replay_protection
import logging

# Set up logging to test logging functionality
logger = logging.getLogger(__name__)

def test_generate_request_signature():
    # Test that signatures are unique and deterministic
    payload1 = {"taskId": "123", "name": "Test"}
    signature1 = generate_request_signature(payload1)
    
    # Same payload should generate same signature within a short time window
    signature2 = generate_request_signature(payload1)
    assert signature1 == signature2
    
    # Different payloads should generate different signatures
    payload2 = {"taskId": "456", "name": "Different"}
    signature3 = generate_request_signature(payload2)
    assert signature1 != signature3

def test_replay_signature_generation():
    payload = {"taskId": "test_task", "action": "submit"}
    
    # Test signature generation
    signature1 = generate_replay_signature(payload)
    assert isinstance(signature1, str)
    assert len(signature1) > 0
    
    # Slight time delay
    time.sleep(0.1)
    
    # Regenerating signature should create a new unique signature
    signature2 = generate_replay_signature(payload)
    assert signature1 != signature2

def test_replay_protection_utility():
    payload = {"taskId": "test_task", "action": "submit"}
    
    # Add replay protection
    protected_payload = add_replay_protection(payload)
    
    # Verify signature added
    assert 'replay_signature' in protected_payload
    assert protected_payload['replay_signature'] != ''
    
    # Ensure original payload is unmodified
    assert payload == {k: v for k, v in protected_payload.items() if k != 'replay_signature'}

def test_prevent_replay_basic(caplog):
    # Mock Flask app for testing
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    @app.route('/test_replay', methods=['POST'])
    @prevent_replay
    def test_route():
        return "Success", 200
    
    client = app.test_client()
    
    # First request should be allowed
    payload1 = {"replay_signature": generate_replay_signature({"action": "test1"})}
    
    # Capture logs
    with caplog.at_level(logging.INFO):
        response1 = client.post('/test_replay', json=payload1)
        assert response1.status_code == 200
        
        # Immediate replay of same signature should be rejected
        response2 = client.post('/test_replay', json=payload1)
        assert response2.status_code == 403
        
        # Check logging
        log_messages = [record.message for record in caplog.records]
        assert any("Potential replay attack" in msg for msg in log_messages)

def test_replay_signature_time_window():
    # Verify that signatures become valid again after the time window
    from src.server.utils.replay_prevention import REPLAY_WINDOW, _processed_requests
    
    # Clear existing processed requests
    _processed_requests.clear()
    
    # Create a signature
    payload = {"taskId": "time_window_test"}
    signature = generate_replay_signature(payload)
    
    # Simulate time passing beyond replay window
    def mock_time_passing():
        global _processed_requests
        current_time = time.time()
        # Modify timestamps to be outside replay window
        _processed_requests[signature] = current_time - REPLAY_WINDOW - 1
    
    mock_time_passing()
    
    # The signature should now be considered fresh
    app = Flask(__name__)
    
    @app.route('/time_window_test', methods=['POST'])
    @prevent_replay
    def test_route():
        return "Success", 200
    
    client = app.test_client()
    response = client.post('/time_window_test', json={"replay_signature": signature})
    assert response.status_code == 200