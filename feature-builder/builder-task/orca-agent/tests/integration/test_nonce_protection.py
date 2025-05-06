import pytest
from flask import Flask
from src.server.routes.task import bp as task_bp
from src.server.routes.nonce import nonce_bp
from src.utils.nonce import nonce_manager

@pytest.fixture
def client():
    """Create a test client with task and nonce routes."""
    app = Flask(__name__)
    app.register_blueprint(task_bp)
    app.register_blueprint(nonce_bp)
    return app.test_client()

def test_worker_task_requires_nonce(client):
    """Test that worker task route requires a valid nonce."""
    # Attempt to call worker task without a nonce
    response = client.post('/worker-task/1', json={
        "taskId": "test-task",
        "roundNumber": 1,
        "stakingKey": "test-key",
        "stakingSignature": "test-sig",
        "pubKey": "test-pub-key",
        "publicSignature": "test-pub-sig",
        "addPRSignature": "test-pr-sig"
    })
    
    # Verify nonce protection
    assert response.status_code == 401
    assert "Nonce" in response.get_json().get("message", "")

def test_worker_task_with_valid_nonce(client):
    """Test worker task route with a valid nonce."""
    # Generate a valid nonce
    nonce = nonce_manager.generate_nonce()
    
    # Attempt to call worker task with a valid nonce
    response = client.post('/worker-task/1', json={
        "taskId": "test-task",
        "roundNumber": 1,
        "stakingKey": "test-key",
        "stakingSignature": "test-sig",
        "pubKey": "test-pub-key",
        "publicSignature": "test-pub-sig",
        "addPRSignature": "test-pr-sig"
    }, headers={'X-Nonce': nonce})
    
    # Verify response (note: this might fail due to other validation)
    # The key point is that it doesn't fail due to nonce
    assert response.status_code != 401

def test_nonce_reuse_prevention(client):
    """Test that a nonce cannot be reused."""
    # Generate and use a nonce
    nonce = nonce_manager.generate_nonce()
    
    # First request should succeed
    response1 = client.post('/worker-task/1', json={
        "taskId": "test-task-1",
        "roundNumber": 1,
        "stakingKey": "test-key",
        "stakingSignature": "test-sig",
        "pubKey": "test-pub-key",
        "publicSignature": "test-pub-sig",
        "addPRSignature": "test-pr-sig"
    }, headers={'X-Nonce': nonce})
    
    # Second request with same nonce should fail
    response2 = client.post('/worker-task/1', json={
        "taskId": "test-task-2",
        "roundNumber": 1,
        "stakingKey": "test-key",
        "stakingSignature": "test-sig",
        "pubKey": "test-pub-key",
        "publicSignature": "test-pub-sig",
        "addPRSignature": "test-pr-sig"
    }, headers={'X-Nonce': nonce})
    
    # First request passes, second fails
    assert response1.status_code != 401
    assert response2.status_code == 401
    assert "already been used" in response2.get_json().get("message", "")