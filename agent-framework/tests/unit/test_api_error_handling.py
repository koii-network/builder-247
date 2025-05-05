import pytest
from unittest.mock import Mock, patch
from prometheus_swarm.clients.base_client import BaseClient
from prometheus_swarm.utils.errors import APIError, NetworkError, AuthenticationError

class TestAPIErrorHandling:
    """Test suite for API error handling scenarios."""

    def test_base_client_network_error(self):
        """Test handling of network-related errors in base client."""
        base_client = BaseClient()
        
        with pytest.raises(NetworkError, match="Unable to connect"):
            with patch('requests.request', side_effect=ConnectionError("Connection failed")):
                base_client._make_request('GET', 'http://example.com')

    def test_base_client_authentication_error(self):
        """Test handling of authentication errors."""
        base_client = BaseClient()
        
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Invalid credentials"}
        
        with pytest.raises(AuthenticationError, match="Authentication failed"):
            with patch('requests.request', return_value=mock_response):
                base_client._make_request('GET', 'http://example.com')

    def test_base_client_rate_limit_error(self):
        """Test handling of rate limiting errors."""
        base_client = BaseClient()
        
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        
        with pytest.raises(APIError, match="Rate limit exceeded"):
            with patch('requests.request', return_value=mock_response):
                base_client._make_request('GET', 'http://example.com')

    def test_base_client_server_error(self):
        """Test handling of server-side errors."""
        base_client = BaseClient()
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        with pytest.raises(APIError, match="Server error"):
            with patch('requests.request', return_value=mock_response):
                base_client._make_request('GET', 'http://example.com')

    def test_base_client_timeout_error(self):
        """Test handling of request timeout errors."""
        base_client = BaseClient()
        
        with pytest.raises(NetworkError, match="Request timed out"):
            with patch('requests.request', side_effect=TimeoutError("Request timed out")):
                base_client._make_request('GET', 'http://example.com')

    def test_base_client_malformed_response(self):
        """Test handling of malformed API responses."""
        base_client = BaseClient()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        
        with pytest.raises(APIError, match="Malformed response"):
            with patch('requests.request', return_value=mock_response):
                base_client._make_request('GET', 'http://example.com')