import pytest
import requests
from unittest.mock import Mock, patch
from src.dad_joke_client import DadJokeClient

@pytest.fixture
def mock_requests_get():
    """Fixture to mock requests.get method."""
    with patch('requests.get') as mock_get:
        yield mock_get

def test_dad_joke_client_initialization():
    """Test client initialization."""
    client = DadJokeClient()
    assert client.base_url == 'https://icanhazdadjoke.com/'
    assert client.headers['Accept'] == 'application/json'

def test_get_random_joke_success(mock_requests_get):
    """Test successful retrieval of a random joke."""
    mock_response = Mock()
    mock_response.json.return_value = {'joke': 'Why did the scarecrow win an award? Because he was outstanding in his field!'}
    mock_response.raise_for_status = Mock()
    mock_requests_get.return_value = mock_response

    client = DadJokeClient()
    joke = client.get_random_joke()

    assert joke == 'Why did the scarecrow win an award? Because he was outstanding in his field!'
    mock_requests_get.assert_called_once_with(client.base_url, headers=client.headers)

def test_get_random_joke_no_joke(mock_requests_get):
    """Test error handling when no joke is returned."""
    mock_response = Mock()
    mock_response.json.return_value = {}
    mock_response.raise_for_status = Mock()
    mock_requests_get.return_value = mock_response

    client = DadJokeClient()
    with pytest.raises(ValueError, match="No joke found in the API response"):
        client.get_random_joke()

def test_get_random_joke_request_error(mock_requests_get):
    """Test error handling for request exceptions."""
    mock_requests_get.side_effect = requests.RequestException("Network error")

    client = DadJokeClient()
    with pytest.raises(requests.RequestException, match="Error fetching dad joke: Network error"):
        client.get_random_joke()

def test_get_joke_by_id_success(mock_requests_get):
    """Test successful retrieval of a joke by ID."""
    joke_id = 'ABC123'
    mock_response = Mock()
    mock_response.json.return_value = {'joke': 'Testing is just the beginning!'}
    mock_response.raise_for_status = Mock()
    mock_requests_get.return_value = mock_response

    client = DadJokeClient()
    joke = client.get_joke_by_id(joke_id)

    assert joke == 'Testing is just the beginning!'
    mock_requests_get.assert_called_once_with(f'{client.base_url}j/{joke_id}', headers=client.headers)

def test_get_joke_by_id_empty_id():
    """Test error handling for empty joke ID."""
    client = DadJokeClient()
    with pytest.raises(ValueError, match="Joke ID cannot be empty"):
        client.get_joke_by_id('')

def test_get_joke_by_id_not_found(mock_requests_get):
    """Test error handling when joke is not found."""
    joke_id = 'NONEXISTENT'
    mock_response = Mock()
    mock_response.json.return_value = {}
    mock_response.raise_for_status = Mock()
    mock_requests_get.return_value = mock_response

    client = DadJokeClient()
    with pytest.raises(ValueError, match=f"No joke found with ID {joke_id}"):
        client.get_joke_by_id(joke_id)

def test_search_jokes_success(mock_requests_get):
    """Test successful joke search."""
    search_term = 'programming'
    mock_response = Mock()
    mock_response.json.return_value = {
        'results': [
            {'joke': 'Programmer joke 1'},
            {'joke': 'Programmer joke 2'}
        ]
    }
    mock_response.raise_for_status = Mock()
    mock_requests_get.return_value = mock_response

    client = DadJokeClient()
    jokes = client.search_jokes(search_term)

    assert jokes == ['Programmer joke 1', 'Programmer joke 2']
    mock_requests_get.assert_called_once_with(
        f'{client.base_url}search', 
        params={'term': search_term, 'limit': 30}, 
        headers=client.headers
    )

def test_search_jokes_empty_term():
    """Test error handling for empty search term."""
    client = DadJokeClient()
    with pytest.raises(ValueError, match="Search term cannot be empty"):
        client.search_jokes('')

def test_search_jokes_no_results(mock_requests_get):
    """Test error handling when no jokes match the search term."""
    search_term = 'nonexistent'
    mock_response = Mock()
    mock_response.json.return_value = {'results': []}
    mock_response.raise_for_status = Mock()
    mock_requests_get.return_value = mock_response

    client = DadJokeClient()
    with pytest.raises(ValueError, match=f"No jokes found matching the term '{search_term}'"):
        client.search_jokes(search_term)