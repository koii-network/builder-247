"""
Test suite for evidence uniqueness validation.
"""

import pytest
from unittest.mock import Mock, patch
from flask import Flask
from flask.testing import FlaskClient

from src.server.routes.evidence_uniqueness import register_evidence_uniqueness_routes

@pytest.fixture
def app():
    """
    Create a Flask test app with evidence uniqueness routes.
    """
    test_app = Flask(__name__)
    mock_database_service = Mock()
    register_evidence_uniqueness_routes(test_app, mock_database_service)
    return test_app

@pytest.fixture
def client(app):
    """
    Create a test client for the Flask app.
    """
    return app.test_client()

def test_evidence_uniqueness_route_requires_data(client: FlaskClient):
    """
    Test that the route requires evidence data.
    """
    response = client.post('/validate/evidence-uniqueness')
    assert response.status_code == 400
    assert 'No evidence data provided' in response.json['message']

def test_evidence_uniqueness_route_requires_unique_fields(client: FlaskClient):
    """
    Test that the route requires unique fields.
    """
    response = client.post('/validate/evidence-uniqueness', json={})
    assert response.status_code == 400
    assert 'No unique fields specified' in response.json['message']

def test_evidence_uniqueness_validation_unique_evidence(client: FlaskClient):
    """
    Test successful uniqueness validation.
    """
    # Use patch to mock the database service
    with patch('src.server.routes.evidence_uniqueness.EvidenceUniquenessValidationRoute._check_evidence_uniqueness') as mock_check:
        mock_check.return_value = {
            'is_unique': True,
            'duplicate_fields': {}
        }
        
        response = client.post('/validate/evidence-uniqueness', json={
            'unique_fields': {
                'id': 'unique_evidence_123',
                'hash': 'abc123'
            }
        })
        
        assert response.status_code == 200
        assert response.json['status'] == 'success'
        assert 'Evidence is unique' in response.json['message']

def test_evidence_uniqueness_validation_duplicate_evidence(client: FlaskClient):
    """
    Test uniqueness validation with duplicate evidence.
    """
    # Use patch to mock the database service
    with patch('src.server.routes.evidence_uniqueness.EvidenceUniquenessValidationRoute._check_evidence_uniqueness') as mock_check:
        mock_check.return_value = {
            'is_unique': False,
            'duplicate_fields': {
                'id': 'duplicate_evidence_123'
            }
        }
        
        response = client.post('/validate/evidence-uniqueness', json={
            'unique_fields': {
                'id': 'duplicate_evidence_123'
            }
        })
        
        assert response.status_code == 409
        assert response.json['status'] == 'error'
        assert 'Evidence is not unique' in response.json['message']
        assert 'duplicate_fields' in response.json

def test_evidence_uniqueness_validation_handles_exceptions(client: FlaskClient):
    """
    Test that the route handles exceptions gracefully.
    """
    # Use patch to make the database service raise an exception
    with patch('src.server.routes.evidence_uniqueness.EvidenceUniquenessValidationRoute._check_evidence_uniqueness') as mock_check:
        mock_check.side_effect = Exception("Database error")
        
        response = client.post('/validate/evidence-uniqueness', json={
            'unique_fields': {
                'id': 'test_evidence'
            }
        })
        
        assert response.status_code == 500
        assert response.json['status'] == 'error'
        assert 'Uniqueness validation failed' in response.json['message']