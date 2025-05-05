import pytest
import requests
from prometheus_swarm.clients.dad_joke_client import DadJokeClient

class TestDadJokeClient:
    """
    Integration tests for the Dad Joke API Client.
    """
    
    @pytest.fixture
    def client(self):
        """
        Fixture to create a DadJokeClient instance for each test.
        """
        return DadJokeClient()

    def test_get_random_joke_success(self, client):
        """
        Test that a random joke can be successfully retrieved.
        """
        joke = client.get_random_joke()
        
        # Validate joke structure
        assert isinstance(joke, dict), "Joke should be a dictionary"
        assert "id" in joke, "Joke should have an ID"
        assert "joke" in joke, "Joke should have a joke text"
        assert isinstance(joke["joke"], str), "Joke text should be a string"
        assert len(joke["joke"]) > 0, "Joke text should not be empty"

    def test_search_jokes_success(self, client):
        """
        Test that jokes can be searched successfully.
        """
        search_term = "car"
        results = client.search_jokes(search_term)
        
        # Validate search results structure
        assert isinstance(results, dict), "Search results should be a dictionary"
        assert "results" in results, "Search results should have a 'results' key"
        assert isinstance(results["results"], list), "Results should be a list"
        
        # Optional: Validate that at least some results match the search term
        if results["results"]:
            assert any(search_term.lower() in joke["joke"].lower() 
                       for joke in results["results"]), "At least some jokes should match the search term"

    def test_search_jokes_no_results(self, client):
        """
        Test searching with a term that likely yields no results.
        """
        results = client.search_jokes("zzzzzzzz_unlikely_term")
        
        assert isinstance(results, dict), "Search results should be a dictionary"
        assert "results" in results, "Search results should have a 'results' key"
        assert isinstance(results["results"], list), "Results should be a list"
        assert len(results["results"]) == 0, "Search for unlikely term should return no results"

    def test_error_handling(self, client, monkeypatch):
        """
        Test error handling by mocking a request failure.
        """
        def mock_get(*args, **kwargs):
            raise requests.RequestException("Simulated network error")
        
        monkeypatch.setattr(requests, "get", mock_get)
        
        with pytest.raises(RuntimeError, match="Failed to fetch dad joke"):
            client.get_random_joke()
        
        with pytest.raises(RuntimeError, match="Failed to search dad jokes"):
            client.search_jokes("test")