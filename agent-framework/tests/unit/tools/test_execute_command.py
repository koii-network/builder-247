import pytest
import requests
import requests_mock
from prometheus_swarm.tools.execute_command.implementations import get_dad_joke


def test_get_dad_joke_success():
    """Test successful dad joke retrieval."""
    with requests_mock.Mocker() as m:
        mock_joke = "Why don't scientists trust atoms? Because they make up everything!"
        m.get("https://icanhazdadjoke.com/", json={"joke": mock_joke}, status_code=200)

        result = get_dad_joke()

        assert result["success"] is True
        assert result["message"] == "Dad joke retrieved successfully"
        assert result["data"]["joke"] == mock_joke


def test_get_dad_joke_api_error():
    """Test dad joke retrieval with API error."""
    with requests_mock.Mocker() as m:
        m.get("https://icanhazdadjoke.com/", status_code=500)

        result = get_dad_joke()

        assert result["success"] is False
        assert "Failed to retrieve dad joke" in result["message"]


def test_get_dad_joke_network_error():
    """Test dad joke retrieval with network error."""
    with requests_mock.Mocker() as m:
        m.get("https://icanhazdadjoke.com/", exc=requests.RequestException)

        result = get_dad_joke()

        assert result["success"] is False
        assert "Error fetching dad joke" in result["message"]