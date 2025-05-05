import pytest
from prometheus_swarm.tools.execute_command.implementations import get_dad_joke

def test_get_dad_joke():
    """Test that dad joke retrieval works correctly."""
    result = get_dad_joke()
    
    # Check basic structure of the result
    assert isinstance(result, dict)
    assert "success" in result
    assert "message" in result
    assert "data" in result
    
    # Check successful dad joke fetch
    assert result["success"] is True
    assert result["message"] == "Dad joke fetched successfully"
    
    # Verify joke data
    assert "joke" in result["data"]
    assert "id" in result["data"]
    assert isinstance(result["data"]["joke"], str)
    assert len(result["data"]["joke"]) > 0

def test_dad_joke_complete_fetch():
    """Detailed test of dad joke fetch."""
    result = get_dad_joke()
    
    assert result["success"], f"Dad joke fetch failed: {result.get('message', 'Unknown error')}"
    joke_data = result["data"]
    
    # Basic joke validation
    assert joke_data is not None
    assert isinstance(joke_data["joke"], str)
    assert len(joke_data["joke"]) > 10  # Some minimum length to ensure it's a real joke
    assert joke_data["id"] is not None  # Each joke should have a unique ID