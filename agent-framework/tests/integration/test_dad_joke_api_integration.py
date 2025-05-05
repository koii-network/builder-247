import pytest
import requests

class TestDadJokeAPIIntegration:
    """Integration tests for the Dad Joke API."""

    def test_dad_joke_api_connection(self):
        """Test basic connection to the icanhazdadjoke API."""
        url = "https://icanhazdadjoke.com/"
        headers = {
            "Accept": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers)
            assert response.status_code == 200, "Failed to connect to Dad Joke API"
            
            joke_data = response.json()
            assert "id" in joke_data, "Joke data does not contain an ID"
            assert "joke" in joke_data, "Joke data does not contain a joke text"
            assert isinstance(joke_data["joke"], str), "Joke text is not a string"
        except requests.RequestException as e:
            pytest.fail(f"Request to Dad Joke API failed: {e}")

    def test_dad_joke_api_random_joke(self):
        """Test retrieving a random dad joke."""
        url = "https://icanhazdadjoke.com/"
        headers = {
            "Accept": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers)
            assert response.status_code == 200, "Failed to retrieve random joke"
            
            joke_data = response.json()
            assert len(joke_data["joke"]) > 0, "Retrieved joke is empty"
            assert len(joke_data["joke"]) <= 300, "Joke text is suspiciously long"
        except requests.RequestException as e:
            pytest.fail(f"Request to Dad Joke API failed: {e}")

    def test_dad_joke_api_search(self):
        """Test searching for dad jokes by term."""
        url = "https://icanhazdadjoke.com/search"
        headers = {
            "Accept": "application/json"
        }
        params = {
            "term": "computer",
            "limit": 5
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            assert response.status_code == 200, "Failed to search for dad jokes"
            
            search_results = response.json()
            assert "results" in search_results, "Search results missing 'results' key"
            assert isinstance(search_results["results"], list), "Results should be a list"
            assert "total_jokes" in search_results, "Search results missing 'total_jokes' key"
        except requests.RequestException as e:
            pytest.fail(f"Request to Dad Joke API failed: {e}")