import pytest
from flask import Flask
from ..server.routes.nonce import nonce_bp
from ..utils.nonce import nonce_manager

@pytest.fixture
def client():
    """Create a test client for the nonce routes."""
    app = Flask(__name__)
    app.register_blueprint(nonce_bp)
    return app.test_client()

def test_get_nonce_route(client):
    """Test the nonce generation route."""
    response = client.get('/get_nonce')
    
    # Check response
    assert response.status_code == 200
    data = response.get_json()
    
    # Validate nonce
    assert 'nonce' in data
    assert len(data['nonce']) > 0
    
    # Validate the nonce works
    try:
        nonce_manager.validate_nonce(data['nonce'])
    except Exception as e:
        pytest.fail(f"Generated nonce failed validation: {e}")