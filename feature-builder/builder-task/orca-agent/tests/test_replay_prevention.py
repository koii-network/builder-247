import pytest
import time
from flask import Flask
from src.server.utils.replay_prevention import generate_request_signature, prevent_replay
from src.utils.replay_utils import generate_replay_signature, add_replay_protection

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

def test_prevent_replay_basic():
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
    response1 = client.post('/test_replay', json=payload1)
    assert response1.status_code == 200
    
    # Immediate replay of same signature should be rejected
    response2 = client.post('/test_replay', json=payload1)
    assert response2.status_code == 403