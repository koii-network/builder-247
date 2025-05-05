import pytest
import requests
from requests.exceptions import Timeout, ConnectionError, HTTPError

from prometheus_swarm.clients.http_client import HttpClient

class MockResponse:
    def __init__(self, json_data=None, text='', status_code=200, reason='OK'):
        self.json_data = json_data
        self.text = text
        self.status_code = status_code
        self.reason = reason

    def json(self):
        if self.json_data is None:
            raise ValueError("No JSON data")
        return self.json_data

    def raise_for_status(self):
        if 400 <= self.status_code < 600:
            raise HTTPError(f"HTTP Error {self.status_code}: {self.reason}", response=self)

def test_http_client_get_json(monkeypatch):
    def mock_request(*args, **kwargs):
        return MockResponse(json_data={'key': 'value'})

    monkeypatch.setattr(requests, 'request', mock_request)

    result = HttpClient.make_request('https://example.com')
    assert result == {'key': 'value'}

def test_http_client_get_text(monkeypatch):
    def mock_request(*args, **kwargs):
        return MockResponse(text='plain text response')

    monkeypatch.setattr(requests, 'request', mock_request)

    result = HttpClient.make_request('https://example.com')
    assert result == {'text': 'plain text response'}

def test_http_client_timeout(monkeypatch):
    def mock_request(*args, **kwargs):
        raise Timeout("Timeout error")

    monkeypatch.setattr(requests, 'request', mock_request)

    with pytest.raises(Timeout, match="timed out"):
        HttpClient.make_request('https://example.com')

def test_http_client_connection_error(monkeypatch):
    def mock_request(*args, **kwargs):
        raise ConnectionError("Connection failed")

    monkeypatch.setattr(requests, 'request', mock_request)

    with pytest.raises(ConnectionError, match="Could not connect"):
        HttpClient.make_request('https://example.com')

def test_http_client_http_error(monkeypatch):
    http_error = HTTPError(
        "HTTP Error 404: Not Found", 
        response=MockResponse(status_code=404, reason='Not Found')
    )

    def mock_request(*args, **kwargs):
        raise http_error

    monkeypatch.setattr(requests, 'request', mock_request)

    with pytest.raises(HTTPError, match="HTTP Error 404: Not Found"):
        HttpClient.make_request('https://example.com')

def test_http_client_invalid_method():
    with pytest.raises(ValueError, match="Unsupported HTTP method"):
        HttpClient.make_request('https://example.com', method='INVALID')

def test_http_client_post_json(monkeypatch):
    def mock_request(*args, **kwargs):
        assert kwargs['method'] == 'POST'
        assert kwargs['json'] == {'data': 'test'}
        return MockResponse(json_data={'result': 'success'})

    monkeypatch.setattr(requests, 'request', mock_request)

    result = HttpClient.make_request(
        'https://example.com', 
        method='POST', 
        json={'data': 'test'}
    )
    assert result == {'result': 'success'}

def test_http_client_custom_headers(monkeypatch):
    def mock_request(*args, **kwargs):
        assert kwargs['headers']['Custom-Header'] == 'value'
        return MockResponse(json_data={'key': 'value'})

    monkeypatch.setattr(requests, 'request', mock_request)

    result = HttpClient.make_request(
        'https://example.com', 
        headers={'Custom-Header': 'value'}
    )
    assert result == {'key': 'value'}